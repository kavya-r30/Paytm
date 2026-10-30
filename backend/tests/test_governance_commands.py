import asyncio

import pytest

from arth.core.clock import SimClock
from arth.core.config import Settings, load_policies
from arth.core.paths import CONFIG_DIR


async def make_bus(db, tier="R1"):
    from arth.governance.commands import CommandBus
    from arth.governance.policy import PolicyEngine
    from arth.governance.tables import merchant_settings

    clock = SimClock(Settings(_env_file=None).clock_start)
    policies = load_policies(CONFIG_DIR / "policies.yaml").model_copy(deep=True)
    policies.tiers["test.write"] = tier
    bus = CommandBus(db, clock, PolicyEngine(policies, clock))

    async def handler(repo, payload):
        await repo.insert(merchant_settings, {"settings": '{"changed":true}'})
        if payload.get("fail"):
            raise RuntimeError("abort")
        return {"saved": True}

    bus.register(
        "test.write",
        {"type": "object", "properties": {"fail": {"type": "boolean"}}, "additionalProperties": False},
        handler,
    )
    return bus


async def test_command_replay_concurrency_conflict_and_atomic_rollback(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log, commands, merchant_settings, outbox

    bus = await make_bus(db)
    session = Session("a", "owner-a", "owner")
    a, b = await asyncio.gather(
        bus.submit(session, "test.write", {}, "same"), bus.submit(session, "test.write", {}, "same")
    )
    assert a == b and a["status"] == "executed"
    from arth.core.schemas import validator

    validator("envelope").validate(a["envelope"])
    with pytest.raises(CommandError, match="idempotency"):
        await bus.submit(session, "test.write", {"fail": False}, "same")
    with pytest.raises(RuntimeError, match="abort"):
        await bus.submit(Session("b", "owner-b", "owner"), "test.write", {"fail": True}, "bad")
    async with db.read() as conn:
        repo = Repository(conn, "a")
        assert len(await repo.select(merchant_settings)) == 1
        assert len(await repo.select(commands)) == 1
        assert len(await repo.select(audit_log)) == 1
        assert len(await repo.select(outbox)) == 1
        assert await Repository(conn, "b").select(commands) == []


async def test_unknown_and_invalid_commands_fail_before_writes(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db)
    for kind, payload in [("unknown.command", {}), ("test.write", {"merchant_id": "b"})]:
        with pytest.raises(CommandError):
            await bus.submit(Session("a", "o", "owner"), kind, payload, "key")
