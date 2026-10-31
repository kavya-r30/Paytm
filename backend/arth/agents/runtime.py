"""Durable playbook runtime (T5.1–T5.6).

A playbook is a dict of named async steps. Each step returns what happens next:
`Next(step)`, `Wait(topic, match, until, next, timeout_next)`, `Done(result)` or `Fail(reason)`.
Run state (step cursor + JSON context) is persisted after every step, so a restart resumes where it was.
Side effects go through the Command Bus with idempotency keys derived from `run_id:step`, so a replayed step
can never send anything twice. The Event Matcher (a Dispatcher consumer) wakes runs waiting on a matching
event; deadlines wake them through `tick`. Agents propose with the owner's authority but can never approve:
`CommandBus.decide` refuses any agent session (AIQ-1).
"""

import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from arth.agents.tables import agent_controls, contact_locks, playbook_runs, playbook_steps, work_items
from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.governance.commands import CommandBus, CommandError
from arth.governance.events import Dispatcher, emit_event
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import merchants, staff

MAX_STEPS_PER_TICK = 25  # ceiling: a runaway playbook cannot spin
BUDGET_PAISE = {"default": 500}  # per-run AI spend ceiling (WFL-7)


@dataclass
class Next:
    step: str


@dataclass
class Wait:
    topic: str
    match: dict[str, Any]
    next: str
    until_minutes: int | None = None
    timeout_next: str | None = None


@dataclass
class Done:
    result: dict[str, Any] = field(default_factory=dict)


@dataclass
class Fail:
    reason: str


Outcome = Next | Wait | Done | Fail


@dataclass
class Run:
    id: str
    merchant_id: str
    playbook: str
    agent: str
    subject: str
    step: str
    context: dict[str, Any]


Step = Callable[["Runtime", Run], Awaitable[Outcome]]


@dataclass
class Playbook:
    name: str
    agent: str
    steps: dict[str, Step]
    start: str = "start"


class Runtime:
    def __init__(self, bus: CommandBus, dispatcher: Dispatcher | None) -> None:
        self.bus, self.db, self.clock = bus, bus.db, bus.clock
        self.playbooks: dict[str, Playbook] = {}
        self._locks: dict[
            str, asyncio.Lock
        ] = {}  # one tick at a time per merchant (loop and runner may race)
        if dispatcher is not None:
            dispatcher.on("playbooks.matcher", self._match)

    def register(self, playbook: Playbook) -> None:
        if playbook.start not in playbook.steps:
            raise ValueError(f"playbook {playbook.name}: missing start step")  # manifest validated at startup
        self.playbooks[playbook.name] = playbook

    # sessions and side effects ----------------------------------------------------------------
    async def session(self, merchant_id: str, agent: str) -> Session:
        async with self.db.read() as conn:
            owners = await Repository(conn, merchant_id).select(staff, staff.c.role == "owner")
        # Agents propose under the owner's authority on the "agent" channel: R1 runs, R2/R3 become gates the
        # owner answers, R4 is refused (Console only). The bus refuses any approval from an agent session.
        return Session(merchant_id, owners[0]["id"], "owner", channel="agent", actor_kind="agent")

    async def command(self, run: Run, kind: str, payload: dict[str, Any], label: str) -> dict[str, Any]:
        """Exactly-once side effect: the idempotency key is stable for this run and step label."""
        session = await self.session(run.merchant_id, run.agent)
        return await self.bus.submit(session, kind, payload, f"{run.id}:{label}")

    async def work(
        self, run: Run, kind: str, title_key: str, params: dict[str, Any], urgency: int = 1
    ) -> str:
        identity = new_id("work")
        async with self.db.write() as conn:
            await Repository(conn, run.merchant_id).insert(
                work_items,
                {
                    "id": identity,
                    "kind": kind,
                    "agent": run.agent,
                    "run_id": run.id,
                    "title_key": title_key,
                    "params": json.dumps(params),
                    "urgency": urgency,
                    "status": "open",
                    "created_at": iso_utc(self.clock.now()),
                },
            )
        return identity

    async def lock(self, run: Run, subject: str, minutes: int = 60 * 24) -> bool:
        """WFL-5: one playbook talks to a person at a time; a held lock defers with a traced reason."""
        now = iso_utc(self.clock.now())
        async with self.db.write() as conn:
            repo = Repository(conn, run.merchant_id)
            rows = await repo.select(contact_locks, contact_locks.c.subject == subject)
            if rows and rows[0]["run_id"] != run.id and rows[0]["until"] > now:
                return False
            until = iso_utc(self.clock.now() + timedelta(minutes=minutes))
            if rows:
                await repo.update(
                    contact_locks, {"run_id": run.id, "until": until}, contact_locks.c.subject == subject
                )
            else:
                await repo.insert(
                    contact_locks,
                    {"id": new_id("lock"), "subject": subject, "run_id": run.id, "until": until},
                )
        return True

    async def unlock(self, run: Run, subject: str) -> None:
        async with self.db.write() as conn:
            await Repository(conn, run.merchant_id).update(
                contact_locks,
                {"until": iso_utc(self.clock.now())},
                contact_locks.c.subject == subject,
                contact_locks.c.run_id == run.id,
            )

    # controls ---------------------------------------------------------------------------------------
    async def set_paused(self, merchant_id: str, agent: str, paused: bool) -> None:
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            values = {"paused": int(paused), "updated_at": iso_utc(self.clock.now())}
            if await repo.select(agent_controls, agent_controls.c.agent == agent):
                await repo.update(agent_controls, values, agent_controls.c.agent == agent)
            else:
                await repo.insert(agent_controls, {"id": new_id("control"), "agent": agent, **values})

    async def paused(self, repo: Repository, agent: str) -> bool:
        rows = {r["agent"]: r["paused"] for r in await repo.select(agent_controls)}
        return bool(rows.get("*") or rows.get(agent))  # "*" is the kill switch (TRU-4, WFL-8)

    # lifecycle ----------------------------------------------------------------------------------------
    async def start(
        self, merchant_id: str, name: str, subject: str, context: dict[str, Any] | None = None
    ) -> str:
        async with self.db.write() as conn:
            return await self.start_in(Repository(conn, merchant_id), name, subject, context)

    async def start_in(
        self, repo: Repository, name: str, subject: str, context: dict[str, Any] | None = None
    ) -> str:
        """Start inside an existing transaction (bus command or event consumer). One live run per subject."""
        playbook = self.playbooks.get(name)
        if playbook is None:
            raise CommandError("playbooks.unknown")
        live = await repo.select(
            playbook_runs,
            playbook_runs.c.playbook == name,
            playbook_runs.c.subject == subject,
            playbook_runs.c.status.in_(["ready", "waiting", "running"]),
        )
        if live:
            return str(live[0]["id"])
        identity, now = new_id("run"), iso_utc(self.clock.now())
        await repo.insert(
            playbook_runs,
            {
                "id": identity,
                "playbook": name,
                "agent": playbook.agent,
                "subject": subject,
                "status": "ready",
                "step": playbook.start,
                "context": json.dumps(context or {}),
                "created_at": now,
                "updated_at": now,
            },
        )
        return identity

    async def cancel(self, merchant_id: str, run_id: str) -> None:
        async with self.db.write() as conn:
            await Repository(conn, merchant_id).update(
                playbook_runs,
                {"status": "cancelled", "updated_at": iso_utc(self.clock.now())},
                playbook_runs.c.id == run_id,
            )

    async def _match(self, repo: Repository, event: dict[str, Any]) -> None:
        """Event Matcher (WFL-2): wake runs waiting for this topic whose match fields equal the payload's."""
        for row in await repo.select(
            playbook_runs, playbook_runs.c.status == "waiting", playbook_runs.c.wait_topic == event["type"]
        ):
            match = json.loads(row["wait_match"] or "{}")
            if all(event["payload"].get(k) == v for k, v in match.items()):
                context = json.loads(row["context"])
                context["event"] = event["payload"]
                await repo.update(
                    playbook_runs,
                    {
                        "status": "ready",
                        "context": json.dumps(context),
                        "updated_at": iso_utc(self.clock.now()),
                    },
                    playbook_runs.c.id == row["id"],
                )

    async def tick(self, merchant_id: str) -> int:
        lock = self._locks.setdefault(merchant_id, asyncio.Lock())
        async with lock:
            return await self._tick(merchant_id)

    async def _tick(self, merchant_id: str) -> int:
        """Run every ready run (and waits past their deadline) until each waits, ends or hits a ceiling."""
        now = iso_utc(self.clock.now())
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            for row in await repo.select(playbook_runs, playbook_runs.c.status == "waiting"):
                if row["wait_until"] and row["wait_until"] <= now:
                    context = json.loads(row["context"])
                    context["timed_out"] = True
                    await repo.update(
                        playbook_runs,
                        {
                            "status": "ready",
                            "context": json.dumps(context),
                            "step": context.pop("_timeout_next", row["step"]),
                        },
                        playbook_runs.c.id == row["id"],
                    )
            ready = await repo.select(playbook_runs, playbook_runs.c.status == "ready")
            stopped = {r["id"] for r in ready if await self.paused(repo, r["agent"])}
        steps = 0
        for row in sorted(ready, key=lambda r: r["created_at"]):
            if row["id"] not in stopped and row["playbook"] in self.playbooks:
                steps += await self._advance(merchant_id, row)
        return steps

    async def _advance(self, merchant_id: str, row: dict[str, Any]) -> int:
        playbook = self.playbooks[row["playbook"]]
        run = Run(
            row["id"],
            merchant_id,
            row["playbook"],
            row["agent"],
            row["subject"],
            row["step"],
            json.loads(row["context"]),
        )
        for count in range(1, MAX_STEPS_PER_TICK + 1):
            try:
                outcome = await playbook.steps[run.step](self, run)
            except CommandError as exc:
                outcome = Fail(str(exc))
            if not isinstance(outcome, Wait):
                run.context.pop("event", None)
            await self._record(run, outcome)
            if not isinstance(outcome, Next):
                return count
            run.step = outcome.step
        await self._record(run, Fail("playbook.step_ceiling"))
        return MAX_STEPS_PER_TICK

    async def _record(self, run: Run, outcome: Outcome) -> None:
        now = iso_utc(self.clock.now())
        values: dict[str, Any] = {
            "step": run.step,
            "context": json.dumps(run.context),
            "updated_at": now,
            "wait_topic": None,
            "wait_match": None,
            "wait_until": None,
        }
        status, detail = "ready", dict[str, Any]()
        if isinstance(outcome, Next):
            values["step"] = outcome.step
            status, detail = "running", {"next": outcome.step}
        elif isinstance(outcome, Wait):
            context = dict(run.context)
            if outcome.timeout_next:
                context["_timeout_next"] = outcome.timeout_next
            values.update(
                step=outcome.next,
                wait_topic=outcome.topic,
                wait_match=json.dumps(outcome.match),
                context=json.dumps(context),
                wait_until=iso_utc(self.clock.now() + timedelta(minutes=outcome.until_minutes))
                if outcome.until_minutes
                else None,
            )
            status, detail = "waiting", {"topic": outcome.topic, "match": outcome.match}
        elif isinstance(outcome, Done):
            status, detail = "done", outcome.result
        else:
            status, detail = "failed", {"reason": outcome.reason}
        values["status"] = status if status != "running" else "ready"
        async with self.db.write() as conn:
            repo = Repository(conn, run.merchant_id)
            await repo.update(playbook_runs, values, playbook_runs.c.id == run.id)
            await repo.insert(
                playbook_steps,
                {
                    "id": new_id("pstep"),
                    "run_id": run.id,
                    "step": run.step,
                    "status": status,
                    "detail": json.dumps(detail, default=str),
                    "occurred_at": now,
                },
            )
            if status != "ready":  # surfaces refresh the Team and Run screens (OBS-2)
                actor = Session(run.merchant_id, "agent_" + run.agent, "system", actor_kind="agent")
                await emit_event(
                    repo,
                    self.clock,
                    actor,
                    "playbook.updated",
                    run.id,
                    {
                        "run_id": run.id,
                        "playbook": run.playbook,
                        "status": values["status"],
                        "step": values["step"],
                    },
                )

    async def merchants(self) -> list[str]:
        return sorted(self.bus.merchant_ids)

    async def shop_pack(self, merchant_id: str) -> str:
        async with self.db.read() as conn:
            return str((await Repository(conn, merchant_id).select(merchants))[0]["pack"])
