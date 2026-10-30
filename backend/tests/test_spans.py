import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from time import perf_counter
from typing import Any

import pytest
from sqlalchemy import select

from arth.api.stream import span_events
from arth.core.clock import IST, SimClock
from arth.core.db import Database
from arth.core.spans import Span, SpanBus
from arth.core.tables import spans

START = datetime(2026, 10, 29, 7, 45, tzinfo=IST)


def make_span(n: int) -> Span:
    return Span(
        id=f"span_{n}",
        trace_id="trace_x",
        parent_id=None,
        kind="tool",
        name=f"s{n}",
        start_at="2026-10-29T02:15:00.000000Z",
        dur_ms=1.0,
        mode="none",
        cost_paise=0,
    )


class BrokenDb:
    @asynccontextmanager
    async def write(self) -> AsyncIterator[Any]:
        raise RuntimeError("disk on fire")
        yield  # pragma: no cover


async def test_span_reaches_subscriber_within_200ms_and_is_persisted(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    queue = bus.subscribe()
    started = perf_counter()
    async with bus.span("tool", "analytics.sales", mode="live") as attrs:
        attrs["rows"] = 3
        attrs["cost_paise"] = 2
    span = await asyncio.wait_for(queue.get(), timeout=0.2)
    assert perf_counter() - started < 0.2
    assert (span.kind, span.name, span.mode, span.cost_paise) == ("tool", "analytics.sales", "live", 2)
    assert span.attrs == {"rows": 3}
    assert span.status == "ok"
    assert span.start_at == "2026-10-29T02:15:00.000000Z"
    await bus.flush()
    async with db.read() as conn:
        row = (await conn.execute(select(spans))).mappings().one()
    assert json.loads(row["attrs"]) == {"rows": 3, "status": "ok"}


async def test_persisted_row_has_cost_mode_parent_and_duration(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    async with bus.span("tool", "x", parent_id="span_parent", mode="replay") as attrs:
        attrs["cost_paise"] = 7
    await bus.flush()
    async with db.read() as conn:
        row = (await conn.execute(select(spans))).mappings().one()
    assert (row["cost_paise"], row["mode"], row["parent_id"]) == (7, "replay", "span_parent")
    assert row["dur_ms"] >= 0


async def test_child_span_shares_trace(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    queue = bus.subscribe()
    async with bus.span("turn", "turn") as parent:
        async with bus.span("tool", "x", trace_id=parent.trace_id, parent_id=parent.span_id):
            pass
    child, outer = await queue.get(), await queue.get()
    assert child.trace_id == outer.trace_id
    assert child.parent_id == outer.id


async def test_body_error_is_recorded_and_propagates(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    queue = bus.subscribe()
    with pytest.raises(ValueError, match="boom"):
        async with bus.span("tool", "bad"):
            raise ValueError("boom")
    span = queue.get_nowait()
    assert span.status == "error"
    assert span.attrs["error"] == "ValueError: boom"
    await bus.flush()
    async with db.read() as conn:
        row = (await conn.execute(select(spans))).mappings().one()
    stored = json.loads(row["attrs"])
    assert stored["status"] == "error"
    assert stored["error"] == "ValueError: boom"


async def test_cancellation_is_recorded_and_propagates() -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe()

    async def body() -> None:
        async with bus.span("tool", "slow"):
            await asyncio.sleep(10)

    task = asyncio.ensure_future(body())
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    span = queue.get_nowait()
    assert span.status == "cancelled"
    assert span.attrs["cancelled"] is True


async def test_bad_cost_and_unserialisable_attrs_do_not_break_caller(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    async with bus.span("tool", "weird") as attrs:
        attrs["cost_paise"] = "lots"
        attrs["ratio"] = float("nan")
        attrs["obj"] = object()
    await bus.flush()
    async with db.read() as conn:
        rows = (await conn.execute(select(spans))).mappings().all()
    assert len(rows) == 1
    assert rows[0]["cost_paise"] == 0
    json.loads(rows[0]["attrs"])  # valid JSON, no NaN literal


async def test_persistence_failure_does_not_break_caller_or_mask_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    bus = SpanBus(SimClock(START), BrokenDb())  # type: ignore[arg-type]
    queue = bus.subscribe()
    async with bus.span("tool", "ok"):
        pass
    with pytest.raises(ValueError, match="body failed"):
        async with bus.span("tool", "bad"):
            raise ValueError("body failed")
    with caplog.at_level(logging.ERROR):
        await bus.flush()
        await bus.aclose()
    assert queue.qsize() == 2
    assert "disk on fire" in caplog.text


async def test_background_task_batches_and_aclose_flushes(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    await bus.start()
    for n in range(120):
        await bus.emit(make_span(n))
    await bus.aclose()
    async with db.read() as conn:
        count = len((await conn.execute(select(spans.c.id))).all())
    assert count == 120


async def test_flush_without_started_task_persists_inline(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    await bus.emit(make_span(1))
    await bus.flush()
    async with db.read() as conn:
        assert len((await conn.execute(select(spans.c.id))).all()) == 1


async def test_bus_without_db_flush_and_close_are_noops() -> None:
    bus = SpanBus(SimClock(START))
    await bus.start()
    await bus.emit(make_span(1))
    await bus.flush()
    await bus.aclose()


async def test_full_subscriber_drops_oldest_and_does_not_raise(
    caplog: pytest.LogCaptureFixture,
) -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe(maxsize=2)
    with caplog.at_level(logging.WARNING):
        for n in range(1, 204):
            await bus.emit(make_span(n))
    assert [queue.get_nowait().id for _ in range(2)] == ["span_202", "span_203"]
    assert (
        len([r for r in caplog.records if r.levelno == logging.WARNING]) == 3
    )  # drops 1, 101 and 201 of 201


async def test_span_events_formats_server_sent_events() -> None:
    bus = SpanBus(SimClock(START))
    stream = span_events(bus, limit=1)
    pending = asyncio.ensure_future(anext(stream))
    await asyncio.sleep(0.01)  # let the stream subscribe
    async with bus.span("guard", "grounding"):
        pass
    item = await asyncio.wait_for(pending, timeout=1)
    assert item["event"] == "span"
    assert json.loads(item["data"])["name"] == "grounding"


async def test_span_events_unsubscribes_on_aclose() -> None:
    bus = SpanBus(SimClock(START))
    stream = span_events(bus)
    pending = asyncio.ensure_future(anext(stream))
    await asyncio.sleep(0.01)
    assert len(bus._subscribers) == 1
    await bus.emit(make_span(1))
    await asyncio.wait_for(pending, timeout=1)
    await stream.aclose()
    assert len(bus._subscribers) == 0


async def test_base_exception_in_body_is_recorded_as_error() -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe()
    with pytest.raises(SystemExit):
        async with bus.span("tool", "exit"):
            raise SystemExit(3)
    span = queue.get_nowait()
    assert span.status == "error"
    assert span.attrs["error"] == "SystemExit: 3"


async def test_long_error_text_is_truncated() -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe()
    with pytest.raises(ValueError):
        async with bus.span("tool", "big"):
            raise ValueError("x" * 5000)
    error = queue.get_nowait().attrs["error"]
    assert len(error) <= 500
    assert error.startswith("ValueError: xxx") and error.endswith("…")
