import pytest


async def test_consumer_failure_retries_without_duplicate_effect(db):
    from arth.core.clock import SimClock
    from arth.core.config import Settings
    from arth.governance.events import Dispatcher, emit_event
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import merchant_settings

    clock = SimClock(Settings(_env_file=None).clock_start)
    dispatcher = Dispatcher(db, clock)
    async with db.write() as conn:
        await emit_event(
            Repository(conn, "a"),
            clock,
            Session("a", "o", "owner"),
            "command.executed",
            "cmd_x",
            {"command_id": "cmd_x"},
        )

    async def broken(repo, event):
        await repo.insert(merchant_settings, {"settings": "{}"})
        raise RuntimeError("retry")

    dispatcher.on("consumer", broken)
    with pytest.raises(RuntimeError):
        await dispatcher.dispatch("a")

    async def working(repo, event):
        await repo.insert(merchant_settings, {"settings": "{}"})

    dispatcher.on("consumer", working)
    await dispatcher.dispatch("a")
    await dispatcher.dispatch("a")
    async with db.read() as conn:
        assert len(await Repository(conn, "a").select(merchant_settings)) == 1
    restarted = Dispatcher(db, clock)
    restarted.on("consumer", working)
    await restarted.dispatch("a")
