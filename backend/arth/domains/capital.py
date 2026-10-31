"""Capital: health profile, need, affordability and lender offers as read tools; applying is R4 on the
Console only (CAP-1…5). No agent tool can apply for a loan: AGENT_TOOLS lists reads only.
"""

from collections.abc import Awaitable, Callable
from datetime import date, timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.money import div_round_half_even
from arth.core.schemas import schema
from arth.domains.commerce_tables import (
    bills,
    loan_applications,
    loan_offers,
    payment_events,
    payments,
    purchase_orders,
    settlements,
    supplier_bills,
)
from arth.domains.ledger_projection import statement
from arth.domains.ledger_tables import credit_accounts, payable_allocations, payables
from arth.domains.merchants import domain_event, owner_only
from arth.domains.supply import suppliers
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository

WINDOW_DAYS = 28
EDI_SHARE_BP = 1500  # CAP-3: EDI ≤ 15% of P25 daily inflow
STRESS_BP = 8000  # … after a −20% stress
IST = timedelta(hours=5, minutes=30)
CONSOLE_POINTER = {"route": "/console/capital", "message_key": "capital.console_only"}


def _ist_day(stamp: str) -> date:
    return (parse_iso(stamp) + IST).date()


async def daily_inflows(repo: Repository, clock: SimClock) -> list[int]:
    today = (clock.now() + IST).date()
    days = {today - timedelta(days=n): 0 for n in range(1, WINDOW_DAYS + 1)}
    for row in await repo.select(payments):
        events = await repo.select(payment_events, payment_events.c.payment_id == row["id"])
        if events and max(events, key=lambda r: r["seq"])["status"] != "success":
            continue
        day = _ist_day(row["received_at"])
        if day in days:
            days[day] += row["amount_paise"]
    return [days[d] for d in sorted(days)]


def percentile(values: list[int], pct: int) -> int:
    ordered = sorted(values)
    if not ordered:
        return 0
    return ordered[min(len(ordered) - 1, (len(ordered) - 1) * pct // 100)]


async def health_profile(repo: Repository, clock: SimClock) -> dict[str, Any]:
    """CAP-1: computed from ledger tables only (payments, bills, khata, payables, settlements)."""
    inflows = await daily_inflows(repo, clock)
    rows = await repo.select(payments)
    upi = sum(r["amount_paise"] for r in rows if r["mode"].startswith("upi"))
    total = sum(r["amount_paise"] for r in rows)
    khata = 0
    for account in await repo.select(credit_accounts):
        khata += (await statement(repo, account["id"], clock))["balance_paise"]
    owed = 0
    for payable in await repo.select(payables):
        paid = await repo.select(payable_allocations, payable_allocations.c.payable_id == payable["id"])
        owed += payable["amount_paise"] - sum(r["amount_paise"] for r in paid)
    stamps = [r["received_at"] for r in rows] + [r["opened_at"] for r in await repo.select(bills)]
    first = min(stamps) if stamps else None
    return {
        "history_days": ((clock.now() + IST).date() - _ist_day(first)).days if first else 0,
        "avg_daily_inflow_paise": sum(inflows) // len(inflows),
        "p25_daily_inflow_paise": percentile(inflows, 25),
        "upi_share_bp": upi * 10000 // total if total else 0,
        "khata_outstanding_paise": khata,
        "payables_due_paise": owed,
        "settlements": len(await repo.select(settlements)),
    }


async def need(repo: Repository, clock: SimClock) -> dict[str, Any] | None:
    """CAP-2: the largest open PO whose total the conservative (P25) inflow cannot cover by its due date."""
    profile = await health_profile(repo, clock)
    best = None
    billed = {r["po_id"] for r in await repo.select(supplier_bills)}
    for po in await repo.select(
        purchase_orders, purchase_orders.c.status.in_(["sent", "confirmed", "received"])
    ):
        if po["id"] in billed and po["status"] == "received":
            continue
        lead = (await repo.select(suppliers, suppliers.c.id == po["supplier_id"]))[0]["lead_days"]
        due = (
            date.fromisoformat(po["due_on"])
            if po["due_on"]
            else (clock.now() + IST).date() + timedelta(days=lead)
        )
        days = max((due - (clock.now() + IST).date()).days, 0)
        shortfall = po["total_paise"] - profile["p25_daily_inflow_paise"] * days
        if shortfall > 0 and (best is None or shortfall > best["shortfall_paise"]):
            best = {
                "purpose_ref": po["id"],
                "purpose_key": "capital.purpose_po",
                "po_total_paise": po["total_paise"],
                "shortfall_paise": shortfall,
                "shortfall_date": due.isoformat(),
            }
    return best


def total_repayment(offer: dict[str, Any]) -> int:
    return int(offer["edi_paise"] * offer["tenor_days"])


async def affordability(repo: Repository, clock: SimClock) -> dict[str, Any]:
    """CAP-3: EDI cap = 15% of P25 daily inflow after a −20% stress."""
    profile = await health_profile(repo, clock)
    stressed = div_round_half_even(profile["p25_daily_inflow_paise"] * STRESS_BP, 10000)
    return {
        "p25_daily_inflow_paise": profile["p25_daily_inflow_paise"],
        "stressed_inflow_paise": stressed,
        "max_edi_paise": div_round_half_even(stressed * EDI_SHARE_BP, 10000),
    }


async def offers(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    cap = (await affordability(repo, clock))["max_edi_paise"]
    now = iso_utc(clock.now())
    keys = (
        "id",
        "lender",
        "amount_paise",
        "tenor_days",
        "apr_bp",
        "edi_paise",
        "processing_fee_paise",
        "kfs_url",
        "cooling_off_days",
        "expires_at",
    )
    return [
        {k: r[k] for k in keys}
        | {"total_repayment_paise": total_repayment(r), "affordable": r["edi_paise"] <= cap}
        for r in sorted(await repo.select(loan_offers), key=lambda r: r["amount_paise"])
        if r["expires_at"] > now
    ]


async def capital_view(repo: Repository, clock: SimClock) -> dict[str, Any]:
    gap = await need(repo, clock)
    listed = await offers(repo, clock)
    fits = [
        o for o in listed if o["affordable"] and (gap is None or o["amount_paise"] >= gap["shortfall_paise"])
    ]
    return {
        "profile": await health_profile(repo, clock),
        "need": gap,
        "affordability": await affordability(repo, clock),
        "offers": listed,
        "recommended_offer_id": fits[0]["id"] if fits and gap else None,  # smallest amount closing the gap
        "console_pointer": CONSOLE_POINTER,  # the device never shows an apply button
        "invalidate_on": ["capital.offer_received", "capital.applied", "po.changed", "payment.received"],
    }


ReadTool = Callable[[Repository, SimClock], Awaitable[Any]]
# The only capital tools an agent may call. There is deliberately no apply tool (CAP-5).
AGENT_TOOLS: dict[str, ReadTool] = {
    "capital.profile": health_profile,
    "capital.need": need,
    "capital.affordability": affordability,
    "capital.offers": offers,
}


def register_capital(bus: CommandBus) -> None:
    async def record_offer(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if repo.session is None or repo.session.role != "system" or not repo.private.get("lender_verified"):
            raise CommandError("capital.verified_lender_required")
        identity = new_id("loan")
        await repo.insert(
            loan_offers,
            {
                "id": identity,
                **payload,
                "purpose_ref": payload.get("purpose_ref"),
                "received_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(bus, repo, "capital.offer_received", {"offer_id": identity})
        return {"offer_id": identity}

    async def apply(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        assert repo.session is not None
        if repo.session.channel != "console" or not repo.session.step_up:
            raise CommandError("policy.console_required")  # defence in depth behind the R4 policy
        rows = await repo.select(loan_offers, loan_offers.c.id == payload["offer_id"])
        if not rows or rows[0]["expires_at"] <= iso_utc(bus.clock.now()):
            raise CommandError("capital.offer_not_available")
        if await repo.select(loan_applications, loan_applications.c.offer_id == payload["offer_id"]):
            raise CommandError("capital.already_applied")
        identity = new_id("loanapp")
        await repo.insert(
            loan_applications,
            {
                "id": identity,
                "offer_id": payload["offer_id"],
                "status": "submitted",
                "staff_id": repo.session.actor_id,
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(
            bus, repo, "capital.applied", {"offer_id": payload["offer_id"], "application_id": identity}
        )
        return {
            "application_id": identity,
            "status": "submitted",
            "cooling_off_days": rows[0]["cooling_off_days"],
        }

    bus.register("capital.record_offer", schema("capital_record_offer"), record_offer)
    bus.register("capital.apply", schema("capital_apply"), apply)
