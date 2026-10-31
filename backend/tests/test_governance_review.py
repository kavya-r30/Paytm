from datetime import timedelta

import pytest
from conftest import seed_repo
from test_governance_commands import make_bus


async def test_discreet_decision_reaches_envelope(db):
    from arth.governance.policy import PolicyContext, Session

    bus = await make_bus(db)
    bus.clock.set(bus.clock.now() + timedelta(hours=2))
    schema, handler, _ = bus.registry["test.write"]

    async def context(repo, payload):
        return PolicyContext(sensitive=True)

    bus.register("test.write", schema.schema, handler, context)
    result = await bus.submit(Session("a", "o", "owner"), "test.write", {}, "one")
    assert result["envelope"]["sensitivity"] == "discreet"


async def test_queue_can_be_cancelled_before_send(db):
    from arth.governance.policy import Session

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one")
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    assert (await bus.decide(owner, gate["thread_id"], "snooze", "cancel"))["status"] == "snoozed"
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 0


async def test_manager_can_tap_r2_but_cannot_voice_approve(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db, "R2")
    manager = Session("a", "m", "manager", device_id="manager-device")
    gate = await bus.submit(manager, "test.write", {}, "one")
    with pytest.raises(CommandError):
        await bus.decide(
            Session("a", "m", "manager", channel="voice", device_id="manager-device", owner_ptt=True),
            gate["thread_id"],
            "approve",
            "voice",
        )
    assert (await bus.decide(manager, gate["thread_id"], "approve", "tap"))["status"] == "executed"


async def test_pack_policy_is_used_by_bus(db):
    from arth.core.packs import PackRegistry
    from arth.governance.commands import CommandError
    from arth.governance.policy import PolicyContext, Session
    from arth.governance.tables import merchants

    bus = await make_bus(db)
    policies = bus.policy.policies.model_copy(deep=True)
    policies.growth.margin_floor = 0.25
    bus.packs = PackRegistry({}, {"cafe": policies})
    # Registry resolves a real manifest as well as merged policies.
    from arth.core.paths import PACKS_DIR

    base = PackRegistry.load(PACKS_DIR, bus.policy.policies).get("kirana")
    bus.packs = PackRegistry({"cafe": base.model_copy(update={"pack": "cafe"})}, {"cafe": policies})
    async with db.write() as conn:
        await seed_repo(conn, "a").insert(merchants, {"id": "a", "name": "Cafe", "pack": "cafe"})
    schema, handler, _ = bus.registry["test.write"]

    async def context(repo, payload):
        return PolicyContext(margin=0.2)

    bus.register("test.write", schema.schema, handler, context)
    with pytest.raises(CommandError, match="margin_floor"):
        await bus.submit(Session("a", "o", "owner"), "test.write", {}, "one")
