"""Offers engine: programs, holdouts, issuance on verified payments, coupons, redemption, expiry,
clawback and liability (OFR-1…11, PHAR-4).

Every reward row records its funding source. Liability lives on the shared `offer_liability` table
(issued − redeemed − expired). Budget checks run inside the single-writer bus transaction, so concurrent
payments can never overspend a program.
"""

import hashlib
import json
import secrets
from datetime import timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.catalog import get_item
from arth.domains.commerce_tables import (
    bill_lines,
    offer_assignments,
    offer_events,
    offer_issuances,
    offer_programs,
    payment_events,
    payment_matches,
    payments,
    refunds,
)
from arth.domains.merchants import domain_event, owner_only
from arth.domains.patron_tables import offer_liability, patron_identities
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import PolicyContext
from arth.governance.repository import Repository
from arth.governance.tables import merchants

REGULAR_VISITS = 4  # payments in the last 30 days that make a payer a "regular" (OFR-8)
VELOCITY_PER_DAY = 3  # issuances per payer per IST day across programs (OFR-10)
IST = timedelta(hours=5, minutes=30)


def _day(stamp: str) -> str:
    return (parse_iso(stamp) + IST).date().isoformat()


async def liability(repo: Repository, program_id: str | None = None) -> dict[str, int]:
    rows = await repo.select(
        offer_liability, *([offer_liability.c.program_id == program_id] if program_id else [])
    )
    issued = sum(r["issued_paise"] for r in rows)
    redeemed = sum(r["redeemed_paise"] for r in rows)
    expired = sum(r["expired_paise"] for r in rows)
    return {
        "issued_paise": issued,
        "redeemed_paise": redeemed,
        "expired_paise": expired,
        "outstanding_paise": issued - redeemed - expired,
    }


async def _book(
    repo: Repository, clock: SimClock, issuance: dict[str, Any], kind: str, amount: int, ref: str
) -> None:
    now = iso_utc(clock.now())
    if kind != "issued":
        await repo.insert(
            offer_events,
            {
                "id": new_id("oevt"),
                "issuance_id": issuance["id"],
                "kind": kind,
                "amount_paise": amount,
                "ref_id": ref,
                "occurred_at": now,
            },
        )
    await repo.insert(
        offer_liability,
        {
            "id": new_id("oliab"),
            "program_id": issuance["program_id"],
            "patron_id": issuance["patron_id"],
            "source_ref": issuance["id"] if kind == "issued" else ref,
            "date": _day(now),
            "issued_paise": amount if kind == "issued" else 0,
            "redeemed_paise": amount if kind == "redeemed" else 0,
            "expired_paise": amount if kind in {"expired", "clawed_back"} else 0,
        },
    )


async def issuance_state(repo: Repository, issuance_id: str) -> str:
    kinds = {r["kind"] for r in await repo.select(offer_events, offer_events.c.issuance_id == issuance_id)}
    for kind in ("clawed_back", "redeemed", "expired"):
        if kind in kinds:
            return kind
    return "open"


async def program_spent(repo: Repository, program: dict[str, Any], day: str | None = None) -> int:
    """Committed budget: issued minus expired/clawed-back (redeemed money is spent, so it stays counted)."""
    rows = await repo.select(offer_liability, offer_liability.c.program_id == program["id"])
    if day:
        rows = [r for r in rows if r["date"] == day]
    return sum(r["issued_paise"] - r["expired_paise"] for r in rows)


async def _arm(repo: Repository, clock: SimClock, program: dict[str, Any], payer_ref: str) -> str:
    if await repo.select(
        offer_assignments, offer_assignments.c.program_id == "*", offer_assignments.c.payer_ref == payer_ref
    ):
        return "excluded"
    rows = await repo.select(
        offer_assignments,
        offer_assignments.c.program_id == program["id"],
        offer_assignments.c.payer_ref == payer_ref,
    )
    if rows:
        return str(rows[0]["arm"])
    bucket = int(hashlib.sha256((program["id"] + "|" + payer_ref).encode()).hexdigest()[:8], 16) % 10000
    arm = "holdout" if bucket < program["holdout_bp"] else "treated"
    await repo.insert(
        offer_assignments,
        {
            "id": new_id("oassign"),
            "program_id": program["id"],
            "payer_ref": payer_ref,
            "arm": arm,
            "occurred_at": iso_utc(clock.now()),
        },
    )
    return arm


async def _received(repo: Repository, payer_ref: str) -> list[dict[str, Any]]:
    """Received, non-refunded payments from a payer (OFR-5 counting rule)."""
    result = []
    for row in await repo.select(payments, payments.c.payer_ref == payer_ref):
        statuses = await repo.select(payment_events, payment_events.c.payment_id == row["id"])
        latest = max(statuses, key=lambda r: r["seq"])["status"] if statuses else "success"
        refunded = await repo.select(refunds, refunds.c.payment_id == row["id"])
        if latest == "success" and not refunded:
            result.append(row)
    return result


async def _forbidden_bill(repo: Repository, payment_id: str, flags: list[str]) -> bool:
    """PHAR-4: no reward on a payment for a bill that contains a pack-forbidden item."""
    if not flags:
        return False
    match = await repo.select(
        payment_matches, payment_matches.c.payment_id == payment_id, payment_matches.c.target_kind == "bill"
    )
    if not match:
        return False
    for line in await repo.select(
        bill_lines, bill_lines.c.bill_id == match[0]["target_id"], bill_lines.c.status == "active"
    ):
        details = (await get_item(repo, line["item_id"]))["details"]
        if any(details.get(flag) for flag in flags):
            return True
    return False


async def _patron_for(repo: Repository, payer_ref: str) -> str | None:
    rows = await repo.select(
        patron_identities, patron_identities.c.kind == "vpa_hash", patron_identities.c.value == payer_ref
    )
    return rows[0]["patron_id"] if len({r["patron_id"] for r in rows}) == 1 else None


async def _issue(
    bus: CommandBus,
    repo: Repository,
    program: dict[str, Any],
    payment: dict[str, Any],
    kind: str,
    amount: int,
    min_spend: int,
    days: int,
    *,
    code: bool = False,
    item_id: str | None = None,
) -> dict[str, Any] | None:
    now = bus.clock.now()
    budget_ok = await program_spent(repo, program) + amount <= program["budget_paise"]
    daily = program["daily_budget_paise"]
    if not budget_ok or (
        daily is not None and await program_spent(repo, program, _day(iso_utc(now))) + amount > daily
    ):
        return None
    issuance = {
        "id": new_id("issue"),
        "program_id": program["id"],
        "kind": kind,
        "payer_ref": payment["payer_ref"],
        "patron_id": await _patron_for(repo, payment["payer_ref"]),
        "amount_paise": amount,
        "min_spend_paise": min_spend,
        "code": ("A" + secrets.token_hex(4).upper()) if code else None,
        "item_id": item_id,
        "source_ref": payment["id"],
        "funding": program["funding"],
        "expires_at": iso_utc(now + timedelta(days=days)),
        "occurred_at": iso_utc(now),
    }
    await repo.insert(offer_issuances, issuance)
    await _book(repo, bus.clock, issuance, "issued", amount, payment["id"])
    await domain_event(
        bus,
        repo,
        "offer.issued",
        {"issuance_id": issuance["id"], "program_id": program["id"], "kind": kind, "amount_paise": amount},
    )
    return issuance


async def _pay_cashback(bus: CommandBus, repo: Repository, issuance: dict[str, Any], payment_id: str) -> None:
    await _book(repo, bus.clock, issuance, "redeemed", issuance["amount_paise"], payment_id)
    await domain_event(
        bus,
        repo,
        "offer.cashback_requested",
        {
            "issuance_id": issuance["id"],
            "payment_id": payment_id,
            "amount_paise": issuance["amount_paise"],
            "funding": issuance["funding"],
        },
    )


async def on_payment(bus: CommandBus, repo: Repository, payment: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate every live program for one verified, received payment (transaction-local)."""
    payer = payment["payer_ref"]
    if not payer:
        return []
    now = iso_utc(bus.clock.now())
    shop = (await repo.select(merchants))[0]
    flags = list(bus.packs.policies_for(shop["pack"]).forbid_offers_on_flags) if bus.packs else []
    if await _forbidden_bill(repo, payment["id"], flags):
        return []
    history = await _received(repo, payer)
    earlier = [r for r in history if r["id"] != payment["id"]]
    month_start = now[:7]
    window_start = iso_utc(parse_iso(now) - timedelta(days=30))
    regular = len([r for r in earlier if r["received_at"] >= window_start]) >= REGULAR_VISITS
    today = _day(now)
    issued_today = [
        r
        for r in await repo.select(offer_issuances, offer_issuances.c.payer_ref == payer)
        if _day(r["occurred_at"]) == today
    ]
    result: list[dict[str, Any]] = []
    # OFR-2: pay any open next-transaction promise first, never twice.
    for promise in await repo.select(
        offer_issuances, offer_issuances.c.payer_ref == payer, offer_issuances.c.kind == "cashback_promise"
    ):
        if (
            promise["source_ref"] != payment["id"]
            and promise["expires_at"] > now
            and payment["amount_paise"] >= promise["min_spend_paise"]
            and await issuance_state(repo, promise["id"]) == "open"
        ):
            await _pay_cashback(bus, repo, promise, payment["id"])
            result.append(
                {
                    "issuance_id": promise["id"],
                    "kind": "cashback_paid",
                    "amount_paise": promise["amount_paise"],
                }
            )
    redeemed_now = bool(result)
    for program in sorted(
        await repo.select(offer_programs, offer_programs.c.status == "active"), key=lambda r: r["created_at"]
    ):
        if not program["valid_from"] <= now < program["valid_until"]:
            continue
        rules = json.loads(program["rules"])
        if regular and not program["include_regulars"] and program["type"] != "first_time_coupon":
            continue
        if await _arm(repo, bus.clock, program, payer) != "treated":
            continue
        mine_today = [r for r in issued_today if r["program_id"] == program["id"]]
        if mine_today or len(issued_today) >= VELOCITY_PER_DAY:
            continue
        issuance = None
        kind = program["type"]
        if kind == "next_txn_cashback":
            open_promise = [
                r
                for r in await repo.select(
                    offer_issuances,
                    offer_issuances.c.program_id == program["id"],
                    offer_issuances.c.payer_ref == payer,
                )
                if r["expires_at"] > now and await issuance_state(repo, r["id"]) == "open"
            ]
            if not open_promise and not redeemed_now and payment["amount_paise"] >= rules["min_spend_paise"]:
                issuance = await _issue(
                    bus,
                    repo,
                    program,
                    payment,
                    "cashback_promise",
                    rules["reward_paise"],
                    rules["min_spend_paise"],
                    rules["validity_days"],
                )
        elif kind == "instant_cashback":
            # OFR-3: payments from one payer inside the window are combined; one reward per window.
            since = iso_utc(parse_iso(now) - timedelta(minutes=rules.get("combine_minutes", 10)))
            combined = payment["amount_paise"] + sum(
                r["amount_paise"] for r in earlier if r["received_at"] >= since
            )
            recent = [
                r
                for r in await repo.select(
                    offer_issuances,
                    offer_issuances.c.program_id == program["id"],
                    offer_issuances.c.payer_ref == payer,
                )
                if r["occurred_at"] >= since
            ]
            if combined >= rules["min_spend_paise"] and not recent:
                issuance = await _issue(
                    bus,
                    repo,
                    program,
                    payment,
                    "instant_cashback",
                    rules["reward_paise"],
                    rules["min_spend_paise"],
                    0,
                )
                if issuance:
                    await _pay_cashback(bus, repo, issuance, payment["id"])
        elif kind == "first_time_coupon":
            # OFR-4: once per payer ever (any earlier payment or any earlier coupon disqualifies).
            ever = await repo.select(
                offer_issuances, offer_issuances.c.payer_ref == payer, offer_issuances.c.kind == "coupon"
            )
            if not earlier and not ever:
                issuance = await _issue(
                    bus,
                    repo,
                    program,
                    payment,
                    "coupon",
                    rules["reward_paise"],
                    rules["min_spend_paise"],
                    rules["validity_days"],
                    code=True,
                )
        elif kind == "payment_count":
            this_month = [r for r in history if r["received_at"][:7] == month_start]
            if len(this_month) == rules["count"] and not [
                r
                for r in await repo.select(
                    offer_issuances,
                    offer_issuances.c.program_id == program["id"],
                    offer_issuances.c.payer_ref == payer,
                )
                if r["occurred_at"][:7] == month_start
            ]:
                issuance = await _issue(
                    bus, repo, program, payment, "count_reward", rules["reward_paise"], 0, 0
                )
                if issuance:
                    await _pay_cashback(bus, repo, issuance, payment["id"])
        elif kind == "item_coupon" and payment["amount_paise"] >= rules["min_spend_paise"]:
            issuance = await _issue(
                bus,
                repo,
                program,
                payment,
                "coupon",
                rules["reward_paise"],
                rules["min_spend_paise"],
                rules["validity_days"],
                code=True,
                item_id=rules["item_id"],
            )
        if issuance:
            issued_today.append(issuance)
            result.append(
                {
                    "issuance_id": issuance["id"],
                    "kind": issuance["kind"],
                    "amount_paise": issuance["amount_paise"],
                    "code": issuance["code"],
                }
            )
    return result


async def redeem_coupon(bus: CommandBus, repo: Repository, code: str, bill_id: str) -> dict[str, Any]:
    """Counter hook: returns the `bill_payments` row for a valid coupon (merchant-funded discount)."""
    from arth.domains.counter import bill_state

    rows = await repo.select(offer_issuances, offer_issuances.c.code == code)
    if not rows:
        raise CommandError("offers.coupon_not_found")
    coupon = rows[0]
    state = await bill_state(repo, bill_id)
    now = iso_utc(bus.clock.now())
    if coupon["expires_at"] <= now or await issuance_state(repo, coupon["id"]) != "open":
        raise CommandError("offers.coupon_not_redeemable")
    if state["total_paise"] < coupon["min_spend_paise"] or coupon["amount_paise"] > state["total_paise"]:
        raise CommandError("offers.min_spend_not_met")
    if coupon["item_id"] and coupon["item_id"] not in {line["item_id"] for line in state["lines"]}:
        raise CommandError("offers.item_not_in_bill")
    await _book(repo, bus.clock, coupon, "redeemed", coupon["amount_paise"], bill_id)
    await domain_event(
        bus,
        repo,
        "offer.redeemed",
        {"issuance_id": coupon["id"], "bill_id": bill_id, "amount_paise": coupon["amount_paise"]},
    )
    return {"mode": "coupon", "amount_paise": coupon["amount_paise"], "ref_id": coupon["id"]}


async def claw_back(bus: CommandBus, repo: Repository, payment_id: str) -> list[str]:
    """OFR-10/PEX-5: a refund voids rewards issued on that payment; paid cashback is reversed."""
    clawed = []
    for issuance in await repo.select(offer_issuances, offer_issuances.c.source_ref == payment_id):
        state = await issuance_state(repo, issuance["id"])
        if state == "clawed_back" or state == "expired":
            continue
        if state == "open":
            await _book(repo, bus.clock, issuance, "clawed_back", issuance["amount_paise"], payment_id)
        else:
            await repo.insert(
                offer_events,
                {
                    "id": new_id("oevt"),
                    "issuance_id": issuance["id"],
                    "kind": "clawed_back",
                    "amount_paise": issuance["amount_paise"],
                    "ref_id": payment_id,
                    "occurred_at": iso_utc(bus.clock.now()),
                },
            )
        await domain_event(
            bus,
            repo,
            "offer.clawed_back",
            {
                "issuance_id": issuance["id"],
                "payment_id": payment_id,
                "amount_paise": issuance["amount_paise"],
            },
        )
        clawed.append(issuance["id"])
    return clawed


async def program_view(repo: Repository, program: dict[str, Any]) -> dict[str, Any]:
    arms = await repo.select(offer_assignments, offer_assignments.c.program_id == program["id"])
    issued = await repo.select(offer_issuances, offer_issuances.c.program_id == program["id"])
    return {
        "id": program["id"],
        "type": program["type"],
        "status": program["status"],
        "funding": program["funding"],
        "terms": json.loads(program["terms"]),
        "budget_paise": program["budget_paise"],
        "spent_paise": await program_spent(repo, program),
        "liability": await liability(repo, program["id"]),
        "treated": len([a for a in arms if a["arm"] == "treated"]),
        "holdout": len([a for a in arms if a["arm"] == "holdout"]),
        "issued": len(issued),
        "valid_until": program["valid_until"],
    }


def register_offers(bus: CommandBus) -> None:

    async def program_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        rules, terms = payload["rules"], payload["terms"]
        if (terms["amount_paise"], terms["min_spend_paise"], terms["expiry_days"]) != (
            rules["reward_paise"],
            rules.get("min_spend_paise", 0),
            rules.get("validity_days", 0),
        ):
            raise CommandError("offers.terms_mismatch")  # OFR-11: the stated terms are the rules
        if payload["type"] == "payment_count" and not rules.get("count"):
            raise CommandError("offers.count_required")
        shop = (await repo.select(merchants))[0]
        policies = bus.packs.policies_for(shop["pack"]) if bus.packs else bus.policy.policies
        if payload["holdout_bp"] < int(policies.growth.holdout_share * 10000):
            raise CommandError("offers.holdout_required")
        if payload["valid_until"] <= payload["valid_from"]:
            raise CommandError("offers.invalid_validity")
        if payload["type"] == "item_coupon":
            if not rules.get("item_id"):
                raise CommandError("offers.item_required")
            item = await get_item(repo, rules["item_id"])
            margin = (item["price_paise"] - item["cost_paise"] - rules["reward_paise"]) / max(
                item["price_paise"], 1
            )
            flags = tuple(flag for flag, value in item["details"].items() if value is True)
            return PolicyContext(margin=margin, flags=flags, facts={"budget_paise": payload["budget_paise"]})
        return PolicyContext(facts={"budget_paise": payload["budget_paise"]})

    async def create(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        identity = new_id("program")
        await repo.insert(
            offer_programs,
            {
                "id": identity,
                "type": payload["type"],
                "status": "active",
                "rules": json.dumps(payload["rules"]),
                "terms": json.dumps(payload["terms"]),
                "budget_paise": payload["budget_paise"],
                "daily_budget_paise": payload.get("daily_budget_paise"),
                "funding": payload["funding"],
                "holdout_bp": payload["holdout_bp"],
                "include_regulars": int(payload.get("include_regulars", False)),
                "valid_from": payload["valid_from"],
                "valid_until": payload["valid_until"],
                "created_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(bus, repo, "offer.program_changed", {"program_id": identity, "status": "active"})
        return {"program_id": identity}

    async def pause(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if not await repo.update(
            offer_programs, {"status": "paused"}, offer_programs.c.id == payload["program_id"]
        ):
            raise CommandError("offers.program_not_found")
        await domain_event(
            bus, repo, "offer.program_changed", {"program_id": payload["program_id"], "status": "paused"}
        )
        return {"program_id": payload["program_id"], "status": "paused"}

    async def exclude(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        for payer in payload["payer_refs"]:
            if not await repo.select(
                offer_assignments,
                offer_assignments.c.program_id == "*",
                offer_assignments.c.payer_ref == payer,
            ):
                await repo.insert(
                    offer_assignments,
                    {
                        "id": new_id("oassign"),
                        "program_id": "*",
                        "payer_ref": payer,
                        "arm": "excluded",
                        "occurred_at": iso_utc(bus.clock.now()),
                    },
                )
        return {"excluded": len(payload["payer_refs"])}

    async def expire_due(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        now = iso_utc(bus.clock.now())
        expired = []
        for issuance in await repo.select(offer_issuances, offer_issuances.c.expires_at <= now):
            if await issuance_state(repo, issuance["id"]) == "open":
                await _book(repo, bus.clock, issuance, "expired", issuance["amount_paise"], "expiry")
                expired.append(issuance["id"])
        if expired:
            await domain_event(bus, repo, "offer.expired", {"issuance_ids": expired})
        return {"expired": expired}

    bus.register("offers.create_program", schema("offers_create_program"), create, program_context)
    bus.register("offers.pause_program", schema("offers_pause_program"), pause)
    bus.register("offers.exclude_payers", schema("offers_exclude_payers"), exclude)
    bus.register("offers.expire_due", schema("offers_expire_due"), expire_due)


__all__ = ["on_payment", "redeem_coupon", "claw_back", "liability", "program_view", "register_offers"]
