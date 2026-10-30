"""Read models for every Part J9 screen not served elsewhere (T1.23). Writes go through the bus only.

Screens whose data comes from later layers (forecasts, Ask, growth, team, memory) return a schema-valid
data-sufficiency read model naming the layer that fills them, so every surface can render its empty state.
"""

import json
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Query, Request

from arth.api.commerce import Actor
from arth.api.problems import ProblemError
from arth.core.clock import iso_utc, parse_iso
from arth.core.config import provider_status
from arth.domains.capital import capital_view
from arth.domains.commerce_tables import (
    bills,
    offer_issuances,
    offer_programs,
    rx_records,
    tickets,
)
from arth.domains.counter import bill_state
from arth.domains.ledger import khata_view
from arth.domains.merchants import settings_view
from arth.domains.offers import issuance_state, liability, program_view
from arth.domains.orders import appointments_view, order_detail, orders_list
from arth.domains.patron_tables import patrons
from arth.domains.sentinel import verdict_view
from arth.domains.stock_tables import batches, stock_moves, unmet_demand
from arth.domains.supply import claim_view, grn_view, po_view, suppliers_view
from arth.domains.tables import items, shifts
from arth.domains.tax import gst_summary, invoice_view, profit_and_loss
from arth.domains.treasury import day_summary, settlement_rows, unmatched
from arth.domains.trust import feedback_view, latest_health, patron_export, public_storefront, storefront_view
from arth.governance.audit import verify_audit
from arth.governance.commands import CommandError
from arth.governance.repository import Repository
from arth.governance.tables import approvals, audit_log, commands, staff

router = APIRouter()
IST = timedelta(hours=5, minutes=30)
UNDOABLE = {"counter.add_lines", "counter.set_qty", "counter.remove_line"}
UNDO_SECONDS = 30
BILL = {"bill.changed", "bill.paid", "bill.price_override", "bill.returned", "bill.ticket_changed"}
PAY = {"payment.received", "payment.pending", "payment.failed", "payment.matched", "payment.refunded"}
OFFER = {"offer.program_changed", "offer.issued", "offer.redeemed", "offer.expired", "offer.clawed_back"}
PO = {"po.changed", "po.variance_found", "po.supplier_added", "credit.payable_changed"}
# Dispatcher declarations: which views go stale on which topics (view.invalidate derivation, J9).
VIEW_TOPICS: dict[str, set[str]] = {
    "home": BILL | PAY | {"approval.requested", "approval.decided", "credit.changed", "clock.hour"},
    "notifications": {"approval.requested", "approval.decided", "command.executed"},
    "bill": BILL | {"hint.offered"},
    "bill/pay": BILL | PAY | OFFER,
    "bill/paid": BILL | PAY | OFFER | {"tax.invoice_issued"},
    "park": BILL,
    "orders": {"order.changed"},
    "stock/expiry": {"stock.changed", "batch.recalled", "clock.day"},
    "suppliers": PO,
    "po": PO,
    "grn": PO | {"stock.changed"},
    "claims": PO,
    "grow/demand": {"stock.demand_logged"},
    "offers": OFFER,
    "storefront": {"storefront.published", "catalog.item_added", "catalog.price_changed"},
    "hisaab": PAY
    | {
        "payment.exception.opened",
        "payment.exception.resolved",
        "payment.expense_recorded",
        "payment.daily_closed",
        "settlement.recorded",
        "staff.shift_opened",
        "staff.shift_closed",
    },
    "reports": {"books.month_closed", "tax.invoice_issued"},
    "feedback": {"feedback.recorded"},
    "health": {"device.health_reported"},
    "capital": {"capital.offer_received", "capital.applied", "po.changed", "payment.received"},
    "kot": {"bill.ticket_changed", "bill.changed"},
    "appointments": {"order.appointment_changed", "bill.changed"},
    "rx": {"bill.paid", "batch.recalled"},
    "verdict": {"sentinel.verdict", "payment.received"},
    "calendar": {"calendar.local_event_added", "clock.day"},
    "trust": {"command.executed", "approval.decided", "privacy.erased", "privacy.sharing_changed"},
}
PENDING = {
    "ask": ("L4", "sufficiency.ask_pending"),
    "forecast": ("L3", "sufficiency.forecast_pending"),
    "grow": ("L6", "sufficiency.growth_pending"),
    "grow/plans": ("L6", "sufficiency.plan_pending"),
    "grow/bundles": ("L6", "sufficiency.bundles_pending"),
    "grow/ledger": ("L6", "sufficiency.ledger_pending"),
    "campaigns": ("L6", "sufficiency.campaign_pending"),
    "team": ("L5", "sufficiency.team_pending"),
    "runs": ("L5", "sufficiency.run_pending"),
    "memory": ("L5", "sufficiency.memory_pending"),
}


async def read(
    request: Request, session: Any, build: Callable[[Repository], Awaitable[dict[str, Any]]]
) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await build(Repository(conn, session.merchant_id))


def pending(screen: str, invalidate_on: list[str]) -> dict[str, Any]:
    layer, reason = PENDING[screen]
    return {
        "screen": screen,
        "status": "not_built_yet",
        "layer": layer,
        "reason_key": reason,
        "items": [],
        "invalidate_on": invalidate_on,
    }


def _gate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate_id": row["id"],
        "thread_id": row["thread_id"],
        "tier": row["tier"],
        "type": json.loads(row["scope"])["type"],
        "status": row["status"],
        "expires_at": row["expires_at"],
    }


async def open_gates(repo: Repository, now: str, status: str = "pending") -> list[dict[str, Any]]:
    rows = await repo.select(approvals, approvals.c.status == status, approvals.c.expires_at > now)
    return [_gate(r) for r in sorted(rows, key=lambda r: r["expires_at"])]


@router.get("/v1/views/home")
async def home(request: Request, session: Actor) -> dict[str, Any]:
    clock = request.app.state.clock

    async def build(repo: Repository) -> dict[str, Any]:
        settings = await settings_view(repo)
        today = (clock.now() + IST).date().isoformat()
        owner = await repo.select(staff, staff.c.role == "owner")
        closed = [
            b
            for b in await repo.select(bills, bills.c.status == "closed")
            if (parse_iso(b["closed_at"]) + IST).date().isoformat() == today
        ]
        new = [
            p
            for p in await repo.select(patrons, patrons.c.erased == 0)
            if (parse_iso(p["created_at"]) + IST).date().isoformat() == today
        ]
        summary = await day_summary(repo, clock, today)
        khata = await khata_view(repo, clock)
        first = min([b["opened_at"] for b in await repo.select(bills)] or [iso_utc(clock.now())])
        days = (clock.now() - parse_iso(first)).days
        hour = (clock.now() + IST).hour
        return {
            "greeting": {
                "owner_name": owner[0]["name"] if owner else "",
                "shop_name": settings["name"],
                "now": iso_utc(clock.now()),
                "part_of_day": "morning"
                if hour < 12
                else "midday"
                if hour < 17
                else "evening"
                if hour < 22
                else "night",
            },
            "today": {
                "sales_paise": summary["sales_paise"] + summary["khata_given_paise"],
                "bills": len(closed),
                "customers": len({b["patron_id"] for b in closed if b["patron_id"]}),
                "new_customers": len(new),
                "by_mode": summary["by_mode"],
            },
            "khata": {
                "outstanding_paise": khata["balance_paise"],
                "change_today_paise": summary["khata_given_paise"],
            },
            "gates": await open_gates(repo, iso_utc(clock.now())),
            "brief": None,
            "data_sufficiency": {
                "status": "cold_start" if days < 14 else "learning" if days < 56 else "ready",
                "days_of_history": days,
                "reason_key": "sufficiency.history_days",
            },
            "invalidate_on": [
                "bill.paid",
                "bill.changed",
                "payment.received",
                "approval.requested",
                "approval.decided",
                "credit.changed",
                "clock.hour",
            ],
        }

    return await read(request, session, build)


@router.get("/v1/views/ask")
async def ask(
    request: Request, session: Actor, session_id: Annotated[str | None, Query(alias="session")] = None
) -> dict[str, Any]:
    return pending("ask", ["turn.completed"])


@router.get("/v1/views/forecast")
async def forecast(request: Request, session: Actor, metric: str = "sales") -> dict[str, Any]:
    if metric not in {"sales", "items"}:
        raise ProblemError(422, "view.invalid_metric", "error.view.invalid_metric", title="Invalid metric")
    return pending("forecast", ["forecast.updated"])


@router.get("/v1/views/notifications")
async def notifications(request: Request, session: Actor) -> dict[str, Any]:
    clock = request.app.state.clock

    async def build(repo: Repository) -> dict[str, Any]:
        now = iso_utc(clock.now())
        done = [
            {k: r[k] for k in ("command_id", "type", "tier", "occurred_at", "undo_until")}
            for r in await recent_commands(repo, now, 20)
        ]
        return {
            "needs_you": await open_gates(repo, now),
            "done": done,
            "snoozed": await open_gates(repo, now, "snoozed"),
            "invalidate_on": ["approval.requested", "approval.decided", "command.executed"],
        }

    return await read(request, session, build)


async def recent_commands(repo: Repository, now: str, limit: int) -> list[dict[str, Any]]:
    result = []
    for row in sorted(
        await repo.select(audit_log, audit_log.c.action == "command.executed"), key=lambda r: -r["seq"]
    ):
        data = json.loads(row["data"])
        kind = await command_type(repo, row["command_id"])
        until = iso_utc(parse_iso(row["occurred_at"]) + timedelta(seconds=UNDO_SECONDS))
        result.append(
            {
                "command_id": row["command_id"],
                "type": kind,
                "tier": data["result"]["tier"],
                "occurred_at": row["occurred_at"],
                "undo_until": until if kind in UNDOABLE and until > now else None,
                "actor_id": data["session"]["actor_id"],
                "status": data["result"]["status"],
            }
        )
        if len(result) >= limit:
            break
    return result


async def command_type(repo: Repository, command_id: str) -> str:
    rows = await repo.select(commands, commands.c.id == command_id)
    return str(rows[0]["type"]) if rows else "unknown"


@router.get("/v1/views/gates/{gate_id}")
async def gate(request: Request, gate_id: str, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        rows = await repo.select(approvals, approvals.c.id == gate_id)
        if not rows:
            raise CommandError("approval.not_found")
        scope = json.loads(rows[0]["scope"])
        return {
            "gate": {
                **_gate(rows[0]),
                "scope": {"type": scope["type"], "payload": scope["payload"]},
                "conditions": json.loads(rows[0]["conditions"]),
            },
            "readback_key": "gate.readback_r2" if rows[0]["tier"] == "R2" else None,
            "invalidate_on": ["approval.decided", "approval.requested", "message.in"],
        }

    return await read(request, session, build)


@router.get("/v1/views/bill/{bill_id}")
async def bill(request: Request, bill_id: str, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        return {
            "bill": await bill_state(repo, bill_id),
            "parked_count": len(await repo.select(bills, bills.c.status == "parked")),
            "invalidate_on": ["bill.changed", "bill.paid", "hint.offered"],
        }

    return await read(request, session, build)


@router.get("/v1/views/bill/{bill_id}/pay")
async def bill_pay(request: Request, bill_id: str, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        state = await bill_state(repo, bill_id)
        failed = state["upi"] is not None and state["upi"]["status"] in {"failed", "expired"}
        return {
            "bill": state,
            "payee_vpa": (await settings_view(repo)).get("vpa"),
            "alternatives": ["cash", "khata", "regenerate"] if failed else ["cash", "khata"],
            "exception": ("payment." + state["upi"]["status"])
            if state["upi"] and state["upi"]["status"] in {"pending", "failed"}
            else None,
            "invalidate_on": [
                "payment.received",
                "payment.pending",
                "payment.failed",
                "bill.changed",
                "offer.issued",
            ],
        }

    return await read(request, session, build)


@router.get("/v1/views/bill/{bill_id}/paid")
async def bill_paid(request: Request, bill_id: str, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        from arth.domains.commerce_tables import payments
        from arth.domains.patron_identity import has_consent

        state = await bill_state(repo, bill_id)
        if state["status"] != "closed":
            raise CommandError("counter.bill_not_closed")
        receipt: dict[str, Any] = {"status": "walk_in", "lang": None}
        if state["patron_id"]:
            row = (await repo.select(patrons, patrons.c.id == state["patron_id"]))[0]
            receipt = {
                "status": "queued" if await has_consent(repo, row["id"], "receipts") else "no_consent",
                "lang": row["lang"],
            }
        refs = [p["ref_id"] for p in state["payments"] if p["mode"] == "upi" and p["ref_id"]]
        utr = None
        if refs:
            paid = await repo.select(payments, payments.c.id == refs[-1])
            utr = paid[0]["utr"][-4:] if paid and paid[0]["utr"] else None
        offers = []
        for ref in refs:
            for issued in await repo.select(offer_issuances, offer_issuances.c.source_ref == ref):
                offers.append(
                    {k: issued[k] for k in ("kind", "amount_paise", "min_spend_paise", "expires_at", "code")}
                    | {"issuance_id": issued["id"]}
                )
        return {
            "bill": state,
            "invoice": await invoice_view(repo, bill_id),
            "receipt": receipt,
            "offers": offers,
            "utr_tail": utr,
            "invalidate_on": ["bill.changed", "payment.received", "offer.issued"],
        }

    return await read(request, session, build)


@router.get("/v1/views/park")
async def park(request: Request, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        rows = []
        for row in sorted(await repo.select(bills, bills.c.status == "parked"), key=lambda r: r["opened_at"]):
            state = await bill_state(repo, row["id"])
            rows.append(
                {
                    "id": row["id"],
                    "patron_id": row["patron_id"],
                    "total_paise": state["total_paise"],
                    "lines": len(state["lines"]),
                    "opened_at": row["opened_at"],
                }
            )
        return {"bills": rows, "invalidate_on": ["bill.changed"]}

    return await read(request, session, build)


@router.get("/v1/views/orders")
async def orders(request: Request, session: Actor) -> dict[str, Any]:
    return await read(request, session, orders_list)


@router.get("/v1/views/orders/{order_id}")
async def order(request: Request, order_id: str, session: Actor) -> dict[str, Any]:
    return await read(request, session, lambda repo: order_detail(repo, order_id))


@router.get("/v1/views/stock/expiry")
async def stock_expiry(request: Request, session: Actor) -> dict[str, Any]:
    from arth.api.commerce_core import expiry

    return await expiry(request, session)


@router.get("/v1/views/suppliers")
async def suppliers(request: Request, session: Actor) -> dict[str, Any]:
    return await read(request, session, suppliers_view)


@router.get("/v1/views/po/{po_id}")
async def po(request: Request, po_id: str, session: Actor) -> dict[str, Any]:
    return await read(request, session, lambda repo: po_view(repo, po_id))


@router.get("/v1/views/grn/{po_id}")
async def grn(request: Request, po_id: str, session: Actor) -> dict[str, Any]:
    return await read(request, session, lambda repo: grn_view(repo, po_id))


@router.get("/v1/views/claims/{claim_id}")
async def claim(request: Request, claim_id: str, session: Actor) -> dict[str, Any]:
    return await read(request, session, lambda repo: claim_view(repo, claim_id))


@router.get("/v1/views/grow")
async def grow(request: Request, session: Actor) -> dict[str, Any]:
    return pending("grow", ["growth.updated", "demand.logged", "preorder.changed"])


@router.get("/v1/views/grow/plans/{plan_id}")
async def grow_plan(request: Request, plan_id: str, session: Actor) -> dict[str, Any]:
    return pending("grow/plans", ["growth.updated"])


@router.get("/v1/views/grow/demand")
async def grow_demand(request: Request, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        rows = sorted(await repo.select(unmet_demand), key=lambda r: r["occurred_at"], reverse=True)
        return {
            "unmet": [{k: r[k] for k in ("id", "text", "item_id", "occurred_at")} for r in rows],
            "clusters": [],
            "status": "needs_more_data",
            "invalidate_on": ["stock.demand_logged", "growth.updated"],
        }

    return await read(request, session, build)


@router.get("/v1/views/grow/bundles")
async def grow_bundles(request: Request, session: Actor) -> dict[str, Any]:
    return pending("grow/bundles", ["growth.updated", "preorder.changed"])


@router.get("/v1/views/grow/ledger")
async def grow_ledger(request: Request, session: Actor) -> dict[str, Any]:
    return pending("grow/ledger", ["growth.updated"])


@router.get("/v1/views/campaigns/{campaign_id}")
async def campaign(request: Request, campaign_id: str, session: Actor) -> dict[str, Any]:
    return pending("campaigns", ["growth.updated"])


@router.get("/v1/views/offers")
async def offers(request: Request, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        rows = sorted(await repo.select(offer_programs), key=lambda r: r["created_at"], reverse=True)
        return {
            "programs": [await program_view(repo, r) for r in rows],
            "liability": await liability(repo),
            "invalidate_on": [
                "offer.program_changed",
                "offer.issued",
                "offer.redeemed",
                "offer.expired",
                "offer.clawed_back",
            ],
        }

    return await read(request, session, build)


@router.get("/v1/views/offers/{program_id}")
async def offer(request: Request, program_id: str, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        rows = await repo.select(offer_programs, offer_programs.c.id == program_id)
        if not rows:
            raise CommandError("offers.program_not_found")
        issued = await repo.select(offer_issuances, offer_issuances.c.program_id == program_id)
        return {
            "program": await program_view(repo, rows[0]),
            "issuances": [
                {k: r[k] for k in ("id", "kind", "amount_paise", "funding", "expires_at", "patron_id")}
                | {"state": await issuance_state(repo, r["id"])}
                for r in sorted(issued, key=lambda r: r["seq"])
            ],
            "invalidate_on": ["offer.program_changed", "offer.issued", "offer.redeemed", "offer.expired"],
        }

    return await read(request, session, build)


@router.get("/v1/views/storefront")
async def storefront(request: Request, session: Actor) -> dict[str, Any]:
    return await read(request, session, storefront_view)


@router.get("/v1/views/team")
async def team(request: Request, session: Actor) -> dict[str, Any]:
    return pending("team", ["playbook.updated", "approval.requested", "approval.decided"])


@router.get("/v1/views/runs/{run_id}")
async def run(request: Request, run_id: str, session: Actor) -> dict[str, Any]:
    return pending("runs", ["playbook.updated"])


@router.get("/v1/views/memory")
async def memory(request: Request, session: Actor) -> dict[str, Any]:
    return pending("memory", ["memory.updated"])


@router.get("/v1/views/hisaab")
async def hisaab(request: Request, session: Actor) -> dict[str, Any]:
    clock = request.app.state.clock

    async def build(repo: Repository) -> dict[str, Any]:
        from arth.domains.commerce_tables import daily_closes, expenses, payment_exceptions

        today = (clock.now() + IST).date().isoformat()
        closes = sorted(await repo.select(daily_closes), key=lambda r: r["date"])
        shift_keys = (
            "id",
            "staff_id",
            "opened_at",
            "closed_at",
            "float_paise",
            "expected_paise",
            "counted_paise",
            "variance_paise",
        )
        return {
            "date": today,
            "close": {"date": closes[-1]["date"], **json.loads(closes[-1]["summary"])} if closes else None,
            "today": await day_summary(repo, clock, today),
            "unmatched": await unmatched(repo, clock),
            "exceptions": [
                {k: r[k] for k in ("id", "kind", "payment_id", "bill_id", "status", "opened_at")}
                for r in sorted(await repo.select(payment_exceptions), key=lambda r: r["opened_at"])
            ],
            "settlements": await settlement_rows(repo),
            "shifts": [
                {k: r[k] for k in shift_keys}
                for r in sorted(await repo.select(shifts), key=lambda r: r["opened_at"])
            ],
            "expenses": [
                {k: r[k] for k in ("id", "category", "amount_paise", "paid_from", "occurred_at")}
                for r in sorted(await repo.select(expenses), key=lambda r: r["seq"])
            ],
            "invalidate_on": [
                "payment.received",
                "payment.matched",
                "payment.exception.opened",
                "payment.exception.resolved",
                "payment.expense_recorded",
                "payment.daily_closed",
                "settlement.recorded",
                "staff.shift_opened",
                "staff.shift_closed",
            ],
        }

    return await read(request, session, build)


@router.get("/v1/views/reports")
async def reports(
    request: Request, session: Actor, month: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None
) -> dict[str, Any]:
    clock = request.app.state.clock

    async def build(repo: Repository) -> dict[str, Any]:
        from arth.domains.commerce_tables import month_closes

        chosen = month or (clock.now() + IST).strftime("%Y-%m")
        return {
            "month": chosen,
            "profile": (await settings_view(repo))["tax_profile"],
            "pnl": await profit_and_loss(repo, chosen),
            "gst": await gst_summary(repo, chosen),
            "closed_months": [
                {"month": r["month"], "net_paise": json.loads(r["pnl"])["net_paise"]}
                for r in sorted(await repo.select(month_closes), key=lambda r: r["month"])
            ],
            "scheduled": [],
            "invalidate_on": ["books.month_closed", "tax.invoice_issued"],
        }

    return await read(request, session, build)


@router.get("/v1/views/feedback")
async def feedback(request: Request, session: Actor) -> dict[str, Any]:
    return await read(request, session, feedback_view)


@router.get("/v1/views/trust")
async def trust(request: Request, session: Actor) -> dict[str, Any]:
    clock = request.app.state.clock
    policies = request.app.state.policies

    async def build(repo: Repository) -> dict[str, Any]:
        from arth.domains.commerce_tables import data_requests, data_sharing

        tiers = []
        for tier in ("R0", "R1", "R2", "R3", "R4"):
            tiers.append(
                {
                    "tier": tier,
                    "commands": sorted(k for k, v in policies.tiers.items() if v == tier),
                    "confirm_key": "trust.tier_" + tier.lower(),
                }
            )
        now = iso_utc(clock.now())
        recent = await recent_commands(repo, now, 50)
        audit = await verify_audit(repo)
        sharing = await repo.select(data_sharing)
        return {
            "tiers": tiers,  # TRU-1: generated from policies.yaml, never literal copy
            "roles": [
                {"role": name, "max_tier": role.max_tier, "approve": list(role.approve)}
                for name, role in sorted(policies.roles.items())
                if name != "system"
            ],
            "activity": [
                {k: r[k] for k in ("command_id", "type", "tier", "status", "actor_id", "occurred_at")}
                for r in recent
            ],  # TRU-2: from the audit chain
            "audit": {"ok": audit["valid"], "rows": audit["checked"]},
            "undo": [
                {"command_id": r["command_id"], "type": r["type"], "until": r["undo_until"]}
                for r in recent
                if r["undo_until"]
            ],
            "data_sharing": {"peer_benchmarks": bool(sharing and sharing[0]["peer_benchmarks"])},
            "data_requests": [
                {k: r[k] for k in ("kind", "patron_id", "occurred_at")}
                for r in sorted(await repo.select(data_requests), key=lambda r: r["seq"])
            ],
            "invalidate_on": [
                "command.executed",
                "approval.decided",
                "audit.verified",
                "privacy.erased",
                "privacy.sharing_changed",
            ],
        }

    return await read(request, session, build)


@router.get("/v1/views/health")
async def health(request: Request, session: Actor) -> dict[str, Any]:
    state = request.app.state

    async def build(repo: Repository) -> dict[str, Any]:
        device = await latest_health(repo)
        configured = provider_status(state.settings, state.providers)
        return {
            "device": device,
            "offline_queue": {
                "size": device["queue_size"] if device else 0,
                "last_sync_at": device["last_sync_at"] if device else None,
            },
            "providers": [
                {"name": name, "configured": ok, "mode": "unknown"} for name, ok in configured.items()
            ],
            "ai_spend_today_paise": 0,
            "backup": {"last_snapshot_at": None},
            "invalidate_on": ["device.health_reported"],
        }

    return await read(request, session, build)


@router.get("/v1/views/capital")
async def capital(request: Request, session: Actor) -> dict[str, Any]:
    return await read(request, session, lambda repo: capital_view(repo, request.app.state.clock))


@router.get("/v1/views/kot")
async def kot(request: Request, session: Actor) -> dict[str, Any]:
    clock = request.app.state.clock

    async def build(repo: Repository) -> dict[str, Any]:
        from arth.domains.catalog import get_item

        result = []
        for row in sorted(
            await repo.select(tickets, tickets.c.status != "served"), key=lambda r: r["created_at"]
        ):
            state = await bill_state(repo, row["bill_id"])
            lines = []
            for line in state["lines"]:
                item = await get_item(repo, line["item_id"])
                names = {o["id"]: o["name"] for g in item["modifier_groups"] for o in g["options"]}
                lines.append(
                    {
                        "name": line["name"],
                        "qty_milli": line["qty_milli"],
                        "modifiers": [names[m] for m in line["modifier_ids"] if m in names],
                    }
                )
            result.append(
                {
                    "id": row["id"],
                    "bill_id": row["bill_id"],
                    "token": row["token"],
                    "status": row["status"],
                    "age_seconds": int((clock.now() - parse_iso(row["created_at"])).total_seconds()),
                    "items": lines,
                }
            )
        return {"tickets": result, "invalidate_on": ["bill.ticket_changed", "bill.changed"]}

    return await read(request, session, build)


@router.get("/v1/views/appointments")
async def appointments(
    request: Request,
    session: Actor,
    date: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
) -> dict[str, Any]:
    day = date or (request.app.state.clock.now() + IST).date().isoformat()
    return await read(request, session, lambda repo: appointments_view(repo, day))


@router.get("/v1/views/rx")
async def rx(request: Request, session: Actor) -> dict[str, Any]:
    async def build(repo: Repository) -> dict[str, Any]:
        names = {r["id"]: json.loads(r["names"]) for r in await repo.select(items)}
        recalls = []
        for batch in await repo.select(batches, batches.c.recalled == 1):
            buyers = sorted(
                {
                    m["buyer_id"]
                    for m in await repo.select(stock_moves, stock_moves.c.batch_id == batch["id"])
                    if m["buyer_id"]
                }
            )
            recalls.append({"batch_id": batch["id"], "item_id": batch["item_id"], "buyer_ids": buyers})
        return {
            "rx_sales": [
                {
                    "bill_id": r["bill_id"],
                    "item_id": r["item_id"],
                    "name": names[r["item_id"]].get("en") or next(iter(names[r["item_id"]].values())),
                    "staff_id": r["staff_id"],
                    "occurred_at": r["occurred_at"],
                }
                for r in sorted(await repo.select(rx_records), key=lambda r: r["seq"])
            ],
            "refills_due": [],  # purchase cycles arrive in L3 (T3.5); refill runs need reminder consent (L5)
            "recalls": recalls,
            "invalidate_on": ["bill.paid", "batch.recalled", "order.changed"],
        }

    return await read(request, session, build)


@router.get("/v1/views/verdict/{check_id}")
async def verdict(request: Request, check_id: str, session: Actor) -> dict[str, Any]:
    return await read(request, session, lambda repo: verdict_view(repo, check_id))


@router.get("/v1/privacy/patrons/{patron_id}/export")
async def privacy_export(request: Request, patron_id: str, session: Actor) -> dict[str, Any]:
    if session.role != "owner":
        raise ProblemError(403, "policy.owner_required", "error.policy.owner_required", title="Owner only")
    result = await read(
        request, session, lambda repo: patron_export(repo, request.app.state.clock, patron_id)
    )
    return {**result, "invalidate_on": ["patron.changed", "credit.changed", "privacy.erased"]}


@router.get("/v1/public/storefront/{slug}")
async def public(request: Request, slug: str) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        owner = await Repository.storefront_slug_owner(conn, slug)
        if owner is None:
            raise ProblemError(404, "storefront.not_found", "error.storefront.not_found", title="Not found")
        try:
            page = await public_storefront(
                Repository(conn, owner), request.app.state.clock, request.app.state.packs
            )
        except CommandError as exc:
            raise ProblemError(
                404, "storefront.not_found", "error.storefront.not_found", title="Not found"
            ) from exc
    return {**page, "invalidate_on": ["storefront.published", "catalog.price_changed", "stock.changed"]}
