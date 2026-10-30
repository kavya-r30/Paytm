"""Growth read models (T6.1–T6.11): grow, plans, campaigns, bundles, Growth Ledger; guardrail auto-stop."""

import json
from typing import Any

from fastapi import APIRouter, Request

from arth.api.commerce import Actor
from arth.core.clock import iso_utc
from arth.governance.commands import CommandError
from arth.governance.events import emit_event
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import merchants
from arth.growth.engine import bundles, campaign_row, credit_advice, diagnostics, ledger, levers
from arth.growth.tables import campaigns, growth_plans, preorders
from arth.sim.peers import peers_view

router = APIRouter()
GROWTH_TOPICS = ["growth.updated", "bill.paid", "preorder.changed", "stock.demand_logged"]


def plan_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "goal_key": row["goal_key"],
        "status": row["status"],
        "budget_paise": row["budget_paise"],
        "levers": json.loads(row["levers"]),
    }


@router.get("/v1/views/grow")
async def grow(request: Request, session: Actor) -> dict[str, Any]:
    state = request.app.state
    async with state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        pack = (await repo.select(merchants))[0]["pack"]
        return {
            "diagnostics": await diagnostics(repo, state.clock),
            "peers": await peers_view(conn, pack),
            "levers": await levers(repo, state.clock, state.packs),
            "plans": [plan_summary(r) for r in await repo.select(growth_plans)],
            "advisor": await credit_advice(repo, state.clock),
            "invalidate_on": GROWTH_TOPICS,
        }


@router.get("/v1/views/grow/plans/{plan_id}")
async def plan(request: Request, plan_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        rows = await repo.select(growth_plans, growth_plans.c.id == plan_id)
        if not rows:
            raise CommandError("growth.plan_not_found")
        row = rows[0]
        return {
            "plan": {
                **plan_summary(row),
                "holdout_bp": row["holdout_bp"],
                "diagnosis": json.loads(row["diagnosis"]),
            },
            "campaigns": [
                await campaign_row(repo, c)
                for c in await repo.select(campaigns, campaigns.c.plan_id == plan_id)
            ],
            "invalidate_on": GROWTH_TOPICS,
        }


@router.get("/v1/views/campaigns/{campaign_id}")
async def campaign(request: Request, campaign_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        rows = await repo.select(campaigns, campaigns.c.id == campaign_id)
        if not rows:
            raise CommandError("growth.campaign_not_found")
        return {"campaign": await campaign_row(repo, rows[0]), "invalidate_on": GROWTH_TOPICS}


@router.get("/v1/views/grow/ledger")
async def growth_ledger(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return {**await ledger(Repository(conn, session.merchant_id)), "invalidate_on": GROWTH_TOPICS}


@router.get("/v1/views/grow/bundles")
async def bundle_view(request: Request, session: Actor) -> dict[str, Any]:
    state = request.app.state
    async with state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        pack = (await repo.select(merchants))[0]["pack"]
        floor = state.packs.policies_for(pack).growth.margin_floor
        return {
            "bundles": await bundles(repo, floor),
            "preorders": [
                {k: r[k] for k in ("id", "patron_id", "total_paise", "deposit_paise", "status")}
                for r in await repo.select(preorders)
            ],
            "invalidate_on": GROWTH_TOPICS,
        }


def install_guardrails(dispatcher: Any, clock: Any) -> None:
    """FBK-3/GRW-14: a complaint (or a low rating) stops every running campaign at once."""

    async def guard(repo: Repository, event: dict[str, Any]) -> None:
        if event["type"] != "feedback.recorded" or not event["payload"].get("low"):
            return
        for row in await repo.select(campaigns, campaigns.c.status == "running"):
            await repo.update(
                campaigns,
                {"status": "stopped", "stop_reason": "guardrail.complaint"},
                campaigns.c.id == row["id"],
            )
            actor = Session(repo.merchant_id, "agent_guardrail", "system", actor_kind="agent")
            await emit_event(
                repo,
                clock,
                actor,
                "growth.updated",
                event["event_id"],
                {"kind": "campaign", "id": row["id"], "status": "stopped"},
            )

    dispatcher.on("growth.guardrails", guard)


__all__ = ["install_guardrails", "iso_utc"]
