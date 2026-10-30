"""GET /healthz: liveness, mode, sim clock, packs and provider-key status (booleans only)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from arth.core.clock import iso_utc
from arth.core.config import provider_status

router = APIRouter()


@router.get("/healthz")
async def get_health(request: Request) -> dict[str, object]:
    state = request.app.state
    return {
        "status": "ok",
        "mode": state.settings.mode,
        "clock": iso_utc(state.clock.now()),
        "packs": state.packs.names,
        "providers": provider_status(state.settings, state.providers),
    }
