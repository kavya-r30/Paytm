from datetime import timedelta

import pytest
from l1c_helpers import fixture_shop

from arth.core.ids import new_id


async def fixture_ledger(db):
    from arth.domains.ledger import register_ledger
    from arth.domains.patrons import PatronService

    bus, actor, item = await fixture_shop(db)
    patrons = PatronService(bus, "synthetic-patron-proof-key")
    patron = (
        await patrons.submit(actor, "patrons.add", {"display_name": "Customer", "lang": "hi"}, "patron")
    )["data"]["patron_id"]
    register_ledger(bus)
    gate = await bus.submit(
        actor, "ledger.open_account", {"patron_id": patron, "limit_paise": 500000}, "account"
    )
    account = (await bus.decide(actor, gate["thread_id"], "approve", "open"))["data"]["account_id"]
    return bus, actor, item, patrons, patron, account


async def charge(bus, actor, item, account, amount, key):
    payload = {
        "account_id": account,
        "amount_paise": amount,
        "source": "voice",
        "lines": [{"item_id": item, "qty_milli": 1000, "unit_price_paise": amount}],
    }
    gate = await bus.submit(actor, "ledger.add_entry", payload, key)
    return await bus.decide(actor, gate["thread_id"], "approve", "approve-" + key)


async def test_oldest_first_allocation_advances_statements_and_no_accrual(db):
    from arth.domains.ledger import account_view, statement
    from arth.governance.repository import Repository

    bus, actor, item, patrons, patron, account = await fixture_ledger(db)
    first = (await charge(bus, actor, item, account, 70000, "first"))["data"]["entry_id"]
    second = (await charge(bus, actor, item, account, 45000, "second"))["data"]["entry_id"]
    payment = new_id("payment")
    gate = await bus.submit(
        actor,
        "ledger.record_payment",
        {"account_id": account, "amount_paise": 100000, "payment_ref": payment, "mode": "cash"},
        "payment",
    )
    result = await bus.decide(actor, gate["thread_id"], "approve", "paid")
    assert result["data"]["allocations"] == [
        {"entry_id": first, "amount_paise": 70000},
        {"entry_id": second, "amount_paise": 30000},
    ]
    await charge(bus, actor, item, account, 45000, "third")
    async with db.read() as conn:
        view = await account_view(Repository(conn, actor.merchant_id), account, bus.clock)
        assert view["balance_paise"] == 60000
        report = await statement(Repository(conn, actor.merchant_id), account, bus.clock)
        assert report["entries_paise"] - report["allocated_paise"] == report["balance_paise"] == 60000
    gate = await bus.submit(
        actor,
        "ledger.record_payment",
        {"account_id": account, "amount_paise": 70000, "payment_ref": new_id("payment"), "mode": "cash"},
        "extra",
    )
    await bus.decide(actor, gate["thread_id"], "approve", "extra-paid")
    bus.clock.set(bus.clock.now() + timedelta(days=730))
    async with db.read() as conn:
        view = await account_view(Repository(conn, actor.merchant_id), account, bus.clock)
        assert view["balance_paise"] == 0 and view["advance_paise"] == 10000


async def test_limits_lines_households_and_reminder_consent(db):
    from arth.governance.commands import CommandError

    bus, actor, item, patrons, patron, account = await fixture_ledger(db)
    payload = {
        "account_id": account,
        "amount_paise": 600000,
        "source": "voice",
        "lines": [{"item_id": item, "qty_milli": 1000, "unit_price_paise": 600000}],
    }
    with pytest.raises(CommandError, match="over_limit"):
        await bus.submit(actor, "ledger.add_entry", payload, "over")
    with pytest.raises(CommandError):
        await bus.submit(actor, "ledger.add_entry", {**payload, "interest_rate": 10}, "interest")
    await charge(bus, actor, item, account, 45000, "entry")
    bus.clock.set(bus.clock.now() + timedelta(days=8, hours=2))
    with pytest.raises(CommandError, match="consent"):
        await bus.submit(
            actor,
            "ledger.send_reminder",
            {"account_id": account, "template_key": "reminder.gentle"},
            "no-consent",
        )
    await patrons.record_customer_instruction(actor.merchant_id, patron, "reminders", True, new_id("evt"))
    gate = await bus.submit(
        actor, "ledger.send_reminder", {"account_id": account, "template_key": "reminder.gentle"}, "reminder"
    )
    assert gate["status"] == "needs_approval"
    await bus.decide(actor, gate["thread_id"], "approve", "yes-reminder")
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due(actor.merchant_id) == 1
    with pytest.raises(CommandError, match="contact_cap"):
        await bus.submit(
            actor, "ledger.send_reminder", {"account_id": account, "template_key": "reminder.gentle"}, "again"
        )
