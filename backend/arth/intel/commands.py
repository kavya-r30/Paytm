"""L3 commands: hourly alert scan (dedupe by key) and snoozing a next-best action (DEC-1)."""

import json
from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.merchants import domain_event
from arth.governance.commands import CommandBus
from arth.governance.repository import Repository
from arth.intel.insight import alerts
from arth.intel.tables import action_snoozes
from arth.intel.tables import alerts as alert_rows


def register_intel(bus: CommandBus, calendar: Any = None) -> None:
    async def scan(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        raised = []
        for alert in await alerts(repo, bus.clock, calendar):
            if await repo.select(alert_rows, alert_rows.c.key == alert["key"]):
                continue  # already raised once: no repeat interruptions
            identity = new_id("alert")
            await repo.insert(
                alert_rows,
                {
                    "id": identity,
                    "key": alert["key"],
                    "kind": alert["kind"],
                    "severity": alert["severity"],
                    "params": json.dumps(alert["params"]),
                    "raised_at": iso_utc(bus.clock.now()),
                },
            )
            await domain_event(
                bus,
                repo,
                "alert.raised",
                {"alert_id": identity, "kind": alert["kind"], "severity": alert["severity"]},
            )
            raised.append(identity)
        return {"raised": raised}

    async def snooze(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await repo.insert(
            action_snoozes,
            {
                "id": new_id("snooze"),
                "key": payload["key"],
                "until": payload["until"],
                "created_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(bus, repo, "action.snoozed", payload)
        return payload

    bus.register("alerts.scan", schema("alerts_scan"), scan)
    bus.register("actions.snooze", schema("actions_snooze"), snooze)


async def active_snoozes(repo: Repository, now: str) -> set[str]:
    return {r["key"] for r in await repo.select(action_snoozes) if r["until"] > now}
