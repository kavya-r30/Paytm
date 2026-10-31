"""Canonical tenant-local SHA256 audit chain (GOV-2)."""

import hashlib
import json
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.governance.repository import Repository
from arth.governance.tables import audit_log


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(previous: str, row: dict[str, Any]) -> str:
    return hashlib.sha256((previous + canonical(row)).encode()).hexdigest()


async def append_audit(
    repo: Repository, clock: SimClock, command_id: str, action: str, data: dict[str, Any]
) -> None:
    rows = sorted(await repo.select(audit_log), key=lambda r: r["seq"])
    previous = rows[-1]["hash"] if rows else ""
    row = {
        "merchant_id": repo.merchant_id,
        "command_id": command_id,
        "action": action,
        "occurred_at": iso_utc(clock.now()),
        "data": canonical(data),
        "prev_hash": previous,
    }
    await repo.insert(audit_log, {**row, "hash": ""})
    stored = max(await repo.select(audit_log), key=lambda r: r["seq"])
    await repo.update(
        audit_log, {"hash": digest(previous, {**row, "seq": stored["seq"]})}, audit_log.c.seq == stored["seq"]
    )


async def verify_audit(repo: Repository) -> dict[str, Any]:
    previous = ""
    checked = 0
    for stored in sorted(await repo.select(audit_log), key=lambda r: r["seq"]):
        row = {k: v for k, v in stored.items() if k != "hash"}
        if row["prev_hash"] != previous or digest(previous, row) != stored["hash"]:
            return {"valid": False, "checked": checked, "bad_seq": stored["seq"]}
        previous = stored["hash"]
        checked += 1
    return {"valid": True, "checked": checked, "bad_seq": None}
