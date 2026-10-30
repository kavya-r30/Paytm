"""GET /v1/stream: server-sent events. L0 streams spans; L1 adds domain events and view invalidations."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from arth.api.governance import require_session
from arth.core.spans import SpanBus, safe_json
from arth.governance.events import Dispatcher
from arth.governance.policy import Session

router = APIRouter()


async def span_events(bus: SpanBus, *, limit: int | None = None) -> AsyncGenerator[dict[str, str]]:
    queue = bus.subscribe()
    sent = 0
    try:
        while limit is None or sent < limit:
            span = await queue.get()
            yield {"event": "span", "data": safe_json(asdict(span))}
            sent += 1
    finally:
        bus.unsubscribe(queue)


@router.get("/v1/stream")
async def get_stream(request: Request) -> EventSourceResponse:
    session = await require_session(request)
    return EventSourceResponse(domain_events(request.app.state.events, request.app.state.spans, session))


async def domain_events(
    dispatcher: Dispatcher, bus: SpanBus, session: Session
) -> AsyncGenerator[dict[str, str]]:
    domain, spans = dispatcher.subscribe(session.merchant_id), bus.subscribe()
    tasks: dict[asyncio.Task[Any], str] = {
        asyncio.create_task(domain.get()): "domain",
        asyncio.create_task(spans.get()): "span",
    }
    try:
        while True:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                kind = tasks.pop(task)
                item = task.result()
                queue = domain if kind == "domain" else spans
                tasks[asyncio.create_task(queue.get())] = kind
                if kind == "domain":
                    yield {"event": item["type"], "id": item["event_id"], "data": safe_json(item)}
                elif item.attrs.get("merchant_id") == session.merchant_id:
                    yield {"event": "span", "data": safe_json(asdict(item))}
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        dispatcher.unsubscribe(domain)
        bus.unsubscribe(spans)
