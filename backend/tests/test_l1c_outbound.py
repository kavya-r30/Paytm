from datetime import timedelta

import pytest
from test_l1c_ledger import charge, fixture_ledger
from test_l1c_review import approved

from arth.core.clock import parse_iso
from arth.core.ids import new_id
from arth.domains.ledger import statement
from arth.governance.commands import CommandError
from arth.governance.repository import Repository


async def test_verified_reminder_link_and_statement_payment_reference(db):
    bus, actor, item, patrons, patron, account = await fixture_ledger(db)
    await charge(bus, actor, item, account, 10000, "charge")
    bus.clock.set(bus.clock.now() + timedelta(days=8, hours=2))
    await patrons.record_customer_instruction(actor.merchant_id, patron, "reminders", True, new_id("evt"))
    gate = await bus.submit(
        actor, "ledger.send_reminder", {"account_id": account, "template_key": "reminder.gentle"}, "reminder"
    )
    await bus.decide(actor, gate["thread_id"], "approve", "yes")
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    await bus.run_due(actor.merchant_id)
    async with db.read() as conn:
        from arth.domains.ledger_tables import reminders

        link = (await Repository(conn, actor.merchant_id).select(reminders))[0]["link_id"]
    payload = {
        "account_id": account,
        "amount_paise": 4000,
        "payment_ref": new_id("payment"),
        "link_ref": link,
    }
    with pytest.raises(CommandError, match="verified"):
        await bus.submit(actor, "ledger.apply_verified_payment", payload, "forged")
    result = await bus.submit(
        patrons._system(actor.merchant_id),
        "ledger.apply_verified_payment",
        payload,
        "verified",
        private={"payment_verified": True},
    )
    assert result["data"]["balance_paise"] == 6000
    with pytest.raises(CommandError, match="consent"):
        await bus.submit(actor, "ledger.send_statement", {"account_id": account}, "no-statement-consent")
    await patrons.record_customer_instruction(actor.merchant_id, patron, "receipts", True, new_id("evt"))
    gate = await bus.submit(actor, "ledger.send_statement", {"account_id": account}, "statement")
    await bus.decide(actor, gate["thread_id"], "approve", "yes-statement")
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    await bus.run_due(actor.merchant_id)
    async with db.read() as conn:
        report = await statement(Repository(conn, actor.merchant_id), account, bus.clock)
        assert report["pay_link_ref"].startswith("link_")


async def test_promise_cutoff_uses_ist_and_freezes_reminder(db):
    from arth.domains.ledger_projection import promise_status
    from arth.domains.ledger_tables import promises

    bus, actor, item, patrons, patron, account = await fixture_ledger(db)
    await charge(bus, actor, item, account, 10000, "charge")
    bus.clock.set(bus.clock.now() + timedelta(days=8, hours=2))
    await patrons.record_customer_instruction(actor.merchant_id, patron, "reminders", True, new_id("evt"))
    due = bus.clock.now_ist().date().isoformat()
    await bus.submit(
        actor,
        "ledger.record_promise",
        {"account_id": account, "amount_paise": 10000, "due_on": due},
        "promise",
    )
    with pytest.raises(CommandError, match="promise_active"):
        await bus.submit(
            actor,
            "ledger.send_reminder",
            {"account_id": account, "template_key": "reminder.gentle"},
            "promised",
        )
    bus.clock.set(parse_iso(due + "T19:00:00Z"))  # Next IST day: this payment is late.
    await approved(
        bus,
        actor,
        "ledger.record_payment",
        {"account_id": account, "amount_paise": 10000, "payment_ref": new_id("payment"), "mode": "cash"},
        "paid-late",
    )
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        row = (await repo.select(promises))[0]
        assert await promise_status(repo, row, bus.clock) == "broken"
