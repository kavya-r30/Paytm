"""L5 bus commands: replies inside a conversation, Merchant Memory with a write guard, agent pause,
playbook start/cancel. Everything an agent or the owner does here is audited like any other command.
"""

import json
from datetime import timedelta
from typing import Any

from arth.agents.tables import agent_controls, memory_facts, playbook_runs
from arth.core.clock import iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.merchants import domain_event, owner_only
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository
from arth.sim.tables import messages_in

REPLY_WINDOW = timedelta(minutes=10)  # R1 replies only inside a live conversation (v5.1 D11)
UNTRUSTED = {"customer", "supplier", "simulator", "system"}


def register_agent_commands(bus: CommandBus, runtime: Any) -> None:
    clock = bus.clock

    async def reply(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        rows = await repo.select(messages_in, messages_in.c.id == payload["message_id"])
        if not rows:
            raise CommandError("messages.not_found")
        if parse_iso(rows[0]["received_at"]) + REPLY_WINDOW < clock.now():
            raise CommandError("policy.message_class")  # outside the reply window it is outreach, not a reply
        await domain_event(
            bus,
            repo,
            "message.out",
            {
                "thread_ref": rows[0]["thread_ref"],
                "template": payload["template"],
                "params": payload["params"],
                "category": "service",
            },
        )
        return {"thread_ref": rows[0]["thread_ref"], "template": payload["template"]}

    async def propose(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        """MEM-1/AIQ-7 write guard: claims from untrusted actors are stored unverified and never used."""
        assert repo.session is not None
        kind = repo.session.actor_kind or repo.session.role
        status = "unverified" if kind in UNTRUSTED else "active"
        identity = new_id("fact")
        await repo.insert(
            memory_facts,
            {
                "id": identity,
                "subject": payload["subject"],
                "predicate": payload["predicate"],
                "value": payload["value"],
                "evidence": json.dumps(payload["evidence"]),
                "source": kind,
                "status": status,
                "created_at": iso_utc(clock.now()),
            },
        )
        await domain_event(bus, repo, "memory.changed", {"fact_id": identity, "status": status})
        return {"fact_id": identity, "status": status}

    async def transition(repo: Repository, payload: dict[str, Any], status: str) -> dict[str, Any]:
        owner_only(repo)
        if repo.session is not None and repo.session.actor_kind == "agent":
            raise CommandError("memory.owner_decides")
        rows = await repo.select(memory_facts, memory_facts.c.id == payload["fact_id"])
        if not rows:
            raise CommandError("memory.not_found")
        values: dict[str, Any] = {"status": status}
        if status == "forgotten":
            values["value"] = "forgotten"  # "Bhool jao" scrubs the content, keeps the audit trail
        await repo.update(memory_facts, values, memory_facts.c.id == payload["fact_id"])
        await domain_event(bus, repo, "memory.changed", {"fact_id": payload["fact_id"], "status": status})
        return {"fact_id": payload["fact_id"], "status": status}

    async def confirm(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return await transition(repo, payload, "active")

    async def retract(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return await transition(repo, payload, "retracted")

    async def forget(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return await transition(repo, payload, "forgotten")

    async def pause(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        values = {"paused": int(payload["paused"]), "updated_at": iso_utc(clock.now())}
        if await repo.select(agent_controls, agent_controls.c.agent == payload["agent"]):
            await repo.update(agent_controls, values, agent_controls.c.agent == payload["agent"])
        else:
            await repo.insert(agent_controls, {"id": new_id("control"), "agent": payload["agent"], **values})
        await domain_event(bus, repo, "agents.paused", payload)
        return payload

    async def start(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return {"run_id": await runtime.start_in(repo, payload["playbook"], payload["subject"])}

    async def cancel(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if not await repo.update(
            playbook_runs,
            {"status": "cancelled", "updated_at": iso_utc(clock.now())},
            playbook_runs.c.id == payload["run_id"],
        ):
            raise CommandError("playbooks.run_not_found")
        return {"run_id": payload["run_id"], "status": "cancelled"}

    for kind, handler in [
        ("messages.reply", reply),
        ("memory.propose", propose),
        ("memory.confirm", confirm),
        ("memory.retract", retract),
        ("memory.forget", forget),
        ("agents.pause", pause),
        ("playbooks.start", start),
        ("playbooks.cancel", cancel),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler)
