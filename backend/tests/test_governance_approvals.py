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
