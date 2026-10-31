"""Director API (presenter only). L0 has a ping; L2/L8 add scenario control."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from arth.api.auth import require_token

router = APIRouter(prefix="/v1/director", dependencies=[Depends(require_token("director"))])


@router.get("/ping")
async def director_ping() -> dict[str, bool]:
    return {"ok": True}
