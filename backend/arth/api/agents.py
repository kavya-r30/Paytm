"""Team, Run and Memory views; Work Board batching (T5.3)."""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from arth.agents.views import memory_view, run_view, team_view
from arth.api.commerce import Actor
from arth.api.problems import ProblemError
from arth.governance.commands import CommandError
from arth.governance.repository import Repository

router = APIRouter()


class BatchBody(BaseModel):
    gate_ids: list[str] = Field(min_length=1, max_length=5)


@router.get("/v1/views/team")
async def team(request: Request, session: Actor) -> dict[str, Any]:
    state = request.app.state
    async with state.db.read() as conn:
        return await team_view(Repository(conn, session.merchant_id), state.policies, state.helpers)


@router.get("/v1/views/runs/{run_id}")
async def run(request: Request, run_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await run_view(Repository(conn, session.merchant_id), run_id)


@router.get("/v1/views/memory")
async def memory(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await memory_view(Repository(conn, session.merchant_id))


@router.post("/v1/work/batches")
async def batch(request: Request, body: BatchBody, session: Actor) -> dict[str, Any]:
    """Group pending gates into one ask ("Teeno haan"); answer it via POST /v1/approvals/{thread_id}."""
    try:
        return {"thread_id": await request.app.state.commands.batch(session, body.gate_ids)}
    except CommandError as exc:
        raise ProblemError(409, str(exc), "error." + str(exc), title="Batch refused") from exc
