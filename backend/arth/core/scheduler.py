"""Jobs on sim time. Jumping the clock runs every due job in order (spec v5.1 D6)."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import Insert, func, insert, select, text, update

from arth.core.clock import ClockError, SimClock, iso_utc, next_daily, parse_iso
from arth.core.db import Database
from arth.core.ids import new_id
from arth.core.tables import jobs

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Job:
    id: str
    name: str
    due_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
    every_seconds: int | None = None
    daily_at: str | None = None


Handler = Callable[[Job], Awaitable[None]]


class Scheduler:
    """Persistent job scheduler on sim time.

    Execution is serialised by an internal lock and each job is claimed atomically
    (pending -> running), so concurrent `run_due`/`advance_to` calls never run a job twice.
    Call `await recover()` once at startup (API lifespan) before `tick_loop` starts.
    Handlers must not call `run_due()`/`advance_to()` (the run lock is not reentrant: deadlock);
    scheduling new jobs from a handler is fine.
    """

    def __init__(self, db: Database, clock: SimClock) -> None:
        self.db = db
        self.clock = clock
        self._handlers: dict[str, Handler] = {}
        self._run_lock = asyncio.Lock()
        self._warned_unhandled: set[str] = set()

    def on(self, name: str, handler: Handler) -> None:
        """Register `handler` for jobs called `name`.

        Delivery is at-least-once: handlers MUST be idempotent. If the process dies while a
        handler runs, the job stays `running` and is re-run after `recover()`.
        """
        self._handlers[name] = handler

    async def recover(self) -> int:
        """Startup recovery: jobs left `running` by a crash go back to `pending`."""
        async with self.db.write() as conn:
            result = await conn.execute(
                update(jobs).where(jobs.c.status == "running").values(status="pending")
            )
            return int(result.rowcount)  # type: ignore[attr-defined]

    async def schedule(
        self,
        name: str,
        due_at: datetime,
        payload: dict[str, Any] | None = None,
        *,
        every_seconds: int | None = None,
        daily_at: str | None = None,
    ) -> str:
        if every_seconds is not None and every_seconds <= 0:
            raise ValueError("every_seconds must be > 0")
        job_id = new_id("job")
        async with self.db.write() as conn:
            await conn.execute(self._insert(job_id, name, due_at, payload or {}, every_seconds, daily_at))
        return job_id

    @staticmethod
    def _insert(
        job_id: str,
        name: str,
        due_at: datetime,
        payload: dict[str, Any],
        every_seconds: int | None,
        daily_at: str | None,
    ) -> Insert:
        return insert(jobs).values(
            id=job_id,
            name=name,
            due_at=iso_utc(due_at),
            payload=json.dumps(payload, sort_keys=True),
            every_seconds=every_seconds,
            daily_at=daily_at,
        )

    async def schedule_daily(self, name: str, at_ist: str, payload: dict[str, Any] | None = None) -> str:
        return await self.schedule(name, next_daily(self.clock.now(), at_ist), payload, daily_at=at_ist)

    async def count(self, *, status: str) -> int:
        async with self.db.read() as conn:
            result = await conn.execute(select(func.count()).select_from(jobs).where(jobs.c.status == status))
            return int(result.scalar_one())

    async def run_due(self) -> int:
        async with self._run_lock:
            ran = 0
            while (job := await self._claim_next(self.clock.now())) is not None:
                await self._run(job)
                ran += 1
            return ran

    async def advance_to(self, target: datetime) -> int:
        if target < self.clock.now():
            raise ClockError("advance_to cannot go backwards")
        async with self._run_lock:
            ran = 0
            while (job := await self._claim_next(target)) is not None:
                if job.due_at > self.clock.now():
                    self.clock.set(job.due_at)
                await self._run(job)
                ran += 1
            if target > self.clock.now():  # a running clock may already be past target
                self.clock.set(target)
            return ran

    async def _claim_next(self, until: datetime) -> Job | None:
        """Atomically move the earliest due, handled job pending -> running; None if there is none."""
        names = list(self._handlers)
        await self._warn_unhandled(until, names)
        while True:
            async with self.db.write() as conn:
                row = (
                    (
                        await conn.execute(
                            select(jobs)
                            .where(
                                jobs.c.status == "pending",
                                jobs.c.due_at <= iso_utc(until),
                                jobs.c.name.in_(names),
                            )
                            .order_by(jobs.c.due_at, text("rowid"))
                            .limit(1)
                        )
                    )
                    .mappings()
                    .first()
                )
                if row is None:
                    return None
                claimed = await conn.execute(
                    update(jobs)
                    .where(jobs.c.id == row["id"], jobs.c.status == "pending")
                    .values(status="running")
                )
                if claimed.rowcount != 1:  # type: ignore[attr-defined]
                    continue
            return Job(
                id=row["id"],
                name=row["name"],
                due_at=parse_iso(row["due_at"]),
                payload=json.loads(row["payload"]),
                every_seconds=row["every_seconds"],
                daily_at=row["daily_at"],
            )

    async def _warn_unhandled(self, until: datetime, names: list[str]) -> None:
        async with self.db.read() as conn:
            result = await conn.execute(
                select(jobs.c.name)
                .where(jobs.c.status == "pending", jobs.c.due_at <= iso_utc(until), jobs.c.name.not_in(names))
                .distinct()
            )
            missing = {r[0] for r in result} - self._warned_unhandled
        for name in sorted(missing):
            self._warned_unhandled.add(name)
            log.warning("no handler registered for job %r; leaving it pending", name)

    async def _run(self, job: Job) -> None:
        handler = self._handlers[job.name]
        log.debug("running job %s (%s) due %s", job.id, job.name, job.due_at.isoformat())
        status, error = "done", None
        try:
            await handler(job)
        except Exception as exc:  # a failing job must not stop the night
            log.exception("job %s (%s) failed", job.id, job.name)
            status, error = "failed", repr(exc)
        # One transaction: mark finished and enqueue the successor together.
        async with self.db.write() as conn:
            await conn.execute(
                update(jobs)
                .where(jobs.c.id == job.id)
                .values(
                    status=status,
                    last_error=error,
                    attempts=jobs.c.attempts + 1,
                    ran_at=iso_utc(self.clock.now()),
                )
            )
            successor = self._successor(job)
            if successor is not None:
                await conn.execute(successor)

    def _successor(self, job: Job) -> Insert | None:
        if job.every_seconds:
            due = job.due_at + timedelta(seconds=job.every_seconds)
        elif job.daily_at:
            due = next_daily(job.due_at, job.daily_at)
        else:
            return None
        return self._insert(new_id("job"), job.name, due, job.payload, job.every_seconds, job.daily_at)


async def tick_loop(scheduler: Scheduler, stop: asyncio.Event, interval_s: float = 1.0) -> None:
    """Run due jobs every `interval_s` real seconds until `stop` is set."""
    while not stop.is_set():
        try:
            await scheduler.run_due()
        except Exception:  # keep the night shift alive; CancelledError still propagates
            log.exception("scheduler tick failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_s)
        except TimeoutError:
            pass
