"""Treasury: unified payments, matching, unmatched queue, payment exceptions, refunds, settlements,
expenses, daily close and per-shift expected cash (TRS-1…5, PEX-1…3, PEX-5, STF-3).

Rails callbacks are trusted only from the restricted system actor with `payment_verified`.
"""

import json
from datetime import timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.commerce_tables import (
    bill_payments,
    bills,
    daily_closes,
    expenses,
    payment_events,
    payment_exceptions,
    payment_matches,
    payments,
    refunds,
    settlement_lines,
    settlements,
    upi_intents,
)
from arth.domains.ledger_money import allocate_payment
from arth.domains.ledger_projection import statement
from arth.domains.ledger_tables import credit_accounts, credit_entries
from arth.domains.merchants import domain_event, owner_only
from arth.domains.patron_identity import related_ids
from arth.domains.patron_tables import patron_identities
from arth.domains.tables import shifts
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import PolicyContext
from arth.governance.repository import Repository

DUPLICATE_WINDOW = timedelta(minutes=10)


def _verified(repo: Repository) -> None:
    if repo.session is None or repo.session.role != "system" or not repo.private.get("payment_verified"):
        raise CommandError("treasury.verified_callback_required")


async def payment_status(repo: Repository, payment_id: str) -> str:
    rows = await repo.select(payment_events, payment_events.c.payment_id == payment_id)
    return max(rows, key=lambda r: r["seq"])["status"] if rows else "success"


async def record_counter_payment(
    repo: Repository, clock: SimClock, bill_id: str, mode: str, amount: int
) -> str:
    """Cash and card taken at the counter join the unified payments table, matched to their bill."""
    assert repo.session is not None
    identity = new_id("payment")
    now = iso_utc(clock.now())
    await repo.insert(
        payments,
        {
            "id": identity,
            "mode": mode,
            "amount_paise": amount,
            "utr": None,
            "order_ref": None,
            "payer_ref": None,
            "source": "counter",
            "staff_id": repo.session.actor_id,
            "received_at": now,
        },
    )
    await repo.insert(
        payment_events,
        {"id": new_id("pevt"), "payment_id": identity, "status": "success", "occurred_at": now},
    )
    await repo.insert(
        payment_matches,
        {
            "id": new_id("pmatch"),
            "payment_id": identity,
            "target_kind": "bill",
            "target_id": bill_id,
            "matched_by": "counter",
            "occurred_at": now,
        },
    )
    return identity


async def matched_target(repo: Repository, payment_id: str) -> dict[str, Any] | None:
    rows = await repo.select(payment_matches, payment_matches.c.payment_id == payment_id)
    return rows[0] if rows else None


async def suggestions(repo: Repository, clock: SimClock, payment: dict[str, Any]) -> list[dict[str, Any]]:
    """TRS-1/PEX-3: open bills ranked by amount closeness, then time closeness."""
    received = parse_iso(payment["received_at"])
    ranked = []
    from arth.domains.counter import bill_state

    for row in await repo.select(bills, bills.c.status.in_(["open", "parked"])):
        state = await bill_state(repo, row["id"])
        if state["due_paise"] <= 0:
            continue
        gap = abs(state["due_paise"] - payment["amount_paise"])
        minutes = abs((received - parse_iso(row["opened_at"])).total_seconds()) / 60
        score = max(0, 10000 - gap * 10000 // max(payment["amount_paise"], 1) - int(minutes) * 10)
        ranked.append(
            {"bill_id": row["id"], "total_paise": state["due_paise"], "score_bp": min(score, 10000)}
        )
    return sorted(ranked, key=lambda r: (-r["score_bp"], r["bill_id"]))[:3]


async def khata_hint(repo: Repository, clock: SimClock, payment: dict[str, Any]) -> str | None:
    """LED-8/PEX-3: a payment from a known khata customer with a balance → 'khate mein jama karun?'.

    `payer_ref` is the merchant-scoped VPA hash computed by the rails adapter; raw VPAs never arrive here.
    """
    if not payment["payer_ref"]:
        return None
    rows = await repo.select(
        patron_identities,
        patron_identities.c.kind == "vpa_hash",
        patron_identities.c.value == payment["payer_ref"],
    )
    if len({r["patron_id"] for r in rows}) != 1:
        return None
    patron_id = rows[0]["patron_id"]
    accounts = await repo.select(
        credit_accounts, credit_accounts.c.patron_id.in_(await related_ids(repo, patron_id))
    )
    if accounts and (await statement(repo, accounts[0]["id"], clock))["balance_paise"] > 0:
        return str(patron_id)
    return None


async def unmatched(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    result = []
    for row in sorted(await repo.select(payments, payments.c.source == "rails"), key=lambda r: r["seq"]):
        if await matched_target(repo, row["id"]) or await payment_status(repo, row["id"]) != "success":
            continue
        if await repo.select(
            payment_exceptions,
            payment_exceptions.c.payment_id == row["id"],
            payment_exceptions.c.kind == "duplicate",
        ):
            continue
        result.append(
            {
                "payment_id": row["id"],
                "amount_paise": row["amount_paise"],
                "received_at": row["received_at"],
                "khata_patron_id": await khata_hint(repo, clock, row),
                "suggestions": await suggestions(repo, clock, row),
            }
        )
    return result


async def shift_cash(repo: Repository, shift: dict[str, Any], until: str) -> int:
    """STF-3/TRS-3: float + cash taken − change given − cash refunds − cash expenses by this staff."""
    window = (shift["opened_at"], until)
    taken = sum(
        r["amount_paise"]
        for r in await repo.select(
            payments, payments.c.mode == "cash", payments.c.staff_id == shift["staff_id"]
        )
        if window[0] <= r["received_at"] <= window[1]
    )
    out = sum(
        r["amount_paise"]
        for r in await repo.select(refunds, refunds.c.mode == "cash", refunds.c.staff_id == shift["staff_id"])
        if window[0] <= r["occurred_at"] <= window[1]
    ) + sum(
        r["amount_paise"]
        for r in await repo.select(
            expenses, expenses.c.paid_from == "cash", expenses.c.staff_id == shift["staff_id"]
        )
        if window[0] <= r["occurred_at"] <= window[1]
    )
    return int(shift["float_paise"]) + taken - out


async def settlement_rows(repo: Repository) -> list[dict[str, Any]]:
    result = []
    for row in sorted(await repo.select(settlements), key=lambda r: r["seq"]):
        lines = await repo.select(settlement_lines, settlement_lines.c.settlement_id == row["id"])
        deductions = [{"kind": r["kind"], "amount_paise": r["amount_paise"]} for r in lines]
        result.append(
            {
                "id": row["id"],
                "date": row["date"],
                "gross_paise": row["gross_paise"],
                "net_paise": row["net_paise"],
                "deductions": deductions,
                "explained": row["gross_paise"] - sum(d["amount_paise"] for d in deductions)
                == row["net_paise"],
            }
        )
    return result


async def day_summary(repo: Repository, clock: SimClock, day: str) -> dict[str, Any]:
    def ist_day(stamp: str) -> str:
        return (parse_iso(stamp) + timedelta(hours=5, minutes=30)).date().isoformat()

    by_mode: dict[str, int] = {}
    for row in await repo.select(payments):
        if ist_day(row["received_at"]) == day and await payment_status(repo, row["id"]) == "success":
            by_mode[row["mode"]] = by_mode.get(row["mode"], 0) + row["amount_paise"]
    khata = sum(
        r["amount_paise"]
        for r in await repo.select(bill_payments, bill_payments.c.mode == "khata")
        if ist_day(r["occurred_at"]) == day
    )
    spent = sum(r["amount_paise"] for r in await repo.select(expenses) if ist_day(r["occurred_at"]) == day)
    refunded = sum(r["amount_paise"] for r in await repo.select(refunds) if ist_day(r["occurred_at"]) == day)
    return {
        "sales_paise": sum(by_mode.values()),
        "by_mode": by_mode,
        "expenses_paise": spent,
        "refunds_paise": refunded,
        "khata_given_paise": khata,
    }


def register_treasury(bus: CommandBus) -> None:
    clock = bus.clock

    async def exception(
        repo: Repository, kind: str, payment_id: str | None, bill_id: str | None, detail: dict[str, Any]
    ) -> str:
        identity = new_id("pex")
        await repo.insert(
            payment_exceptions,
            {
                "id": identity,
                "kind": kind,
                "payment_id": payment_id,
                "bill_id": bill_id,
                "status": "open",
                "detail": json.dumps(detail),
                "opened_at": iso_utc(clock.now()),
            },
        )
        await domain_event(bus, repo, "payment.exception.opened", {"exception_id": identity, "kind": kind})
        return identity

    async def settle_exceptions(repo: Repository, payment_id: str, kinds: set[str]) -> None:
        for row in await repo.select(
            payment_exceptions,
            payment_exceptions.c.payment_id == payment_id,
            payment_exceptions.c.status == "open",
        ):
            if row["kind"] in kinds:
                await repo.update(
                    payment_exceptions,
                    {"status": "resolved", "resolved_at": iso_utc(clock.now())},
                    payment_exceptions.c.id == row["id"],
                )

    async def pay_bill(repo: Repository, payment: dict[str, Any], bill_id: str, by: str) -> dict[str, Any]:
        from arth.domains.counter import bill_state, close_bill

        state = await bill_state(repo, bill_id)
        if state["status"] not in {"open", "parked"} or payment["amount_paise"] > state["due_paise"]:
            raise CommandError("treasury.bill_not_payable")
        await repo.insert(
            payment_matches,
            {
                "id": new_id("pmatch"),
                "payment_id": payment["id"],
                "target_kind": "bill",
                "target_id": bill_id,
                "matched_by": by,
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await domain_event(
            bus,
            repo,
            "payment.matched",
            {"payment_id": payment["id"], "target_kind": "bill", "target_id": bill_id},
        )
        row = {"mode": "upi", "amount_paise": payment["amount_paise"], "ref_id": payment["id"]}
        if payment["amount_paise"] == state["due_paise"]:
            return await close_bill(bus, repo, bill_id, [row])
        await repo.insert(
            bill_payments,
            {"id": new_id("bpay"), "bill_id": bill_id, "occurred_at": iso_utc(clock.now()), **row},
        )
        return {"bill_id": bill_id, "status": state["status"]}

    async def is_duplicate(repo: Repository, payment: dict[str, Any]) -> str | None:
        """PEX-2: same payer, same amount, within 10 minutes, and that earlier payment already paid a bill."""
        if not payment["payer_ref"]:
            return None
        since = iso_utc(parse_iso(payment["received_at"]) - DUPLICATE_WINDOW)
        for row in await repo.select(
            payments,
            payments.c.payer_ref == payment["payer_ref"],
            payments.c.amount_paise == payment["amount_paise"],
            payments.c.id != payment["id"],
        ):
            if row["received_at"] >= since and await payment_status(repo, row["id"]) == "success":
                match = await matched_target(repo, row["id"])
                if match and match["target_kind"] == "bill":
                    bill = await repo.select(bills, bills.c.id == match["target_id"])
                    if bill and bill[0]["status"] == "closed":
                        return str(match["target_id"])
        return None

    async def rails_event(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        _verified(repo)
        now = iso_utc(clock.now())
        existing = await repo.select(payments, payments.c.utr == payload["utr"])
        if existing:
            payment = existing[0]
            if payment["amount_paise"] != payload["amount_paise"]:
                raise CommandError("treasury.utr_conflict")
            previous = await payment_status(repo, payment["id"])
            if previous == payload["status"] or previous in {"success", "failed", "refunded"}:
                return {"payment_id": payment["id"], "status": previous, "replay": True}
        else:
            payment = {
                "id": new_id("payment"),
                "mode": payload["mode"],
                "amount_paise": payload["amount_paise"],
                "utr": payload["utr"],
                "order_ref": payload.get("order_ref"),
                "payer_ref": payload.get("payer_ref"),
                "source": "rails",
                "staff_id": None,
                "received_at": now,
            }
            await repo.insert(payments, payment)
        await repo.insert(
            payment_events,
            {
                "id": new_id("pevt"),
                "payment_id": payment["id"],
                "status": payload["status"],
                "occurred_at": now,
            },
        )
        intent = None
        if payment["order_ref"]:
            rows = await repo.select(upi_intents, upi_intents.c.order_ref == payment["order_ref"])
            intent = rows[0] if rows else None
        bill_id = intent["bill_id"] if intent else None
        if payload["status"] == "pending":
            if intent:
                await repo.update(upi_intents, {"status": "pending"}, upi_intents.c.id == intent["id"])
            await exception(repo, "pending", payment["id"], bill_id, {"utr": payload["utr"]})
            await domain_event(
                bus, repo, "payment.pending", {"payment_id": payment["id"], "bill_id": bill_id}
            )
            return {"payment_id": payment["id"], "status": "pending", "bill_id": bill_id}
        await settle_exceptions(repo, payment["id"], {"pending"})
        if payload["status"] == "failed":
            if intent:
                await repo.update(upi_intents, {"status": "failed"}, upi_intents.c.id == intent["id"])
            await exception(
                repo, "failed", payment["id"], bill_id, {"alternatives": ["cash", "khata", "regenerate"]}
            )
            await domain_event(bus, repo, "payment.failed", {"payment_id": payment["id"], "bill_id": bill_id})
            return {
                "payment_id": payment["id"],
                "status": "failed",
                "bill_id": bill_id,
                "alternatives": ["cash", "khata", "regenerate"],
            }
        result: dict[str, Any] = {"payment_id": payment["id"], "status": "success", "bill_id": None}
        duplicate_of = await is_duplicate(repo, payment)
        if duplicate_of and not (intent and intent["status"] in {"waiting", "pending"}):
            await exception(
                repo,
                "duplicate",
                payment["id"],
                duplicate_of,
                {"suggestion": "treasury.refund", "tier": "R4"},
            )
            result["duplicate_of_bill"] = duplicate_of
        elif (
            intent
            and intent["status"] in {"waiting", "pending"}
            and payment["amount_paise"] == intent["amount_paise"]
        ):
            await repo.update(upi_intents, {"status": "paid"}, upi_intents.c.id == intent["id"])
            result["bill_id"] = intent["bill_id"]
            result["bill"] = await pay_bill(repo, payment, intent["bill_id"], "order_ref")
        else:
            await exception(repo, "unmatched", payment["id"], None, {})
        await domain_event(
            bus,
            repo,
            "payment.received",
            {
                "payment_id": payment["id"],
                "amount_paise": payment["amount_paise"],
                "mode": payment["mode"],
                "bill_id": result["bill_id"],
            },
        )
        from arth.domains.offers import on_payment

        result["offers"] = await on_payment(bus, repo, payment)
        return result

    async def unmatched_payment(repo: Repository, payment_id: str) -> dict[str, Any]:
        rows = await repo.select(payments, payments.c.id == payment_id)
        if not rows:
            raise CommandError("treasury.payment_not_found")
        if await matched_target(repo, payment_id) or await payment_status(repo, payment_id) != "success":
            raise CommandError("treasury.payment_not_matchable")
        return rows[0]

    async def match_bill(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        payment = await unmatched_payment(repo, payload["payment_id"])
        result = await pay_bill(
            repo, payment, payload["bill_id"], repo.session.actor_id if repo.session else ""
        )
        await settle_exceptions(repo, payment["id"], {"unmatched"})
        return {"payment_id": payment["id"], **result}

    async def match_khata(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        payment = await unmatched_payment(repo, payload["payment_id"])
        allocated = await allocate_payment(
            repo, clock, payload["account_id"], payment["amount_paise"], payment["id"], "upi"
        )
        await repo.insert(
            payment_matches,
            {
                "id": new_id("pmatch"),
                "payment_id": payment["id"],
                "target_kind": "khata",
                "target_id": payload["account_id"],
                "matched_by": repo.session.actor_id if repo.session else "",
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await settle_exceptions(repo, payment["id"], {"unmatched"})
        await domain_event(
            bus,
            repo,
            "payment.matched",
            {"payment_id": payment["id"], "target_kind": "khata", "target_id": payload["account_id"]},
        )
        await domain_event(bus, repo, "credit.changed", {"account_id": payload["account_id"]})
        return allocated

    async def refund(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        rows = await repo.select(payments, payments.c.id == payload["payment_id"])
        if not rows:
            raise CommandError("treasury.payment_not_found")
        payment = rows[0]
        done = sum(
            r["amount_paise"] for r in await repo.select(refunds, refunds.c.payment_id == payment["id"])
        )
        if payload["amount_paise"] > payment["amount_paise"] - done:
            raise CommandError("treasury.refund_exceeds_payment")
        identity = new_id("refund")
        mode = "upi" if payment["mode"].startswith("upi") else payment["mode"]
        match = await matched_target(repo, payment["id"])
        await repo.insert(
            refunds,
            {
                "id": identity,
                "payment_id": payment["id"],
                "bill_id": match["target_id"] if match and match["target_kind"] == "bill" else None,
                "amount_paise": payload["amount_paise"],
                "mode": mode,
                "reason_key": payload["reason_key"],
                "staff_id": repo.session.actor_id if repo.session else None,
                "occurred_at": iso_utc(clock.now()),
            },
        )
        if done + payload["amount_paise"] == payment["amount_paise"]:
            await repo.insert(
                payment_events,
                {
                    "id": new_id("pevt"),
                    "payment_id": payment["id"],
                    "status": "refunded",
                    "occurred_at": iso_utc(clock.now()),
                },
            )
        await settle_exceptions(repo, payment["id"], {"duplicate", "refund_due"})
        from arth.domains.offers import claw_back

        clawed = await claw_back(bus, repo, payment["id"])
        await domain_event(
            bus,
            repo,
            "payment.refunded",
            {"refund_id": identity, "amount_paise": payload["amount_paise"], "mode": mode},
        )
        return {"refund_id": identity, "amount_paise": payload["amount_paise"], "clawed_back": clawed}

    async def expense(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        assert repo.session is not None
        identity = new_id("expense")
        await repo.insert(
            expenses,
            {
                "id": identity,
                "category": payload["category"],
                "amount_paise": payload["amount_paise"],
                "paid_from": payload["paid_from"],
                "note_key": payload.get("note_key"),
                "staff_id": repo.session.actor_id,
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await domain_event(
            bus,
            repo,
            "payment.expense_recorded",
            {"expense_id": identity, "amount_paise": payload["amount_paise"]},
        )
        return {"expense_id": identity, "readback_key": "treasury.expense_readback", **payload}

    async def record_settlement(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        _verified(repo)
        existing = await repo.select(settlements, settlements.c.external_ref == payload["external_ref"])
        if existing:
            return {"settlement_id": existing[0]["id"], "replay": True}
        identity = new_id("stl")
        await repo.insert(
            settlements,
            {
                "id": identity,
                "external_ref": payload["external_ref"],
                "date": payload["date"],
                "gross_paise": payload["gross_paise"],
                "net_paise": payload["net_paise"],
                "occurred_at": iso_utc(clock.now()),
            },
        )
        for line in payload["lines"]:
            await repo.insert(settlement_lines, {"id": new_id("stline"), "settlement_id": identity, **line})
        utrs = set(payload["utrs"])
        covered = (
            sum(r["amount_paise"] for r in await repo.select(payments, payments.c.utr.in_(utrs)))
            if utrs
            else 0
        )
        explained = (
            payload["gross_paise"] - sum(r["amount_paise"] for r in payload["lines"]) == payload["net_paise"]
        )
        matches = explained and (not utrs or covered == payload["gross_paise"])
        if not matches:
            await exception(
                repo,
                "settlement_mismatch",
                None,
                None,
                {"settlement_id": identity, "gross_paise": payload["gross_paise"], "covered_paise": covered},
            )
        await domain_event(bus, repo, "settlement.recorded", {"settlement_id": identity, "matches": matches})
        return {"settlement_id": identity, "matches": matches}

    async def daily_close(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if await repo.select(daily_closes, daily_closes.c.date == payload["date"]):
            raise CommandError("treasury.day_closed")
        summary = {
            **await day_summary(repo, clock, payload["date"]),
            "unmatched": len(await unmatched(repo, clock)),
            "open_exceptions": len(
                await repo.select(payment_exceptions, payment_exceptions.c.status == "open")
            ),
            "variance_paise": sum(
                r["variance_paise"] or 0
                for r in await repo.select(shifts)
                if r["closed_at"] and r["closed_at"][:10] >= payload["date"][:10]
            ),
        }
        await repo.insert(
            daily_closes,
            {
                "id": new_id("close"),
                "date": payload["date"],
                "summary": json.dumps(summary),
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await domain_event(bus, repo, "payment.daily_closed", {"date": payload["date"]})
        return {"date": payload["date"], "summary": summary, "sensitivity": "discreet"}

    async def resolve(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        rows = await repo.select(
            payment_exceptions,
            payment_exceptions.c.id == payload["exception_id"],
            payment_exceptions.c.status == "open",
        )
        if not rows:
            raise CommandError("treasury.exception_not_found")
        await repo.update(
            payment_exceptions,
            {"status": "resolved", "resolved_at": iso_utc(clock.now())},
            payment_exceptions.c.id == payload["exception_id"],
        )
        await domain_event(bus, repo, "payment.exception.resolved", payload)
        return payload

    async def sensitive(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        return PolicyContext(sensitive=True)

    for kind, handler in [
        ("treasury.rails_event", rails_event),
        ("treasury.match_bill", match_bill),
        ("treasury.match_khata", match_khata),
        ("treasury.refund", refund),
        ("treasury.expense", expense),
        ("treasury.record_settlement", record_settlement),
        ("treasury.daily_close", daily_close),
        ("treasury.resolve_exception", resolve),
    ]:
        bus.register(
            kind,
            schema(kind.replace(".", "_")),
            handler,
            sensitive if kind != "treasury.rails_event" else None,
        )


__all__ = ["register_treasury", "record_counter_payment", "shift_cash", "unmatched", "credit_entries"]
