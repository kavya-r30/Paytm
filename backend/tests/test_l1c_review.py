"""Spec-first review regressions: replay, immutable money and approval safety."""

import asyncio
from datetime import timedelta

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from test_l1c_ledger import charge, fixture_ledger

from arth.core.ids import new_id
from arth.domains.ledger import account_view, statement
from arth.domains.ledger_tables import advances, credit_accounts, credit_entries, reminders
from arth.governance.commands import CommandError
from arth.governance.repository import Repository
from arth.governance.tables import approvals, commands


async def approved(bus, actor, kind, payload, key):
    gate = await bus.submit(actor, kind, payload, key)
    return await bus.decide(actor, gate["thread_id"], "approve", "approve-" + key)


async def test_payment_ref_is_atomic_and_deposit_cannot_be_received_twice(db):
    bus, actor, item, _, _, account = await fixture_ledger(db)
    await charge(bus, actor, item, account, 10000, "charge")
    ref = new_id("payment")
    payload = {"account_id": account, "amount_paise": 6000, "payment_ref": ref, "mode": "cash"}
    gates = await asyncio.gather(
        *(bus.submit(actor, "ledger.record_payment", payload, k) for k in ["one", "two"])
    )
    results = await asyncio.gather(*(bus.decide(actor, g["thread_id"], "approve", "yes") for g in gates))
    assert results[0]["data"] == results[1]["data"]
    deposit_ref = new_id("payment")
    await approved(
        bus,
        actor,
        "ledger.record_deposit",
        {"account_id": account, "amount_paise": 2000, "payment_ref": deposit_ref},
        "deposit",
    )
    with pytest.raises(CommandError, match="payment_ref_conflict"):
        await approved(
            bus, actor, "ledger.record_payment", {**payload, "payment_ref": deposit_ref}, "duplicate-deposit"
        )
    async with db.read() as conn:
        view = await account_view(Repository(conn, actor.merchant_id), account, bus.clock)
        assert (view["balance_paise"], view["advance_paise"]) == (4000, 2000)


async def test_advances_disputes_promises_reversals_lines_and_payables(db):
    bus, actor, item, _, _, account = await fixture_ledger(db)
    entry = (await charge(bus, actor, item, account, 10000, "charge"))["data"]["entry_id"]
    await bus.submit(actor, "ledger.dispute_entry", {"entry_id": entry}, "dispute")
    with pytest.raises(CommandError, match="dispute"):
        await approved(
            bus, actor, "ledger.set_limit", {"account_id": account, "limit_paise": 600000}, "raise"
        )
    await approved(bus, actor, "ledger.resolve_dispute", {"entry_id": entry}, "resolve")
    await approved(
        bus,
        actor,
        "ledger.record_deposit",
        {"account_id": account, "amount_paise": 4000, "payment_ref": new_id("payment")},
        "deposit",
    )
    await approved(bus, actor, "ledger.apply_advance", {"account_id": account, "amount_paise": 3000}, "apply")
    with pytest.raises(CommandError, match="requires_refund"):
        await approved(
            bus,
            actor,
            "ledger.reverse_entry",
            {"entry_id": entry, "reason_key": "ledger.correction"},
            "reverse-paid",
        )
    unallocated = (await charge(bus, actor, item, account, 2000, "other"))["data"]["entry_id"]
    await approved(
        bus,
        actor,
        "ledger.reverse_entry",
        {"entry_id": unallocated, "reason_key": "ledger.correction"},
        "reverse",
    )
    tomorrow = (bus.clock.now_ist().date() + timedelta(days=1)).isoformat()
    await bus.submit(
        actor,
        "ledger.record_promise",
        {"account_id": account, "amount_paise": 5000, "due_on": tomorrow},
        "promise",
    )
    bus.clock.set(bus.clock.now() + timedelta(days=3))
    with pytest.raises(CommandError, match="broken_promise"):
        await approved(
            bus, actor, "ledger.set_limit", {"account_id": account, "limit_paise": 600000}, "raise-again"
        )
    payable = (
        await approved(
            bus,
            actor,
            "ledger.add_payable",
            {
                "supplier_ref": new_id("supplier"),
                "source_ref": new_id("grn"),
                "amount_paise": 8000,
                "due_on": tomorrow,
            },
            "payable",
        )
    )["data"]["payable_id"]
    payment = {"payable_id": payable, "amount_paise": 8000, "payment_ref": new_id("payment")}
    await approved(bus, actor, "ledger.pay_payable", payment, "pay-supplier")
    await approved(bus, actor, "ledger.pay_payable", payment, "same-supplier-ref")
    with pytest.raises(CommandError, match="overpayment"):
        await approved(
            bus, actor, "ledger.pay_payable", {**payment, "payment_ref": new_id("payment")}, "overpay"
        )
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        report = await statement(repo, account, bus.clock)
        assert (report["balance_paise"], report["advance_paise"]) == (7000, 1000)
        assert all(
            sum(line["amount_paise"] for line in r["lines"]) == r["amount_paise"] for r in report["entries"]
        )
        assert await repo.select(credit_accounts) and await repo.select(advances)
        with pytest.raises(CommandError, match="not_found"):
            await statement(Repository(conn, "another"), account, bus.clock)


async def test_reminder_scope_binds_balance_and_expired_queue_never_executes(db):
    bus, actor, item, patrons, patron, account = await fixture_ledger(db)
    await charge(bus, actor, item, account, 10000, "entry")
    bus.clock.set(bus.clock.now() + timedelta(days=8, hours=2))
    await patrons.record_customer_instruction(actor.merchant_id, patron, "reminders", True, new_id("evt"))
    gate = await bus.submit(
        actor, "ledger.send_reminder", {"account_id": account, "template_key": "reminder.gentle"}, "reminder"
    )
    assert gate["scope"]["conditions"]["balance_paise"] == {"lte": 10000}
    await bus.decide(actor, gate["thread_id"], "approve", "yes")
    # Import is permitted for historical opening entries; a larger debt invalidates the approved amount.
    await approved(
        bus,
        actor,
        "ledger.add_entry",
        {
            "account_id": account,
            "amount_paise": 2000,
            "source": "import",
            "occurred_at": "2026-10-28T04:00:00Z",
            "lines": [{"item_id": item, "qty_milli": 1000, "unit_price_paise": 2000}],
        },
        "historical",
    )
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due(actor.merchant_id) == 0
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        rows = await repo.select(commands, commands.c.id == gate["command_id"])
        import json

        fresh = json.loads(rows[0]["result"])
        assert fresh["status"] == "needs_approval" and fresh["gate_id"] != gate["gate_id"]
        assert not await repo.select(reminders)
    await bus.decide(actor, fresh["thread_id"], "approve", "yes-fresh")
    bus.clock.set(bus.clock.now() + timedelta(days=1))
    assert await bus.run_due(actor.merchant_id) == 0
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        assert not await repo.select(reminders)
        gates = await repo.select(approvals, approvals.c.id == fresh["gate_id"])
        assert gates[0]["status"] == "expired"


@settings(max_examples=8, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    st.lists(st.integers(min_value=1, max_value=10000), min_size=1, max_size=4),
    st.integers(min_value=1, max_value=50000),
)
async def test_payment_conservation_property(db, amounts, payment):
    bus, actor, item, _, _, account = await fixture_ledger(db)
    for n, amount in enumerate(amounts):
        await charge(bus, actor, item, account, amount, "charge-" + str(n))
    await approved(
        bus,
        actor,
        "ledger.record_payment",
        {"account_id": account, "amount_paise": payment, "payment_ref": new_id("payment"), "mode": "cash"},
        "pay",
    )
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        report = await statement(repo, account, bus.clock)
        assert report["balance_paise"] == max(sum(amounts) - payment, 0)
        assert report["advance_paise"] == max(payment - sum(amounts), 0)
        assert report["allocated_paise"] + report["advance_paise"] == payment
        assert sum(r["amount_paise"] for r in await repo.select(credit_entries)) == sum(amounts)
