"""Spans: one row per step of a turn or playbook (OBS-1). Published live to subscribers (stage, SSE)."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Literal

from sqlalchemy import insert

from arth.core.clock import SimClock, iso_utc
from arth.core.db import Database
from arth.core.ids import new_id
from arth.core.tables import spans as spans_table

log = logging.getLogger(__name__)
Mode = Literal["live", "replay", "none"]
Status = Literal["ok", "error", "cancelled"]

BATCH_SIZE = 50
BATCH_WINDOW_S = 0.1
PERSIST_QUEUE_MAX = 10_000
DROP_LOG_EVERY = 100


def safe_json(value: Any) -> str:
    """JSON text that is always valid (no NaN/Infinity); never raises."""
    try:
        return json.dumps(value, sort_keys=True, default=str, allow_nan=False)
    except (TypeError, ValueError):
        return json.dumps({"_unserialisable": repr(value)[:2000]})


@dataclass(frozen=True)
class Span:
    id: str
    trace_id: str
    parent_id: str | None
    kind: str
    name: str
    start_at: str
    dur_ms: float
    mode: Mode
    cost_paise: int
    attrs: dict[str, Any] = field(default_factory=dict)
    status: Status = "ok"


class SpanAttrs:
    """Mutable attributes yielded by `SpanBus.span`; also carries the ids for child spans.

    `attrs["cost_paise"] = n` sets the span cost; any other key lands in the span's attrs.
    """

    def __init__(self, span_id: str, trace_id: str) -> None:
        self.span_id = span_id
        self.trace_id = trace_id
        self.attrs: dict[str, Any] = {}
        self.cost_paise: int = 0

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "cost_paise":
            self.cost_paise = value
        else:
            self.attrs[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.cost_paise if key == "cost_paise" else self.attrs[key]


def _cost(raw: Any) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError, OverflowError):
        log.warning("invalid span cost_paise %r; recording 0", raw)
        return 0


ERROR_TEXT_MAX = 500


def _error_text(exc: BaseException) -> str:
    """`Type: message`, capped so user data in exception text can't flood the stream or DB."""
    text = f"{type(exc).__name__}: {exc}"
    return text if len(text) <= ERROR_TEXT_MAX else text[: ERROR_TEXT_MAX - 1] + "…"


class SpanBus:
    """Publishes spans to live subscribers and persists them in the background (best-effort).

    `emit` fans out to subscribers immediately, then enqueues the span for persistence. One
    background task drains the queue in batches (<= 50 spans or 100 ms) into a single multi-row
    insert per transaction. Persistence and serialisation failures are logged, never raised.

    Lifecycle: the app lifespan must `await bus.start()` on startup and `await bus.aclose()` on
    shutdown (flushes pending spans, then stops the task). Without `start()` (or without a DB)
    no task runs; `flush()` then persists any queued spans inline.

    Never call `flush()`/`aclose()` while holding `db.write()`: the persister needs that lock, so
    it would deadlock. `emit()` itself never awaits and is safe anywhere.
    """

    def __init__(self, clock: SimClock, db: Database | None = None) -> None:
        self.clock = clock
        self.db = db
        self._subscribers: set[asyncio.Queue[Span]] = set()
        self._drops: dict[asyncio.Queue[Span], int] = {}
        self._pending: asyncio.Queue[Span] = asyncio.Queue(maxsize=PERSIST_QUEUE_MAX)
        self._task: asyncio.Task[None] | None = None

    def subscribe(self, maxsize: int = 1000) -> asyncio.Queue[Span]:
        queue: asyncio.Queue[Span] = asyncio.Queue(maxsize=maxsize)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[Span]) -> None:
        self._subscribers.discard(queue)
        self._drops.pop(queue, None)

    async def start(self) -> None:
        """Start the persister (idempotent; restarts it if a previous task died)."""
        if self.db is not None and (self._task is None or self._task.done()):
            self._task = asyncio.create_task(self._run(), name="span-persister")

    async def flush(self) -> None:
        """Wait until every span emitted so far has been written (or logged as failed)."""
        if self.db is None:
            return
        if self._task is not None and not self._task.done():
            await self._pending.join()
            return
        while not self._pending.empty():
            await self._write_batch(self._take_nowait(BATCH_SIZE))

    async def aclose(self) -> None:
        await self.flush()
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def emit(self, span: Span) -> None:
        for queue in list(self._subscribers):
            self._publish(queue, span)
        if self.db is None:
            return
        if self._pending.full():
            with contextlib.suppress(asyncio.QueueEmpty):
                self._pending.get_nowait()
                self._pending.task_done()
            log.warning("span persistence backlog full; dropped oldest span")
        self._pending.put_nowait(span)

    def _publish(self, queue: asyncio.Queue[Span], span: Span) -> None:
        try:
            queue.put_nowait(span)
            return
        except asyncio.QueueFull:
            pass
        with contextlib.suppress(asyncio.QueueEmpty):
            queue.get_nowait()  # drop the oldest so the live view stays current
        with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(span)
        drops = self._drops.get(queue, 0) + 1
        self._drops[queue] = drops
        if drops % DROP_LOG_EVERY == 1:
            log.warning("span subscriber is full; dropped oldest span (%d dropped so far)", drops)

    def _take_nowait(self, limit: int) -> list[Span]:
        batch: list[Span] = []
        while len(batch) < limit:
            try:
                batch.append(self._pending.get_nowait())
            except asyncio.QueueEmpty:
                break
        return batch

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            batch = [await self._pending.get()]
            deadline = loop.time() + BATCH_WINDOW_S
            while len(batch) < BATCH_SIZE:
                batch.extend(self._take_nowait(BATCH_SIZE - len(batch)))
                remaining = deadline - loop.time()
                if len(batch) >= BATCH_SIZE or remaining <= 0:
                    break
                try:
                    batch.append(await asyncio.wait_for(self._pending.get(), remaining))
                except TimeoutError:
                    break
            await self._write_batch(batch)

    async def _write_batch(self, batch: list[Span]) -> None:
        if not batch:
            return
        try:
            if self.db is not None:
                rows = [self._row(span) for span in batch]
                async with self.db.write() as conn:
                    await conn.execute(insert(spans_table).values(rows))
        except Exception:
            log.exception("failed to persist %d span(s); telemetry dropped", len(batch))
        finally:
            for _ in batch:
                self._pending.task_done()

    @staticmethod
    def _row(span: Span) -> dict[str, Any]:
        return {
            "id": span.id,
            "trace_id": span.trace_id,
            "parent_id": span.parent_id,
            "kind": span.kind,
            "name": span.name,
            "start_at": span.start_at,
            "dur_ms": span.dur_ms,
            "mode": span.mode,
            "cost_paise": span.cost_paise,
            "attrs": safe_json({**span.attrs, "status": span.status}),
        }

    @asynccontextmanager
    async def span(
        self,
        kind: str,
        name: str,
        *,
        trace_id: str | None = None,
        parent_id: str | None = None,
        mode: Mode = "none",
    ) -> AsyncIterator[SpanAttrs]:
        span_id = new_id("span")
        handle = SpanAttrs(span_id, trace_id or new_id("trace"))
        start_at = iso_utc(self.clock.now())
        started = perf_counter()
        status: Status = "ok"
        try:
            yield handle
        except asyncio.CancelledError:
            status = "cancelled"
            handle.attrs["cancelled"] = True
            raise
        except BaseException as exc:  # incl. SystemExit/KeyboardInterrupt; CancelledError handled above
            status = "error"
            handle.attrs["error"] = _error_text(exc)
            raise
        finally:
            try:
                await self.emit(
                    Span(
                        id=span_id,
                        trace_id=handle.trace_id,
                        parent_id=parent_id,
                        kind=kind,
                        name=name,
                        start_at=start_at,
                        dur_ms=(perf_counter() - started) * 1000,
                        mode=mode,
                        cost_paise=_cost(handle.cost_paise),
                        attrs=dict(handle.attrs),
                        status=status,
                    )
                )
            except Exception:
                log.exception("failed to emit span %s", span_id)
