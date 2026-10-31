"""Inbound messages (verified messaging webhooks) and owner-added local calendar events (T2.3, T2.10)."""

from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.merchants import domain_event, owner_only
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository
from arth.sim.tables import local_events, messages_in


def register_inbox(bus: CommandBus) -> None:
    async def receive(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        # Customer text is untrusted data (ORD-5, AIQ-6): it is stored, never executed.
        if repo.session is None or repo.session.role != "system" or not repo.private.get("message_verified"):
            raise CommandError("messages.verified_webhook_required")
        identity = new_id("msgin")
        await repo.insert(
            messages_in,
            {
                "id": identity,
                "thread_ref": payload["thread_ref"],
                "persona_ref": payload["persona_ref"],
                "patron_id": payload.get("patron_id"),
                "supplier_id": payload.get("supplier_id"),
                "kind": payload["kind"],
                "text": payload["text"],
                "received_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(
            bus,
            repo,
            "message.in",
            {
                "message_id": identity,
                "persona_ref": payload["persona_ref"],
                "patron_id": payload.get("patron_id"),
                "supplier_id": payload.get("supplier_id"),
            },
        )
        return {"message_id": identity}

    async def local_event(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if payload["end"] < payload["start"]:
            raise CommandError("calendar.invalid_range")
        identity = new_id("levent")
        await repo.insert(local_events, {"id": identity, **payload, "created_at": iso_utc(bus.clock.now())})
        await domain_event(bus, repo, "calendar.local_event_added", {"event_id": identity})
        return {"event_id": identity}

    bus.register("messages.receive", schema("messages_receive"), receive)
    bus.register("calendar.add_local_event", schema("calendar_add_local_event"), local_event)
