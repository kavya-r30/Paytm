"""Foundation endpoints; merchant and actor identity come from provisioned server sessions."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Request

from arth.api.problems import ProblemError
from arth.contracts.approval import ApprovalRequest
from arth.contracts.command import CommandRequest
from arth.governance.audit import verify_audit
from arth.governance.commands import CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository

router = APIRouter()


async def require_session(request: Request) -> Session:
    authorization = request.headers.get("authorization", "")
    session = (
        request.app.state.sessions.get(authorization.removeprefix("Bearer "))
        if authorization.startswith("Bearer ")
        else None
    )
    if session is None and authorization.startswith("Bearer ") and hasattr(request.app.state, "staff"):
        try:
            session = await request.app.state.staff.resolve(authorization.removeprefix("Bearer "))
        except CommandError:
            session = None
    if session is None:
        raise ProblemError(401, "auth.missing_session", "error.auth.missing_session", title="Unauthorized")
    return session


def problem(exc: CommandError) -> ProblemError:
    return ProblemError(409, str(exc), "error." + str(exc), title="Command refused")


@router.post("/v1/commands")
async def submit_command(
    request: Request,
    body: CommandRequest,
    session: Annotated[Session, Depends(require_session)],
    idempotency_key: Annotated[str, Header(min_length=1, max_length=200)],
) -> dict[str, Any]:
    try:
        result: dict[str, Any] = await request.app.state.commands.submit(
            session, body.type, body.payload, idempotency_key
        )
    except CommandError as exc:
        raise problem(exc) from exc
    if body.type == "counter.request_upi" and result["status"] == "executed":
        # the merchant backend asks the payment gateway for a dynamic QR; the rails simulator plays it (T2.2)
        data = result["data"]
        sim = request.app.state.sim
        qr = await sim.create_qr(session.merchant_id, data["order_ref"], data["amount_paise"])
        result["data"] = {**data, "pay_token": qr["token"]}
    return result


@router.post("/v1/approvals/{thread_id}")
async def decide_approval(
    request: Request,
    thread_id: str,
    body: ApprovalRequest,
    session: Annotated[Session, Depends(require_session)],
    idempotency_key: Annotated[str, Header(min_length=1, max_length=200)],
) -> dict[str, Any]:
    try:
        return await request.app.state.commands.decide(
            session,
            thread_id,
            body.decision.value,
            idempotency_key,
            decisions={key: value.value for key, value in (body.decisions or {}).items()},
            edits=body.edits,
        )
    except CommandError as exc:
        raise problem(exc) from exc


@router.get("/v1/audit/verify")
async def verify(request: Request, session: Annotated[Session, Depends(require_session)]) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await verify_audit(Repository(conn, session.merchant_id))
