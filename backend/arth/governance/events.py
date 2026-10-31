"""Transactional event delivery: consumer effects and offsets share a transaction."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.db import Database
from arth.core.ids import new_id
from arth.governance.audit import canonical
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import consumer_offsets, outbox

Consumer = Callable[[Repository, dict[str, Any]], Awaitable[None]]


async def emit_event(
    repo: Repository, clock: SimClock, session: Session, topic: str, cause: str, payload: dict[str, Any]
) -> None:
    event = {
        "event_id": new_id("evt"),
        "type": topic,
        "merchant_id": repo.merchant_id,
        "occurred_at": iso_utc(clock.now()),
        "actor": {
            "kind": session.actor_kind
            or ("system" if session.role == "system" else "owner" if session.role == "owner" else "staff"),
            "id": session.actor_id,
        },
        "causation_id": cause,
        "payload": payload,
    }
    await repo.insert(
        outbox,
        {
            "event_id": event["event_id"],
            "type": topic,
            "occurred_at": event["occurred_at"],
            "payload": canonical(event),
        },
    )


class Dispatcher:
    def __init__(self, db: Database, clock: SimClock) -> None:
        self.db, self.clock = db, clock
        self.consumers: dict[str, Consumer] = {}
        self.subscribers: dict[asyncio.Queue[dict[str, Any]], str] = {}
        self.views: dict[str, set[str]] = {}

    def on(self, name: str, handler: Consumer) -> None:
        self.consumers[name] = handler

    def subscribe(self, merchant_id: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=1000)
        self.subscribers[queue] = merchant_id
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self.subscribers.pop(queue, None)

    def publish(self, merchant_id: str, item: dict[str, Any]) -> None:
        """Push a non-persisted stream item (e.g. a turn's envelope) to this merchant's live subscribers."""
        for queue, owner in list(self.subscribers.items()):
            if owner == merchant_id:
                if queue.full():
                    queue.get_nowait()
                queue.put_nowait(item)

    def declare_view(self, name: str, topics: set[str]) -> None:
        self.views[name] = topics

    async def dispatch(self, merchant_id: str) -> None:
        for name, consumer in list(self.consumers.items()) + [("sse", self._broadcast)]:
            async with self.db.write() as conn:
                repo = Repository(conn, merchant_id)
                offsets = await repo.select(consumer_offsets, consumer_offsets.c.consumer == name)
                last = offsets[0]["last_seq"] if offsets else 0
                rows = sorted(await repo.select(outbox, outbox.c.seq > last), key=lambda r: r["seq"])
                for row in rows:
                    repo.command_id = row["event_id"]  # consumer effects are caused by this event
                    await consumer(repo, json.loads(row["payload"]))
                    last = row["seq"]
                if not offsets:
                    await repo.insert(consumer_offsets, {"consumer": name, "last_seq": last})
                elif rows:
                    await repo.update(
                        consumer_offsets, {"last_seq": last}, consumer_offsets.c.consumer == name
                    )

    async def _broadcast(self, repo: Repository, event: dict[str, Any]) -> None:
        views = sorted(name for name, topics in self.views.items() if event["type"] in topics)
        events = [event]
        if views and event["type"] != "view.invalidate":
            events.append(
                {
                    **event,
                    "event_id": new_id("evt"),
                    "type": "view.invalidate",
                    "causation_id": event["event_id"],
                    "payload": {"views": views},
                }
            )
        for queue, merchant_id in list(self.subscribers.items()):
            if merchant_id == repo.merchant_id:
                for item in events:
                    if queue.full():
                        queue.get_nowait()
                    queue.put_nowait(item)
