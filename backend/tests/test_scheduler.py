import asyncio
import logging
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select, update

from arth.core.clock import IST, ClockError, SimClock, parse_iso
from arth.core.db import Database
from arth.core.scheduler import Job, Scheduler, tick_loop
from arth.core.tables import jobs

START = datetime(2026, 10, 29, 7, 45, tzinfo=IST)


async def test_jumping_eight_days_runs_eight_nightly_jobs_in_order(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    seen: list[datetime] = []

    async def night_shift(job: Job) -> None:
        seen.append(clock.now_ist())

    scheduler.on("night_shift", night_shift)
    await scheduler.schedule_daily("night_shift", "22:00")
    ran = await scheduler.advance_to(START + timedelta(days=8))

    assert ran == 8
    assert [(d.day, d.hour, d.minute) for d in seen] == [
        (29, 22, 0),
        (30, 22, 0),
        (31, 22, 0),
        (1, 22, 0),
        (2, 22, 0),
        (3, 22, 0),
        (4, 22, 0),
        (5, 22, 0),
    ]
    assert clock.now() == (START + timedelta(days=8)).astimezone(clock.now().tzinfo)


async def test_jobs_run_in_due_order_across_names(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    order: list[str] = []

    async def record(job: Job) -> None:
        order.append(job.payload["tag"])

    scheduler.on("a", record)
    scheduler.on("b", record)
    await scheduler.schedule("b", START + timedelta(hours=2), {"tag": "second"})
    await scheduler.schedule("a", START + timedelta(hours=1), {"tag": "first"})
    await scheduler.advance_to(START + timedelta(hours=3))
    assert order == ["first", "second"]


async def test_failed_job_is_marked_and_does_not_stop_others(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    done: list[str] = []

    async def boom(job: Job) -> None:
        raise RuntimeError("boom")

    async def ok(job: Job) -> None:
        done.append("ok")

    scheduler.on("boom", boom)
    scheduler.on("ok", ok)
    await scheduler.schedule("boom", START + timedelta(minutes=1))
    await scheduler.schedule("ok", START + timedelta(minutes=2))
    await scheduler.advance_to(START + timedelta(minutes=5))
    assert done == ["ok"]
    assert await scheduler.count(status="failed") == 1


async def test_tick_loop_runs_due_jobs_while_clock_runs(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    fired = asyncio.Event()

    async def handler(job: Job) -> None:
        fired.set()

    scheduler.on("soon", handler)
    await scheduler.schedule("soon", START + timedelta(minutes=1))
    clock.run(rate=3600.0)
    stop = asyncio.Event()
    task = asyncio.create_task(tick_loop(scheduler, stop, interval_s=0.01))
    await asyncio.wait_for(fired.wait(), timeout=2)
    stop.set()
    await task


async def test_eight_nights_record_each_ran_at(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)

    async def noop(job: Job) -> None:
        return None

    scheduler.on("night_shift", noop)
    await scheduler.schedule_daily("night_shift", "22:00")
    await scheduler.advance_to(START + timedelta(days=8))
    async with db.read() as conn:
        rows = (
            await conn.execute(select(jobs.c.ran_at).where(jobs.c.status == "done").order_by(jobs.c.ran_at))
        ).all()
    ran_at = [parse_iso(r[0]).astimezone(IST) for r in rows]
    assert [(d.day, d.hour, d.minute) for d in ran_at] == [(d, 22, 0) for d in (29, 30, 31, 1, 2, 3, 4, 5)]


async def test_concurrent_run_due_and_advance_run_job_once(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    calls: list[str] = []

    async def slow(job: Job) -> None:
        calls.append(job.id)
        await asyncio.sleep(0.05)

    scheduler.on("night_shift", slow)
    await scheduler.schedule_daily("night_shift", "22:00")
    due = START.replace(hour=22, minute=0)
    clock.set(due)
    await asyncio.gather(scheduler.run_due(), scheduler.advance_to(due + timedelta(hours=1)))
    assert len(calls) == 1
    assert await scheduler.count(status="done") == 1
    assert await scheduler.count(status="pending") == 1


async def test_recover_resets_running_jobs_to_pending(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    job_id = await scheduler.schedule("x", START)
    async with db.write() as conn:
        await conn.execute(update(jobs).where(jobs.c.id == job_id).values(status="running"))
    assert await scheduler.recover() == 1
    assert await scheduler.count(status="pending") == 1
    assert await scheduler.count(status="running") == 0


async def test_done_and_successor_commit_together(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)

    async def noop(job: Job) -> None:
        return None

    scheduler.on("n", noop)
    await scheduler.schedule_daily("n", "22:00")
    await scheduler.advance_to(START + timedelta(hours=15))
    assert await scheduler.count(status="done") == 1
    assert await scheduler.count(status="pending") == 1


async def test_advance_to_on_running_clock_does_not_go_backwards(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)

    async def slow(job: Job) -> None:
        await asyncio.sleep(0.05)

    scheduler.on("j", slow)
    await scheduler.schedule("j", START + timedelta(seconds=1))
    clock.run(rate=10_000.0)
    assert clock.running
    assert await scheduler.advance_to(START + timedelta(seconds=2)) == 1
    assert clock.now() >= START + timedelta(seconds=2)


async def test_tick_loop_survives_run_due_error(db: Database, monkeypatch: pytest.MonkeyPatch) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    fired = asyncio.Event()

    async def handler(job: Job) -> None:
        fired.set()

    scheduler.on("soon", handler)
    await scheduler.schedule("soon", START)
    real = scheduler._claim_next
    state = {"calls": 0}

    async def flaky(until: datetime) -> Job | None:
        state["calls"] += 1
        if state["calls"] == 1:
            raise RuntimeError("db hiccup")
        return await real(until)

    monkeypatch.setattr(scheduler, "_claim_next", flaky)
    stop = asyncio.Event()
    task = asyncio.create_task(tick_loop(scheduler, stop, interval_s=0.01))
    await asyncio.wait_for(fired.wait(), timeout=2)
    stop.set()
    await task


def test_every_seconds_must_be_positive(db: Database) -> None:
    scheduler = Scheduler(db, SimClock(START))
    for bad in (0, -5):
        with pytest.raises(ValueError):
            asyncio.run(scheduler.schedule("x", START, every_seconds=bad))


async def test_same_instant_jobs_run_in_insertion_order(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    order: list[str] = []

    async def record(job: Job) -> None:
        order.append(job.payload["tag"])

    scheduler.on("t", record)
    tags = [f"t{i}" for i in range(10)]
    for tag in tags:
        await scheduler.schedule("t", START + timedelta(minutes=1), {"tag": tag})
    await scheduler.advance_to(START + timedelta(minutes=2))
    assert order == tags


async def test_unhandled_job_stays_pending_and_warns_once(
    db: Database, caplog: pytest.LogCaptureFixture
) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    await scheduler.schedule("ghost", START + timedelta(minutes=1))
    with caplog.at_level(logging.WARNING, logger="arth.core.scheduler"):
        await scheduler.advance_to(START + timedelta(minutes=5))
        await scheduler.run_due()
    assert await scheduler.count(status="pending") == 1
    assert await scheduler.count(status="failed") == 0
    assert len([r for r in caplog.records if "ghost" in r.getMessage()]) == 1


async def test_interval_job_reschedules_from_due_time(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    runs: list[datetime] = []

    async def tick(job: Job) -> None:
        runs.append(job.due_at)

    scheduler.on("poll", tick)
    await scheduler.schedule("poll", START + timedelta(hours=1), every_seconds=3600)
    assert await scheduler.advance_to(START + timedelta(hours=3, minutes=30)) == 3
    assert runs == [(START + timedelta(hours=h)).astimezone(runs[0].tzinfo) for h in (1, 2, 3)]
    assert await scheduler.count(status="pending") == 1


async def test_job_scheduled_by_handler_inside_window_runs_in_same_advance(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    order: list[str] = []

    async def first(job: Job) -> None:
        order.append("first")
        await scheduler.schedule("second", clock.now() + timedelta(minutes=10))

    async def second(job: Job) -> None:
        order.append("second")

    scheduler.on("first", first)
    scheduler.on("second", second)
    await scheduler.schedule("first", START + timedelta(minutes=5))
    assert await scheduler.advance_to(START + timedelta(hours=1)) == 2
    assert order == ["first", "second"]


async def test_advance_backwards_raises(db: Database) -> None:
    scheduler = Scheduler(db, SimClock(START))
    with pytest.raises(ClockError):
        await scheduler.advance_to(START - timedelta(minutes=1))
