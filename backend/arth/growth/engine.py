"""Growth layer (T6.1–T6.12): diagnostics that sum exactly, levers resolved per pack, counter hints with a
holdout, outreach campaigns bounded by an approved plan, guardrail auto-stop, Growth Ledger, Impact Statement.

Every customer-facing action is a bus command (R3 for campaigns and plans); holdout members are assigned and
recorded before any send and are never messaged (RCH-1).
"""

import hashlib
import json
from datetime import date, timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.core.packs import PackRegistry
from arth.core.schemas import schema
from arth.domains.commerce_tables import bill_lines, bills, ratings
from arth.domains.ledger_projection import account_view
from arth.domains.ledger_tables import credit_accounts, ledger_payments
from arth.domains.merchants import domain_event, owner_only
from arth.domains.patron_identity import has_consent
from arth.domains.summaries import item_name, label
from arth.domains.tables import items
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import PolicyContext
from arth.governance.repository import Repository
from arth.governance.tables import merchants
from arth.growth.tables import campaign_assignments, campaigns, growth_plans, hints, preorders
from arth.intel.analytics import affinity, closed_bills, ist_date, lifecycle, purchase_cycles, today
from arth.intel.forecast import bootstrap_ci
from arth.intel.insight import sufficiency

LEVER_SEGMENTS = {"winback": "lapsing", "replenish": "due", "repeat_order": "regular", "welcome": "new"}
HINT_HOLDOUT_BP = 2000  # F4.1: 20% of eligible bills get no hint


def arm(key: str, holdout_bp: int) -> str:
    bucket = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % 10000
    return "holdout" if bucket < holdout_bp else "treated"


# ---- T6.1 diagnostics --------------------------------------------------------------------------------------
async def period(repo: Repository, start: date, end: date) -> dict[str, int]:
    rows = [b for b in await closed_bills(repo) if start <= ist_date(b["closed_at"]) <= end]
    return {
        "customers": len({b["patron_id"] or b["id"] for b in rows}),
        "visits": len(rows),
        "sales_paise": sum(b["total_paise"] for b in rows),
    }


async def diagnostics(repo: Repository, clock: SimClock, days: int = 14) -> dict[str, Any]:
    """Sales = customers × visits per customer × basket; the change splits into three exact parts."""
    end = today(clock)
    cur = await period(repo, end - timedelta(days=days - 1), end)
    prev = await period(repo, end - timedelta(days=2 * days - 1), end - timedelta(days=days))
    change = cur["sales_paise"] - prev["sales_paise"]

    def parts(c: dict[str, int]) -> tuple[float, float, float]:
        freq = c["visits"] / c["customers"] if c["customers"] else 0.0
        basket = c["sales_paise"] / c["visits"] if c["visits"] else 0.0
        return float(c["customers"]), freq, basket

    c0, f0, b0 = parts(prev)
    c1, f1, b1 = parts(cur)
    customers_part = round((c1 - c0) * f0 * b0)
    frequency_part = round(c1 * (f1 - f0) * b0)
    basket_part = change - customers_part - frequency_part  # sequential attribution; remainder keeps it exact
    return {
        "current": cur,
        "previous": prev,
        "change_paise": change,
        "parts": {
            "customers_paise": customers_part,
            "frequency_paise": frequency_part,
            "basket_paise": basket_part,
        },
    }


# ---- T6.2 levers per pack --------------------------------------------------------------------------------
async def audience(repo: Repository, clock: SimClock, lever: str) -> list[str]:
    if lever == "replenish":
        due = [
            c
            for c in await purchase_cycles(repo, clock)
            if c["next_due"] <= (today(clock) + timedelta(days=3)).isoformat()
        ]
        return sorted({c["patron_id"] for c in due})
    segment = LEVER_SEGMENTS.get(lever)
    if segment is None:
        return []
    return [r["patron_id"] for r in await lifecycle(repo, clock) if r["state"] == segment]


async def levers(repo: Repository, clock: SimClock, packs: PackRegistry) -> list[dict[str, Any]]:
    pack = packs.get((await repo.select(merchants))[0]["pack"])
    gates = {g["feature"]: g["status"] for g in await sufficiency(repo, clock)}
    gate_for = {
        "counter_hint": "counter_hints",
        "winback": "winback",
        "replenish": "replenish",
        "offers": "offers_targeting",
    }
    result = []
    for name in sorted(pack.levers):
        people = await audience(repo, clock, name)
        result.append(
            {
                "name": name,
                "enabled": True,
                "eligible": len(people),
                "estimate_paise": len(people) * 5000,
                "label": "estimate",
                "gate": gates.get(gate_for.get(name, ""), "ready"),
            }
        )
    return result


# ---- T6.3 counter hints ----------------------------------------------------------------------------------
async def hint_for(repo: Repository, clock: SimClock, bill_id: str) -> dict[str, Any] | None:
    """One quiet owner-only line: the patron's habit item not yet on the bill. Holdout bills get none."""
    bill = await repo.select(bills, bills.c.id == bill_id)
    if not bill or not bill[0]["patron_id"] or bill[0]["status"] != "open":
        return None
    patron = bill[0]["patron_id"]
    stored = await repo.select(hints, hints.c.bill_id == bill_id)
    if stored:
        row = stored[0]
    else:
        return None
    if row["arm"] == "holdout" or not row["item_id"]:
        return None
    on_bill = {
        line["item_id"]
        for line in await repo.select(
            bill_lines, bill_lines.c.bill_id == bill_id, bill_lines.c.status == "active"
        )
    }
    if row["item_id"] in on_bill:
        return None
    item = (await repo.select(items, items.c.id == row["item_id"]))[0]
    return {
        "hint_id": row["id"],
        "patron_id": patron,
        "item_id": row["item_id"],
        "name": label(item["names"]),
        "price_paise": item["price_paise"],
        "reason_key": row["reason_key"],
        "audience": "owner",
    }


async def choose_hint(repo: Repository, clock: SimClock, patron_id: str) -> tuple[str | None, str]:
    habits = [h for h in (await affinity(repo))["habits"] if h["patron_id"] == patron_id]
    if habits:
        return max(habits, key=lambda h: h["share_bp"])["item_id"], "hint.weekday_habit"
    due = [c for c in await purchase_cycles(repo, clock) if c["patron_id"] == patron_id]
    if due:
        return min(due, key=lambda c: c["next_due"])["item_id"], "hint.run_out_due"
    return None, "hint.none"


# ---- T6.7 credit advisor ----------------------------------------------------------------------------------
async def credit_advice(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    """GRW-10: raise only for steady payers; never with a dispute or a broken promise."""
    result = []
    for account in await repo.select(credit_accounts):
        view = await account_view(repo, account["id"], clock)
        paid = await repo.select(ledger_payments, ledger_payments.c.account_id == account["id"])
        blocked = any(e["status"] == "disputed" for e in view["entries"]) or any(
            p["status"] == "broken" for p in view["promises"]
        )
        if len(paid) >= 3 and not blocked and view["balance_paise"] < view["limit_paise"] // 2:
            result.append(
                {
                    "account_id": account["id"],
                    "patron_id": account["patron_id"],
                    "current_limit_paise": view["limit_paise"],
                    "suggested_limit_paise": view["limit_paise"] * 3 // 2,
                    "reason_key": "advisor.steady_payer",
                }
            )
    return result


# ---- T6.6 bundles ------------------------------------------------------------------------------------------
async def bundles(repo: Repository, margin_floor: float) -> list[dict[str, Any]]:
    """Greedy bundles from co-purchase pairs; 5% off, kept above the pack margin floor and only if stocked."""
    from arth.domains.stock import on_hand, stock_tracked

    catalog = {r["id"]: r for r in await repo.select(items)}
    result = []
    for pair in (await affinity(repo, min_support=2))["pairs"][:10]:
        chosen = [catalog[pair["a"]], catalog[pair["b"]]]
        price = sum(i["price_paise"] for i in chosen) * 95 // 100
        cost = sum(i["cost_paise"] for i in chosen)
        margin = (price - cost) * 10000 // max(price, 1)
        stocked = True
        for item in chosen:
            if await stock_tracked(repo, item["id"]) and await on_hand(repo, item["id"]) <= 0:
                stocked = False
        if margin >= margin_floor * 10000 and stocked:
            result.append(
                {
                    "items": [i["id"] for i in chosen],
                    "names": [label(i["names"]) for i in chosen],
                    "price_paise": price,
                    "margin_bp": margin,
                    "support": pair["support"],
                }
            )
    return result


# ---- T6.11 Growth Ledger ---------------------------------------------------------------------------------
async def outcomes(repo: Repository, campaign: dict[str, Any], window_days: int = 14) -> dict[str, Any]:
    rows = await repo.select(campaign_assignments, campaign_assignments.c.campaign_id == campaign["id"])
    start = campaign["created_at"]
    spend: dict[str, int] = {}
    for bill in await closed_bills(repo):
        if bill["patron_id"] and bill["closed_at"] >= start:
            spend[bill["patron_id"]] = spend.get(bill["patron_id"], 0) + bill["total_paise"]
    treated = [spend.get(r["patron_id"], 0) for r in rows if r["arm"] == "treated"]
    holdout = [spend.get(r["patron_id"], 0) for r in rows if r["arm"] == "holdout"]
    result = bootstrap_ci(treated, holdout)
    return {
        "treated_n": len(treated),
        "holdout_n": len(holdout),
        "measured": result,
        "direct_paise": sum(treated),
        "sent": len([r for r in rows if r["sent"]]),
    }


async def ledger(repo: Repository) -> dict[str, Any]:
    entries = []
    measured = direct = estimated = 0
    for campaign in await repo.select(campaigns):
        result = await outcomes(repo, campaign)
        label_kind = "measured" if result["measured"].get("measurable") else "direct"
        if label_kind == "measured":
            measured += int(result["measured"]["uplift"]) * result["treated_n"]
        direct += result["direct_paise"]
        entries.append(
            {
                "campaign_id": campaign["id"],
                "lever": campaign["lever"],
                "treated_n": result["treated_n"],
                "holdout_n": result["holdout_n"],
                "measured": result["measured"],
                "direct_paise": result["direct_paise"],
                "reward_cost_paise": 0,
                "label": label_kind,
            }
        )
    return {
        "entries": entries,
        "impact": {"measured_paise": measured, "direct_paise": direct, "estimated_paise": estimated},
    }


async def campaign_row(repo: Repository, campaign: dict[str, Any]) -> dict[str, Any]:
    result = await outcomes(repo, campaign)
    return {
        "id": campaign["id"],
        "plan_id": campaign["plan_id"],
        "lever": campaign["lever"],
        "status": campaign["status"],
        "stop_reason": campaign["stop_reason"],
        "treated": result["treated_n"],
        "holdout": result["holdout_n"],
        "sent": result["sent"],
        "result": result["measured"],
    }


# ---- commands --------------------------------------------------------------------------------------------
def register_growth(bus: CommandBus, packs: PackRegistry) -> None:
    clock = bus.clock

    async def plan_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        pack = packs.get((await repo.select(merchants))[0]["pack"])
        unknown = set(payload["levers"]) - set(pack.levers)
        if unknown:
            raise CommandError("growth.lever_not_in_pack")  # a disabled lever is never offered (T6.2)
        return PolicyContext(facts={"budget_paise": payload["budget_paise"]})

    async def create_plan(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        identity = new_id("plan")
        await repo.insert(
            growth_plans,
            {
                "id": identity,
                "goal_key": payload["goal_key"],
                "levers": json.dumps(payload["levers"]),
                "budget_paise": payload["budget_paise"],
                "holdout_bp": payload["holdout_bp"],
                "status": "active",
                "diagnosis": json.dumps(await diagnostics(repo, clock)),
                "created_at": iso_utc(clock.now()),
            },
        )
        await domain_event(bus, repo, "growth.updated", {"kind": "plan", "id": identity, "status": "active"})
        return {"plan_id": identity}

    async def campaign_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        plans = await repo.select(growth_plans, growth_plans.c.id == payload["plan_id"])
        if not plans or plans[0]["status"] != "active":
            raise CommandError("growth.plan_not_active")
        if payload["lever"] not in json.loads(plans[0]["levers"]):
            raise CommandError("growth.outside_plan_scope")  # plan scope bounds every campaign (T6.10)
        return PolicyContext(facts={"plan_id": payload["plan_id"]})

    async def send_campaign(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        await campaign_context(repo, payload)
        plan = (await repo.select(growth_plans, growth_plans.c.id == payload["plan_id"]))[0]
        identity = new_id("campaign")
        now = iso_utc(clock.now())
        await repo.insert(
            campaigns,
            {
                "id": identity,
                "plan_id": plan["id"],
                "lever": payload["lever"],
                "template": payload["template"],
                "status": "running",
                "created_at": now,
            },
        )
        from arth.domains.patrons import outbound_context

        sent = 0
        for patron_id in await audience(repo, clock, payload["lever"]):
            side = arm(identity + patron_id, plan["holdout_bp"])
            reason = None
            if side == "treated":
                context = await outbound_context(repo, clock, patron_id, "marketing")
                if not context.consent:
                    reason = "policy.consent"
                elif (
                    context.weekly_contacts >= bus.policy.policies.contact_caps.marketing_per_patron_per_week
                ):
                    reason = "policy.contact_cap"
            # assignment is stored before any send; holdout members are never messaged
            await repo.insert(
                campaign_assignments,
                {
                    "id": new_id("assign"),
                    "campaign_id": identity,
                    "patron_id": patron_id,
                    "arm": side,
                    "sent": int(side == "treated" and reason is None),
                    "reason": reason,
                    "created_at": now,
                },
            )
            if side == "treated" and reason is None:
                sent += 1
                await domain_event(
                    bus,
                    repo,
                    "growth.outreach_requested",
                    {"campaign_id": identity, "patron_id": patron_id, "template": payload["template"]},
                )
        await domain_event(
            bus, repo, "growth.updated", {"kind": "campaign", "id": identity, "status": "running"}
        )
        return {"campaign_id": identity, "sent": sent}

    async def stop(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if not await repo.update(
            campaigns,
            {"status": "stopped", "stop_reason": payload["reason_key"]},
            campaigns.c.id == payload["campaign_id"],
        ):
            raise CommandError("growth.campaign_not_found")
        await domain_event(
            bus,
            repo,
            "growth.updated",
            {"kind": "campaign", "id": payload["campaign_id"], "status": "stopped"},
        )
        return {"campaign_id": payload["campaign_id"], "status": "stopped"}

    async def accept_hint(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        rows = await repo.select(hints, hints.c.id == payload["hint_id"])
        if not rows or rows[0]["arm"] != "treated":
            raise CommandError("hints.not_found")
        await repo.update(hints, {"accepted": 1}, hints.c.id == payload["hint_id"])
        await domain_event(
            bus, repo, "growth.updated", {"kind": "hint", "id": payload["hint_id"], "status": "accepted"}
        )
        return {"hint_id": payload["hint_id"], "item_id": rows[0]["item_id"]}

    async def preorder(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        """GRW-9/STO-4: the deposit is an advance on the khata account (a liability until applied)."""
        owner_only(repo)
        from arth.domains.ledger_tables import advances

        account = await repo.select(credit_accounts, credit_accounts.c.id == payload["account_id"])
        if not account or account[0]["patron_id"] != payload["patron_id"]:
            raise CommandError("preorders.account_mismatch")
        total = 0
        for line in payload["items"]:
            item = await repo.select(items, items.c.id == line["item_id"])
            if not item:
                raise CommandError("catalog.item_not_found")
            total += item[0]["price_paise"] * line["qty_milli"] // 1000
        if payload["deposit_paise"] > total:
            raise CommandError("preorders.deposit_exceeds_total")
        identity, ref = new_id("preorder"), new_id("payment")
        await repo.insert(
            advances,
            {
                "id": new_id("advance"),
                "account_id": payload["account_id"],
                "amount_paise": payload["deposit_paise"],
                "source_ref": ref,
                "purpose_ref": identity,
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await repo.insert(
            preorders,
            {
                "id": identity,
                "patron_id": payload["patron_id"],
                "items": json.dumps(payload["items"]),
                "total_paise": total,
                "deposit_paise": payload["deposit_paise"],
                "advance_ref": ref,
                "status": "deposited",
                "created_at": iso_utc(clock.now()),
            },
        )
        await domain_event(bus, repo, "preorder.changed", {"preorder_id": identity, "status": "deposited"})
        await domain_event(bus, repo, "credit.changed", {"account_id": payload["account_id"]})
        return {"preorder_id": identity, "total_paise": total}

    bus.register("growth.create_plan", schema("growth_create_plan"), create_plan, plan_context)
    bus.register("outreach.send_campaign", schema("outreach_send_campaign"), send_campaign, campaign_context)
    bus.register("growth.stop_campaign", schema("growth_stop_campaign"), stop)
    bus.register("hints.accept", schema("hints_accept"), accept_hint)
    bus.register("preorders.create", schema("preorders_create"), preorder)


async def record_hint(repo: Repository, clock: SimClock, bill_id: str, patron_id: str) -> None:
    """Called when a patron is attached to an open bill: assign the arm before showing anything (F4.1)."""
    if await repo.select(hints, hints.c.bill_id == bill_id):
        return
    item, reason = await choose_hint(repo, clock, patron_id)
    await repo.insert(
        hints,
        {
            "id": new_id("hint"),
            "bill_id": bill_id,
            "patron_id": patron_id,
            "item_id": item,
            "arm": arm("hint" + bill_id, HINT_HOLDOUT_BP),
            "reason_key": reason,
            "created_at": iso_utc(clock.now()),
        },
    )


async def complaints_since(repo: Repository, since: str) -> int:
    return len(
        [
            r
            for r in await repo.select(ratings)
            if r["occurred_at"] >= since and (r["rating"] <= 2 or r["complaint_key"])
        ]
    )


__all__ = [
    "register_growth",
    "diagnostics",
    "levers",
    "hint_for",
    "record_hint",
    "bundles",
    "ledger",
    "credit_advice",
    "campaign_row",
    "complaints_since",
    "has_consent",
    "item_name",
]
