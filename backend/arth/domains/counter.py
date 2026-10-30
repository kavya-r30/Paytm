"""Counter: bills, running tab with undo, park/resume, checkout (cash, card, UPI, khata), returns, KOT.

Quantities and amounts are computed here, never by a model (CTR-3). Money rows are append-only;
a bill's totals are derived from its active lines and its `bill_payments` rows.
"""

import json
from datetime import timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.core.money import div_round_half_even
from arth.core.packs import PackRegistry
from arth.core.qty import line_amount
from arth.core.schemas import schema
from arth.domains.catalog import get_item, modifier_total
from arth.domains.commerce_tables import (
    bill_lines,
    bill_ops,
    bill_payments,
    bills,
    payment_exceptions,
    refunds,
    return_lines,
    returns,
    rx_records,
    ticket_events,
    tickets,
    upi_intents,
)
from arth.domains.ledger_projection import account_view
from arth.domains.ledger_tables import advances, credit_entries, credit_entry_lines
from arth.domains.merchants import domain_event, owner_only
from arth.domains.patron_identity import patron_row, related_ids
from arth.domains.patron_tables import household_members
from arth.domains.stock import issue_stock, on_hand, stock_tracked
from arth.domains.stock_tables import stock_moves
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import PolicyContext
from arth.governance.repository import Repository
from arth.governance.tables import merchants

PRICE_GUARD_BP = 2500  # CTR-10: >25% from the usual price needs owner/manager + reason
TICKET_FLOW = {"new": "preparing", "preparing": "ready", "ready": "served"}
UPI_VALIDITY = timedelta(minutes=5)
LOOSE_UNITS = {"g", "kg", "ml", "l"}


async def bill_row(repo: Repository, bill_id: str) -> dict[str, Any]:
    rows = await repo.select(bills, bills.c.id == bill_id)
    if not rows:
        raise CommandError("counter.bill_not_found")
    return rows[0]


async def bill_state(repo: Repository, bill_id: str) -> dict[str, Any]:
    row = await bill_row(repo, bill_id)
    lines = []
    for line in await repo.select(
        bill_lines, bill_lines.c.bill_id == bill_id, bill_lines.c.status == "active"
    ):
        item = await get_item(repo, line["item_id"])
        lines.append(
            {
                "id": line["id"],
                "item_id": line["item_id"],
                "name": item["names"].get("en") or next(iter(item["names"].values())),
                "qty_milli": line["qty_milli"],
                "unit_price_paise": line["unit_price_paise"],
                "amount_paise": line["amount_paise"],
                "added_via": line["added_via"],
                "modifier_ids": json.loads(line["modifiers"]),
                "price_override": bool(line["price_override"]),
                "batch_id": line["batch_id"],
            }
        )
    paid = await repo.select(bill_payments, bill_payments.c.bill_id == bill_id)
    total = sum(line["amount_paise"] for line in lines) if row["status"] != "closed" else row["total_paise"]
    khata = sum(p["amount_paise"] for p in paid if p["mode"] == "khata")
    settled = sum(p["amount_paise"] for p in paid if p["mode"] != "khata")
    ticket = await repo.select(tickets, tickets.c.bill_id == bill_id)
    intents = sorted(
        await repo.select(upi_intents, upi_intents.c.bill_id == bill_id), key=lambda r: r["created_at"]
    )
    return {
        "id": row["id"],
        "status": row["status"],
        "patron_id": row["patron_id"],
        "staff_id": row["staff_id"],
        "opened_at": row["opened_at"],
        "closed_at": row["closed_at"],
        "total_paise": total,
        "paid_paise": settled,
        "khata_paise": khata,
        "due_paise": max(total - settled - khata, 0),
        "lines": lines,
        "payments": [
            {k: p[k] for k in ("mode", "amount_paise", "change_paise", "ref_id")}
            for p in sorted(paid, key=lambda r: r["seq"])
        ],
        "ticket": {k: ticket[0][k] for k in ("id", "token", "status")} if ticket else None,
        "upi": {k: intents[-1][k] for k in ("order_ref", "amount_paise", "status", "expires_at")}
        if intents
        else None,
    }


def _session(repo: Repository) -> Any:
    assert repo.session is not None and repo.command_id is not None
    return repo.session


def _manager(repo: Repository) -> None:
    if _session(repo).role not in {"owner", "manager"}:
        raise CommandError("policy.role")


async def _open_bill(repo: Repository, bill_id: str) -> dict[str, Any]:
    row = await bill_row(repo, bill_id)
    if row["status"] != "open":
        raise CommandError("counter.bill_not_open")
    return row


async def _pack(repo: Repository, packs: PackRegistry) -> Any:
    return packs.get((await repo.select(merchants))[0]["pack"])


async def close_bill(
    bus: CommandBus, repo: Repository, bill_id: str, settle: list[dict[str, Any]]
) -> dict[str, Any]:
    """Record final payments, issue stock (FEFO; recipes consume ingredients), invoice and emit."""
    clock = bus.clock
    current = await bill_state(repo, bill_id)
    if current["status"] not in {"open", "parked"}:
        raise CommandError("counter.bill_not_open")
    if not current["lines"]:
        raise CommandError("counter.empty_bill")
    now = iso_utc(clock.now())
    for payment in settle:
        await repo.insert(
            bill_payments, {"id": new_id("bpay"), "bill_id": bill_id, "occurred_at": now, **payment}
        )
    paid = await repo.select(bill_payments, bill_payments.c.bill_id == bill_id)
    if sum(p["amount_paise"] for p in paid) != current["total_paise"]:
        raise CommandError("counter.payment_mismatch")
    row = await bill_row(repo, bill_id)
    for line in await repo.select(
        bill_lines, bill_lines.c.bill_id == bill_id, bill_lines.c.status == "active"
    ):
        item = await get_item(repo, line["item_id"])
        if "duration_minutes" in item["details"]:
            continue
        if item["recipe"]:
            for ingredient in item["recipe"]:
                qty = div_round_half_even(line["qty_milli"] * ingredient["qty_milli"], 1000)
                if qty and await stock_tracked(repo, ingredient["item_id"]):
                    await issue_stock(repo, clock, ingredient["item_id"], qty, bill_id, row["patron_id"])
        elif await stock_tracked(repo, line["item_id"]):
            await issue_stock(
                repo,
                clock,
                line["item_id"],
                line["qty_milli"],
                bill_id,
                row["patron_id"],
                line["batch_id"],
                line["override_reason"] if line["batch_id"] else None,
            )
    await repo.update(
        bills,
        {"status": "closed", "closed_at": now, "total_paise": current["total_paise"]},
        bills.c.id == bill_id,
    )
    for intent in await repo.select(
        upi_intents, upi_intents.c.bill_id == bill_id, upi_intents.c.status == "waiting"
    ):
        await repo.update(upi_intents, {"status": "expired"}, upi_intents.c.id == intent["id"])
    from arth.domains.tax import issue_invoice

    await issue_invoice(repo, clock, bill_id)
    khata = sum(p["amount_paise"] for p in paid if p["mode"] == "khata")
    await domain_event(
        bus,
        repo,
        "bill.paid",
        {"bill_id": bill_id, "total_paise": current["total_paise"], "khata_paise": khata},
    )
    await domain_event(bus, repo, "bill.changed", {"bill_id": bill_id, "status": "closed"})
    return {"bill_id": bill_id, "status": "closed", "total_paise": current["total_paise"]}


def register_counter(bus: CommandBus, packs: PackRegistry) -> None:
    clock: SimClock = bus.clock

    async def changed(repo: Repository, bill_id: str) -> None:
        row = await bill_row(repo, bill_id)
        await domain_event(bus, repo, "bill.changed", {"bill_id": bill_id, "status": row["status"]})
        for intent in await repo.select(
            upi_intents, upi_intents.c.bill_id == bill_id, upi_intents.c.status == "waiting"
        ):
            if row["status"] == "open":
                await repo.update(upi_intents, {"status": "expired"}, upi_intents.c.id == intent["id"])

    async def op(repo: Repository, bill_id: str, kind: str, added: str | None, voided: str | None) -> None:
        await repo.insert(
            bill_ops,
            {
                "id": new_id("billop"),
                "bill_id": bill_id,
                "kind": kind,
                "line_added": added,
                "line_voided": voided,
                "occurred_at": iso_utc(clock.now()),
            },
        )

    async def open_bill(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("patron_id"):
            await patron_row(repo, payload["patron_id"])
        identity = new_id("bill")
        await repo.insert(
            bills,
            {
                "id": identity,
                "status": "open",
                "patron_id": payload.get("patron_id"),
                "staff_id": _session(repo).actor_id,
                "opened_at": iso_utc(clock.now()),
            },
        )
        await changed(repo, identity)
        return {"bill_id": identity}

    async def priced_line(repo: Repository, bill_id: str, spec: dict[str, Any]) -> dict[str, Any]:
        item = await get_item(repo, spec["item_id"])
        pack = await _pack(repo, packs)
        if ("qty_milli" in spec) == ("amount_paise" in spec):
            raise CommandError("counter.qty_or_amount_required")
        selections: dict[str, list[str]] = {}
        groups = {o["id"]: g["id"] for g in item["modifier_groups"] for o in g["options"]}
        for modifier in spec.get("modifier_ids", []):
            if modifier not in groups:
                raise CommandError("catalog.invalid_modifier")
            selections.setdefault(groups[modifier], []).append(modifier)
        usual = (
            await modifier_total(repo, spec["item_id"], selections)
            if item["modifier_groups"]
            else item["price_paise"]
        )
        unit = spec.get("unit_price_paise", usual)
        override = unit != usual
        if override:
            deviation = abs(unit - usual) * 10000 // max(usual, 1)
            if deviation > PRICE_GUARD_BP and (
                _session(repo).role not in {"owner", "manager"} or not spec.get("reason_key")
            ):
                raise CommandError("counter.price_guard")
        if "amount_paise" in spec:
            if not pack.catalog.loose_sale or item["unit"] not in LOOSE_UNITS or unit <= 0:
                raise CommandError("counter.loose_not_allowed")
            qty, amount = div_round_half_even(spec["amount_paise"] * 1000, unit), spec["amount_paise"]
            if qty <= 0:
                raise CommandError("counter.amount_too_small")
        else:
            qty = spec["qty_milli"]
            amount = line_amount(unit, qty)
        if item["details"].get("rx_required"):
            if not spec.get("rx_seen"):
                raise CommandError("counter.rx_required")
            await repo.insert(
                rx_records,
                {
                    "id": new_id("rx"),
                    "bill_id": bill_id,
                    "item_id": spec["item_id"],
                    "staff_id": _session(repo).actor_id,
                    "occurred_at": iso_utc(clock.now()),
                },
            )
        line_id = new_id("bline")
        await repo.insert(
            bill_lines,
            {
                "id": line_id,
                "bill_id": bill_id,
                "item_id": spec["item_id"],
                "qty_milli": qty,
                "unit_price_paise": unit,
                "amount_paise": amount,
                "modifiers": json.dumps(spec.get("modifier_ids", [])),
                "added_via": spec["added_via"],
                "price_override": int(override),
                "override_reason": spec.get("reason_key"),
                "occurred_at": iso_utc(clock.now()),
            },
        )
        if override:
            await domain_event(
                bus,
                repo,
                "bill.price_override",
                {
                    "bill_id": bill_id,
                    "line_id": line_id,
                    "deviation_bp": abs(unit - usual) * 10000 // max(usual, 1),
                },
            )
        return {"id": line_id, "qty_milli": qty, "amount_paise": amount}

    async def add_lines(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        added = []
        for spec in payload["lines"]:
            line = await priced_line(repo, payload["bill_id"], spec)
            await op(repo, payload["bill_id"], "add", line["id"], None)
            added.append(line)
        await changed(repo, payload["bill_id"])
        return {"bill_id": payload["bill_id"], "lines": added}

    async def active_line(repo: Repository, bill_id: str, line_id: str) -> dict[str, Any]:
        rows = await repo.select(
            bill_lines,
            bill_lines.c.id == line_id,
            bill_lines.c.bill_id == bill_id,
            bill_lines.c.status == "active",
        )
        if not rows:
            raise CommandError("counter.line_not_found")
        return rows[0]

    async def set_qty(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        old = await active_line(repo, payload["bill_id"], payload["line_id"])
        identity = new_id("bline")
        await repo.insert(
            bill_lines,
            {
                **{k: v for k, v in old.items() if k not in {"merchant_id", "id"}},
                "id": identity,
                "qty_milli": payload["qty_milli"],
                "amount_paise": line_amount(old["unit_price_paise"], payload["qty_milli"]),
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await repo.update(bill_lines, {"status": "voided"}, bill_lines.c.id == old["id"])
        await op(repo, payload["bill_id"], "set_qty", identity, old["id"])
        await changed(repo, payload["bill_id"])
        return {"bill_id": payload["bill_id"], "line_id": identity}

    async def remove_line(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        old = await active_line(repo, payload["bill_id"], payload["line_id"])
        await repo.update(bill_lines, {"status": "voided"}, bill_lines.c.id == old["id"])
        await op(repo, payload["bill_id"], "remove", None, old["id"])
        await changed(repo, payload["bill_id"])
        return {"bill_id": payload["bill_id"], "line_id": old["id"]}

    async def undo(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        ops = await repo.select(bill_ops, bill_ops.c.bill_id == payload["bill_id"], bill_ops.c.undone == 0)
        if not ops:
            raise CommandError("counter.nothing_to_undo")
        last = max(ops, key=lambda r: r["seq"])
        if last["line_added"]:
            await repo.update(bill_lines, {"status": "voided"}, bill_lines.c.id == last["line_added"])
        if last["line_voided"]:
            await repo.update(bill_lines, {"status": "active"}, bill_lines.c.id == last["line_voided"])
        await repo.update(bill_ops, {"undone": 1}, bill_ops.c.id == last["id"])
        await changed(repo, payload["bill_id"])
        return {"bill_id": payload["bill_id"], "undone": last["kind"]}

    async def attach(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        await patron_row(repo, payload["patron_id"])
        await repo.update(bills, {"patron_id": payload["patron_id"]}, bills.c.id == payload["bill_id"])
        await changed(repo, payload["bill_id"])
        return payload

    async def park(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        await repo.update(bills, {"status": "parked"}, bills.c.id == payload["bill_id"])
        await changed(repo, payload["bill_id"])
        return {"bill_id": payload["bill_id"], "status": "parked"}

    async def resume(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if (await bill_row(repo, payload["bill_id"]))["status"] != "parked":
            raise CommandError("counter.bill_not_parked")
        await repo.update(bills, {"status": "open"}, bills.c.id == payload["bill_id"])
        await changed(repo, payload["bill_id"])
        return {"bill_id": payload["bill_id"], "status": "open"}

    async def request_upi(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        current = await bill_state(repo, payload["bill_id"])
        if current["due_paise"] <= 0:
            raise CommandError("counter.nothing_due")
        for intent in await repo.select(
            upi_intents, upi_intents.c.bill_id == payload["bill_id"], upi_intents.c.status == "waiting"
        ):
            await repo.update(upi_intents, {"status": "expired"}, upi_intents.c.id == intent["id"])
        order_ref = new_id("ord")
        await repo.insert(
            upi_intents,
            {
                "id": new_id("upi"),
                "bill_id": payload["bill_id"],
                "order_ref": order_ref,
                "amount_paise": current["due_paise"],
                "status": "waiting",
                "created_at": iso_utc(clock.now()),
                "expires_at": iso_utc(clock.now() + UPI_VALIDITY),
            },
        )
        return {"bill_id": payload["bill_id"], "order_ref": order_ref, "amount_paise": current["due_paise"]}

    def tendered(payments: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
        rows, change = [], 0
        for payment in payments:
            given = payment.get("tendered_paise")
            if given is not None and payment["mode"] != "cash":
                raise CommandError("counter.tender_cash_only")
            if given is not None and given < payment["amount_paise"]:
                raise CommandError("counter.tendered_short")
            delta = given - payment["amount_paise"] if given is not None else None
            change += delta or 0
            rows.append(
                {
                    "mode": payment["mode"],
                    "amount_paise": payment["amount_paise"],
                    "tendered_paise": given,
                    "change_paise": delta,
                }
            )
        return rows, change

    async def checkout(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        rows, change = tendered(payload["payments"])
        if payload.get("coupon_code"):
            from arth.domains.offers import redeem_coupon

            rows.append(await redeem_coupon(bus, repo, payload["coupon_code"], payload["bill_id"]))
        result = await close_bill(bus, repo, payload["bill_id"], rows)
        await _record_cash(repo, payload["bill_id"], rows)
        return {**result, "change_paise": change}

    async def _record_cash(repo: Repository, bill_id: str, rows: list[dict[str, Any]]) -> None:
        from arth.domains.treasury import record_counter_payment

        for row in rows:
            if row["mode"] in {"cash", "card"}:
                await record_counter_payment(repo, clock, bill_id, row["mode"], row["amount_paise"])

    async def khata_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        view = await account_view(repo, payload["account_id"], clock)
        row = await bill_row(repo, payload["bill_id"])
        if row["patron_id"] and row["patron_id"] not in await related_ids(repo, view["patron_id"]):
            raise CommandError("counter.account_patron_mismatch")
        if payload.get("member_id") and not await repo.select(
            household_members,
            household_members.c.id == payload["member_id"],
            household_members.c.active == 1,
            household_members.c.patron_id.in_(await related_ids(repo, view["patron_id"])),
        ):
            raise CommandError("ledger.unknown_household_member")
        if view["balance_paise"] + payload["khata_paise"] > view["limit_paise"]:
            if not payload.get("limit_override") or not payload.get("reason_key"):
                raise CommandError("ledger.over_limit")
            owner_only(repo)
        return PolicyContext(sensitive=True, facts={"balance_paise": view["balance_paise"]})

    async def checkout_khata(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await _open_bill(repo, payload["bill_id"])
        await khata_context(repo, payload)
        current = await bill_state(repo, payload["bill_id"])
        rows, change = tendered(payload["payments"])
        entry = new_id("entry")
        full = payload["khata_paise"] == current["total_paise"] and not rows
        await repo.insert(
            credit_entries,
            {
                "id": entry,
                "account_id": payload["account_id"],
                "amount_paise": payload["khata_paise"],
                "source": "counter",
                "ref_id": payload["bill_id"],
                "member_id": payload.get("member_id"),
                "occurred_at": iso_utc(clock.now()),
            },
        )
        lines = (
            [
                {
                    "item_id": line["item_id"],
                    "description_key": None,
                    "qty_milli": line["qty_milli"],
                    "unit_price_paise": line["unit_price_paise"],
                    "amount_paise": line["amount_paise"],
                }
                for line in current["lines"]
            ]
            if full
            else [
                {
                    "item_id": None,
                    "description_key": "ledger.bill_balance",
                    "qty_milli": 1000,
                    "unit_price_paise": payload["khata_paise"],
                    "amount_paise": payload["khata_paise"],
                }
            ]
        )
        if full and sum(line["amount_paise"] for line in lines) != payload["khata_paise"]:
            raise CommandError("ledger.lines_total_mismatch")
        for line in lines:
            await repo.insert(credit_entry_lines, {"id": new_id("line"), "entry_id": entry, **line})
        await repo.update(bills, {"account_id": payload["account_id"]}, bills.c.id == payload["bill_id"])
        rows.append({"mode": "khata", "amount_paise": payload["khata_paise"], "ref_id": entry})
        result = await close_bill(bus, repo, payload["bill_id"], rows)
        await _record_cash(repo, payload["bill_id"], rows)
        await domain_event(bus, repo, "credit.changed", {"account_id": payload["account_id"]})
        return {**result, "entry_id": entry, "change_paise": change, "readback_key": "ledger.entry_readback"}

    async def void(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        _manager(repo)
        row = await bill_row(repo, payload["bill_id"])
        if row["status"] not in {"open", "parked"}:
            raise CommandError("counter.bill_not_open")
        if await repo.select(bill_payments, bill_payments.c.bill_id == payload["bill_id"]):
            raise CommandError("counter.bill_has_payments")
        await repo.update(
            bills, {"status": "voided", "closed_at": iso_utc(clock.now())}, bills.c.id == payload["bill_id"]
        )
        await changed(repo, payload["bill_id"])
        return {"bill_id": payload["bill_id"], "status": "voided"}

    async def return_items(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        _manager(repo)
        row = await bill_row(repo, payload["bill_id"])
        if row["status"] != "closed":
            raise CommandError("counter.bill_not_closed")
        amount, pieces = 0, list[dict[str, Any]]()
        for spec in payload["lines"]:
            lines = await repo.select(
                bill_lines,
                bill_lines.c.id == spec["line_id"],
                bill_lines.c.bill_id == payload["bill_id"],
                bill_lines.c.status == "active",
            )
            if not lines:
                raise CommandError("counter.line_not_found")
            line = lines[0]
            done = sum(
                r["qty_milli"] for r in await repo.select(return_lines, return_lines.c.line_id == line["id"])
            )
            done += sum(p["qty_milli"] for p in pieces if p["line_id"] == line["id"])
            if spec["qty_milli"] > line["qty_milli"] - done:
                raise CommandError("counter.return_exceeds_sold")
            value = div_round_half_even(line["amount_paise"] * spec["qty_milli"], line["qty_milli"])
            pieces.append(
                {
                    "line_id": line["id"],
                    "item_id": line["item_id"],
                    "qty_milli": spec["qty_milli"],
                    "amount_paise": value,
                }
            )
            amount += value
        mode = payload["refund_mode"]
        status = "refund_pending" if mode == "upi" else "completed"
        identity = new_id("return")
        await repo.insert(
            returns,
            {
                "id": identity,
                "bill_id": payload["bill_id"],
                "reason_key": payload["reason_key"],
                "refund_mode": mode,
                "amount_paise": amount,
                "status": status,
                "occurred_at": iso_utc(clock.now()),
            },
        )
        for piece in pieces:
            await repo.insert(return_lines, {"id": new_id("rline"), "return_id": identity, **piece})
            await restock(repo, payload["bill_id"], piece["item_id"], piece["qty_milli"], identity)
        if mode == "cash":
            await repo.insert(
                refunds,
                {
                    "id": new_id("refund"),
                    "bill_id": payload["bill_id"],
                    "amount_paise": amount,
                    "mode": "cash",
                    "reason_key": payload["reason_key"],
                    "staff_id": _session(repo).actor_id,
                    "occurred_at": iso_utc(clock.now()),
                },
            )
        elif mode == "upi":
            pex = new_id("pex")
            await repo.insert(
                payment_exceptions,
                {
                    "id": pex,
                    "kind": "refund_due",
                    "bill_id": payload["bill_id"],
                    "status": "open",
                    "detail": json.dumps({"return_id": identity, "amount_paise": amount}),
                    "opened_at": iso_utc(clock.now()),
                },
            )
            await domain_event(
                bus, repo, "payment.exception.opened", {"exception_id": pex, "kind": "refund_due"}
            )
        else:
            if not row["account_id"]:
                raise CommandError("counter.no_khata_account")
            await credit_back(repo, row, amount, mode, identity)
        await domain_event(
            bus,
            repo,
            "bill.returned",
            {
                "bill_id": payload["bill_id"],
                "return_id": identity,
                "amount_paise": amount,
                "refund_mode": mode,
            },
        )
        return {"return_id": identity, "amount_paise": amount, "status": status}

    async def restock(repo: Repository, bill_id: str, item_id: str, qty: int, ref: str) -> None:
        """Return stock to the batches it was issued from (newest issue first), as new moves."""
        from arth.domains.stock import _move

        issued = sorted(
            await repo.select(
                stock_moves,
                stock_moves.c.ref_id == bill_id,
                stock_moves.c.item_id == item_id,
                stock_moves.c.reason == "stock.issue",
            ),
            key=lambda r: -r["seq"],
        )
        if not issued:
            return
        return_ids = [r["id"] for r in await repo.select(returns, returns.c.bill_id == bill_id)]
        back: dict[Any, int] = {}
        for move in await repo.select(
            stock_moves,
            stock_moves.c.item_id == item_id,
            stock_moves.c.reason == "stock.return",
            stock_moves.c.ref_id.in_(return_ids),
        ):
            back[move["batch_id"]] = back.get(move["batch_id"], 0) + move["delta_qty_milli"]
        for move in issued:
            take = min(-move["delta_qty_milli"] - back.get(move["batch_id"], 0), qty)
            if take > 0:
                await _move(repo, clock, item_id, move["batch_id"], take, "stock.return", ref)
                back[move["batch_id"]] = back.get(move["batch_id"], 0) + take
                qty -= take
        await domain_event(bus, repo, "stock.changed", {"item_id": item_id})

    async def credit_back(repo: Repository, row: dict[str, Any], amount: int, mode: str, ref: str) -> None:
        if mode == "khata":
            view = await account_view(repo, row["account_id"], clock)
            if amount > view["balance_paise"]:
                raise CommandError("counter.refund_exceeds_khata")
            entry = new_id("entry")
            await repo.insert(
                credit_entries,
                {
                    "id": entry,
                    "account_id": row["account_id"],
                    "amount_paise": -amount,
                    "source": "return",
                    "ref_id": ref,
                    "member_id": None,
                    "occurred_at": iso_utc(clock.now()),
                },
            )
            await repo.insert(
                credit_entry_lines,
                {
                    "id": new_id("line"),
                    "entry_id": entry,
                    "item_id": None,
                    "description_key": "ledger.return",
                    "qty_milli": 1000,
                    "unit_price_paise": -amount,
                    "amount_paise": -amount,
                },
            )
        else:
            await repo.insert(
                advances,
                {
                    "id": new_id("advance"),
                    "account_id": row["account_id"],
                    "amount_paise": amount,
                    "source_ref": ref,
                    "purpose_ref": None,
                    "occurred_at": iso_utc(clock.now()),
                },
            )
        await domain_event(bus, repo, "credit.changed", {"account_id": row["account_id"]})

    async def send_to_kitchen(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if not (await _pack(repo, packs)).counter.tickets:
            raise CommandError("counter.tickets_disabled")
        row = await bill_row(repo, payload["bill_id"])
        if row["status"] == "voided":
            raise CommandError("counter.bill_not_open")
        if await repo.select(tickets, tickets.c.bill_id == payload["bill_id"]):
            raise CommandError("counter.ticket_exists")
        day = clock.now_ist().date().isoformat()
        token = len(await repo.select(tickets, tickets.c.day == day)) + 1
        identity, now = new_id("ticket"), iso_utc(clock.now())
        await repo.insert(
            tickets,
            {
                "id": identity,
                "bill_id": payload["bill_id"],
                "token": token,
                "day": day,
                "status": "new",
                "created_at": now,
                "updated_at": now,
            },
        )
        await repo.insert(
            ticket_events,
            {
                "id": new_id("tevt"),
                "ticket_id": identity,
                "from_state": None,
                "to_state": "new",
                "occurred_at": now,
            },
        )
        await domain_event(
            bus,
            repo,
            "bill.ticket_changed",
            {"ticket_id": identity, "bill_id": payload["bill_id"], "token": token, "status": "new"},
        )
        return {"ticket_id": identity, "token": token, "status": "new"}

    async def advance_ticket(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        rows = await repo.select(tickets, tickets.c.id == payload["ticket_id"])
        if not rows:
            raise CommandError("counter.ticket_not_found")
        ticket = rows[0]
        if TICKET_FLOW.get(ticket["status"]) != payload["to"]:
            raise CommandError("counter.illegal_ticket_transition")
        now = iso_utc(clock.now())
        await repo.update(tickets, {"status": payload["to"], "updated_at": now}, tickets.c.id == ticket["id"])
        await repo.insert(
            ticket_events,
            {
                "id": new_id("tevt"),
                "ticket_id": ticket["id"],
                "from_state": ticket["status"],
                "to_state": payload["to"],
                "occurred_at": now,
            },
        )
        await domain_event(
            bus,
            repo,
            "bill.ticket_changed",
            {
                "ticket_id": ticket["id"],
                "bill_id": ticket["bill_id"],
                "token": ticket["token"],
                "status": payload["to"],
            },
        )
        return {"ticket_id": ticket["id"], "token": ticket["token"], "status": payload["to"]}

    async def sensitive(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        return PolicyContext(sensitive=True)

    for kind, handler, context in [
        ("counter.open_bill", open_bill, None),
        ("counter.add_lines", add_lines, None),
        ("counter.set_qty", set_qty, None),
        ("counter.remove_line", remove_line, None),
        ("counter.undo", undo, None),
        ("counter.attach_patron", attach, None),
        ("counter.park", park, None),
        ("counter.resume", resume, None),
        ("counter.request_upi", request_upi, None),
        ("counter.checkout", checkout, None),
        ("counter.checkout_khata", checkout_khata, khata_context),
        ("counter.void_bill", void, None),
        ("counter.return", return_items, sensitive),
        ("counter.send_to_kitchen", send_to_kitchen, None),
        ("counter.advance_ticket", advance_ticket, None),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler, context)


__all__ = ["bill_state", "close_bill", "register_counter", "on_hand"]
