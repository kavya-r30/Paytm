"""Authenticated Stock, Patrons and Khata read models; mutations use the bus."""

from typing import Annotated, Any

from fastapi import APIRouter, Query, Request

from arth.api.commerce import Actor, Key
from arth.contracts.patrons_add import PatronsAdd
from arth.contracts.patrons_update_profile import PatronsUpdateProfile
from arth.domains.ledger import account_view, khata_view, statement
from arth.domains.ledger_projection import promise_status
from arth.domains.ledger_tables import (
    credit_accounts,
    payable_allocations,
    payables,
    promises,
)
from arth.domains.patron_identity import related_ids, resolve_identity
from arth.domains.patron_tables import patrons
from arth.domains.patrons import patron_view
from arth.domains.stock import expiry_view, stock_view
from arth.governance.commands import CommandError
from arth.governance.repository import Repository
from arth.governance.tables import merchants

router = APIRouter()


@router.post("/v1/patrons")
async def add_patron(
    request: Request, body: PatronsAdd, session: Actor, idempotency_key: Key
) -> dict[str, Any]:
    return await request.app.state.patrons.submit(
        session, "patrons.add", body.model_dump(mode="json", exclude_unset=True), idempotency_key
    )


@router.patch("/v1/patrons")
async def update_patron(
    request: Request, body: PatronsUpdateProfile, session: Actor, idempotency_key: Key
) -> dict[str, Any]:
    return await request.app.state.patrons.submit(
        session, "patrons.update_profile", body.model_dump(mode="json", exclude_unset=True), idempotency_key
    )


@router.get("/v1/views/stock")
async def stock(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await stock_view(Repository(conn, session.merchant_id), request.app.state.clock)


@router.get("/v1/views/expiry")
async def expiry(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        shops = await repo.select(merchants)
        policy = request.app.state.packs.policies_for(shops[0]["pack"])
        window = policy.expiry_alert_days.get(shops[0]["pack"], policy.expiry_alert_days["default"])
        return await expiry_view(repo, request.app.state.clock, window)


@router.get("/v1/views/customers/search")
async def customers(
    request: Request, session: Actor, q: Annotated[str, Query(min_length=1, max_length=200)]
) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        result = await resolve_identity(repo, "spoken_name", q)
        rows = {r["id"]: r for r in await repo.select(patrons, patrons.c.erased == 0)}
        return {
            "customers": [
                {**r, "display_name": rows[r["patron_id"]]["display_name"]} for r in result["candidates"]
            ],
            "needs_clarification": result["needs_clarification"],
            "invalidate_on": ["patron.changed", "patron.merged"],
        }


@router.get("/v1/views/patron/{patron_id}")
async def patron(request: Request, patron_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await patron_view(Repository(conn, session.merchant_id), patron_id)


@router.get("/v1/views/khata")
async def khata(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await khata_view(Repository(conn, session.merchant_id), request.app.state.clock)


@router.get("/v1/views/khata/{patron_id}")
async def account(request: Request, patron_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        rows = await repo.select(
            credit_accounts, credit_accounts.c.patron_id.in_(await related_ids(repo, patron_id))
        )
        if not rows:
            raise CommandError("ledger.account_not_found")
        return await account_view(repo, rows[0]["id"], request.app.state.clock)


@router.get("/v1/views/statement/{account_id}")
async def statement_view(request: Request, account_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await statement(Repository(conn, session.merchant_id), account_id, request.app.state.clock)


@router.get("/v1/views/promises")
async def promise_view(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        result = []
        for row in await repo.select(promises):
            status = await promise_status(repo, row, request.app.state.clock)
            result.append(
                {k: row[k] for k in ("id", "account_id", "amount_paise", "due_on")} | {"status": status}
            )
        return {"promises": result, "invalidate_on": ["credit.changed"]}


@router.get("/v1/views/payables")
async def payable_view(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        result = []
        for row in await repo.select(payables):
            paid = sum(
                r["amount_paise"]
                for r in await repo.select(payable_allocations, payable_allocations.c.payable_id == row["id"])
            )
            result.append(
                {k: row[k] for k in ("id", "supplier_ref", "amount_paise", "due_on")}
                | {"paid_paise": paid, "balance_paise": row["amount_paise"] - paid}
            )
        return {"payables": result, "invalidate_on": ["credit.payable_changed"]}
