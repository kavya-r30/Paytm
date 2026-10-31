from datetime import timedelta

import pytest
from test_governance_commands import make_bus


async def test_owner_binding_scope_change_and_send_queue(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db, "R3")
    owner = Session("a", "owner", "owner", channel="voice", device_id="device-a", owner_ptt=True)
    gate = await bus.submit(owner, "test.write", {}, "one")
    assert gate["status"] == "needs_approval"
    from arth.core.schemas import validator

    validator("envelope").validate(gate["envelope"])
    assert gate["scope"] == {"type": "test.write", "payload": {}, "conditions": {}}
    with pytest.raises(CommandError, match="approve"):
        await bus.decide(
            Session("a", "helper", "helper", channel="voice", owner_ptt=True),
            gate["thread_id"],
            "approve",
            "decision1",
        )
    with pytest.raises(CommandError, match="approve"):
        await bus.decide(
            Session("a", "owner", "owner", channel="voice"), gate["thread_id"], "approve", "decision2"
        )
    queued = await bus.decide(owner, gate["thread_id"], "approve", "decision3")
    assert queued["status"] == "queued"
    assert await bus.run_due("a") == 0
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 1
    assert (await bus.submit(owner, "test.write", {}, "one"))["status"] == "executed"
    assert (await bus.submit(owner, "test.write", {"fail": False}, "changed"))["status"] == "needs_approval"


async def test_expired_gate_cannot_be_approved(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db, "R2")
    owner = Session("a", "o", "owner", device_id="device-a", owner_ptt=True)
    gate = await bus.submit(owner, "test.write", {}, "one")
    bus.clock.set(bus.clock.now() + timedelta(hours=12))
    with pytest.raises(CommandError, match="expired"):
        await bus.decide(owner, gate["thread_id"], "approve", "decision")


async def test_decline_closes_the_gate_without_running_the_command(db):
    from l1d_helpers import run, shop

    from arth.governance.commands import CommandError

    s = await shop(db)
    gate = await run(
        s,
        "ledger.open_account",
        {
            "patron_id": (
                await s.services.patrons.submit(
                    s.owner, "patrons.add", {"display_name": "Decline Me", "lang": "hi"}, "decline-patron"
                )
            )["data"]["patron_id"],
            "limit_paise": 1000,
        },
    )
    result = await s.bus.decide(s.owner, gate["thread_id"], "decline", "decline-1")
    assert result["status"] == "declined"
    with pytest.raises(CommandError, match="approval.already_decided"):
        await s.bus.decide(s.owner, gate["thread_id"], "approve", "approve-after-decline")
