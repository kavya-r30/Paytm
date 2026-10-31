"""Scope-bound gate primitives; decisions execute inside the command transaction."""

import hashlib
from datetime import timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.governance.audit import canonical
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import approvals


def scope_hash(kind: str, payload: dict[str, Any], conditions: dict[str, Any]) -> str:
    return hashlib.sha256((kind + canonical(payload) + canonical(conditions)).encode()).hexdigest()


def envelope(tier: str, *, needs_you: bool = False) -> dict[str, Any]:
    return {
        "turn_id": new_id("turn"),
        "lang": {"screen": "hi-Latn", "speech": "hi-IN"},
        "audience": "owner",
        "cards": [],
        "followups": [],
        "provenance": [],
        "presence": {"state": "needs_you" if needs_you else "done"},
        "sensitivity": "normal",
        "tier": tier,
    }


def can_approve(session: Session, tier: str, permissions: list[str]) -> bool:
    if session.channel == "voice" and (
        session.role != "owner" or not session.owner_ptt or not session.device_id
    ):
        return False
    return tier in permissions and (tier != "R3" or session.role == "owner")


async def create_gate(
    repo: Repository,
    clock: SimClock,
    command_id: str,
    tier: str,
    scope: dict[str, Any],
    conditions: dict[str, Any],
    hashed: str,
) -> dict[str, Any]:
    scope = {**scope, "decisions": {}}
    gate_id, thread_id = new_id("gate"), new_id("thread")
    await repo.insert(
        approvals,
        {
            "id": gate_id,
            "thread_id": thread_id,
            "command_id": command_id,
            "scope_hash": hashed,
            "tier": tier,
            "status": "pending",
            "conditions": canonical(conditions),
            "scope": canonical(scope),
            "expires_at": iso_utc(clock.now() + timedelta(hours=12)),
        },
    )
    return {
        "command_id": command_id,
        "status": "needs_approval",
        "gate_id": gate_id,
        "thread_id": thread_id,
        "tier": tier,
        "scope": {"type": scope["type"], "payload": scope["payload"], "conditions": conditions},
        "expires_at": iso_utc(clock.now() + timedelta(hours=12)),
        "envelope": envelope(tier, needs_you=True),
    }
