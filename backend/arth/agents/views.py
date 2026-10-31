"""Team, Run and Memory read models (T5.13, OBS-2, MEM-1) and the brief for the home screen."""

import json
from pathlib import Path
from typing import Any

import yaml

from arth.agents.tables import agent_controls, briefs, memory_facts, playbook_runs, playbook_steps, work_items
from arth.core.config import Policies
from arth.core.paths import CONFIG_DIR
from arth.governance.commands import CommandError
from arth.governance.repository import Repository
from arth.governance.tables import approvals

TIERS = ["R0", "R1", "R2", "R3", "R4"]


def load_helpers(path: Path = CONFIG_DIR / "helpers.yaml") -> list[dict[str, Any]]:
    return list(yaml.safe_load(path.read_text(encoding="utf-8"))["helpers"])


def helper_tier(helper: dict[str, Any], policies: Policies) -> str:
    tiers = [policies.tiers.get(command, "R0") for command in helper["commands"]]
    return max(tiers, key=TIERS.index) if tiers else "R0"


async def team_view(repo: Repository, policies: Policies, helpers: list[dict[str, Any]]) -> dict[str, Any]:
    runs = sorted(await repo.select(playbook_runs), key=lambda r: r["updated_at"], reverse=True)
    work = sorted(
        await repo.select(work_items, work_items.c.status == "open"),
        key=lambda r: (-r["urgency"], r["created_at"]),
    )
    controls = {r["agent"]: bool(r["paused"]) for r in await repo.select(agent_controls)}
    pending = await repo.select(approvals, approvals.c.status == "pending")
    cards = []
    for helper in helpers:
        mine = [r for r in runs if r["agent"] in helper["agents"]]
        live = [r for r in mine if r["status"] in {"ready", "waiting", "running"}]
        paused = controls.get("*") or any(controls.get(a) for a in helper["agents"])
        status = (
            "paused"
            if paused
            else "waiting"
            if any(r["status"] == "waiting" for r in live)
            else "working"
            if live
            else "idle"
        )
        cards.append(
            {
                "id": helper["id"],
                "name_key": helper["name_key"],
                "agents": helper["agents"],
                "status": status,
                "tier": helper_tier(helper, policies),
                "pending_gates": len([r for r in live if r["status"] == "waiting"]),
                "open_work": len([w for w in work if w["agent"] in helper["agents"]]),
                "line": f"{live[0]['playbook']}:{live[0]['step']}" if live else None,
            }
        )
    keys = ("id", "playbook", "agent", "subject", "status", "step", "created_at", "updated_at")
    return {
        "helpers": cards,
        "runs": [{k: r[k] for k in keys} for r in runs[:20]],
        "work": [
            {
                **{k: w[k] for k in ("id", "kind", "agent", "title_key", "urgency", "status", "created_at")},
                "params": json.loads(w["params"]),
            }
            for w in work[:20]
        ],
        "kill_switch": bool(controls.get("*")),
        "summary": {
            "done_since_night": len([r for r in runs if r["status"] == "done"]),
            "waiting_for_you": len(pending),
        },
        "invalidate_on": ["playbook.updated", "approval.requested", "approval.decided", "agents.paused"],
    }


async def run_view(repo: Repository, run_id: str) -> dict[str, Any]:
    rows = await repo.select(playbook_runs, playbook_runs.c.id == run_id)
    if not rows:
        raise CommandError("playbooks.run_not_found")
    row = rows[0]
    steps = sorted(
        await repo.select(playbook_steps, playbook_steps.c.run_id == run_id), key=lambda r: r["seq"]
    )
    keys = ("id", "playbook", "agent", "subject", "status", "step", "created_at", "updated_at")
    return {
        "run": {
            **{k: row[k] for k in keys},
            "context": json.loads(row["context"]),
            "wait": {
                "topic": row["wait_topic"],
                "match": json.loads(row["wait_match"] or "{}"),
                "until": row["wait_until"],
            }
            if row["status"] == "waiting"
            else None,
        },
        "steps": [
            {
                "step": s["step"],
                "status": s["status"],
                "detail": json.loads(s["detail"]),
                "occurred_at": s["occurred_at"],
            }
            for s in steps
        ],
        "invalidate_on": ["playbook.updated"],
    }


async def memory_view(repo: Repository) -> dict[str, Any]:
    rows = sorted(await repo.select(memory_facts), key=lambda r: r["created_at"], reverse=True)
    return {
        "facts": [
            {
                **{
                    k: r[k] for k in ("id", "subject", "predicate", "value", "source", "status", "created_at")
                },
                "evidence": json.loads(r["evidence"]),
            }
            for r in rows
        ],
        "invalidate_on": ["memory.changed"],
    }


async def latest_brief(repo: Repository) -> dict[str, Any] | None:
    rows = sorted(await repo.select(briefs), key=lambda r: r["date"])
    return json.loads(rows[-1]["content"]) if rows else None
