"""L1b authentication, scoped catalog reads and screen read models."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Query, Request

from arth.api.auth import require_token
from arth.api.governance import require_session
from arth.api.problems import ProblemError
from arth.contracts.staff_add import StaffAdd
from arth.contracts.staff_login import StaffLogin
from arth.domains.catalog import get_item, public_item
from arth.domains.merchants import onboarding_view, settings_view
from arth.domains.resolution import resolve
from arth.domains.tables import devices, shifts
from arth.governance.commands import CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import staff

router = APIRouter()
Actor = Annotated[Session, Depends(require_session)]
Key = Annotated[str, Header(min_length=1, max_length=200)]
CATALOG_EVENTS = ["catalog.item_added", "catalog.price_changed"]


@router.post("/v1/staff/login")
async def login(request: Request, body: StaffLogin, idempotency_key: Key) -> dict[str, Any]:
    await require_token(body.channel.value)(request)
    try:
        return await request.app.state.staff.login(
            body.device_credential, body.staff_id, body.pin, body.channel.value, idempotency_key
        )
    except CommandError as exc:
        raise ProblemError(401, str(exc), "error." + str(exc), title="Login refused") from exc


@router.post("/v1/staff")
async def add_staff(request: Request, body: StaffAdd, session: Actor, idempotency_key: Key) -> dict[str, Any]:
    return await request.app.state.staff.add(session, body.name, body.role.value, body.pin, idempotency_key)


@router.get("/v1/catalog/search")
async def search(
    request: Request, session: Actor, q: Annotated[str, Query(min_length=1, max_length=200)]
) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).search_catalog(q)
        return {"items": [public_item(row) for row in rows], "invalidate_on": CATALOG_EVENTS}


@router.get("/v1/catalog/resolve")
async def resolution(
    request: Request, session: Actor, q: Annotated[str, Query(min_length=1, max_length=200)]
) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await resolve(Repository(conn, session.merchant_id), q)


@router.get("/v1/views/settings/language")
async def language(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return {
            **await settings_view(Repository(conn, session.merchant_id)),
            "invalidate_on": ["i18n.changed"],
        }


@router.get("/v1/views/onboarding")
async def onboarding(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await onboarding_view(Repository(conn, session.merchant_id))


@router.get("/v1/views/settings/staff")
async def staff_settings(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).select(staff)
        return {
            "staff": [{k: r[k] for k in ("id", "name", "role")} for r in rows],
            "invalidate_on": ["staff.added"],
        }


@router.get("/v1/views/staff/login")
async def staff_login_view(request: Request, x_device_credential: Annotated[str, Header()]) -> dict[str, Any]:
    await require_token("device")(request)
    try:
        mid, device_id = request.app.state.staff.device_identity(x_device_credential)
    except CommandError as exc:
        raise ProblemError(401, str(exc), "error." + str(exc), title="Invalid device") from exc
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, mid)
        if not await repo.select(devices, devices.c.id == device_id):
            raise ProblemError(
                401, "auth.invalid_device", "error.auth.invalid_device", title="Invalid device"
            )
        return {
            "staff": [{k: r[k] for k in ("id", "name", "role")} for r in await repo.select(staff)],
            "invalidate_on": ["staff.added"],
        }


@router.get("/v1/views/shift")
async def shift(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).select(
            shifts, shifts.c.staff_id == session.actor_id, shifts.c.closed_at.is_(None)
        )
        return {
            "current": {k: v for k, v in rows[0].items() if k != "merchant_id"} if rows else None,
            "invalidate_on": ["staff.shift_opened", "staff.shift_closed"],
        }


@router.get("/v1/views/item/{item_id}")
async def item_view(request: Request, item_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return {
            **await get_item(Repository(conn, session.merchant_id), item_id),
            "invalidate_on": CATALOG_EVENTS,
        }
