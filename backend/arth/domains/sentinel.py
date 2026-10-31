"""Sentinel: reconcile what a payment screenshot claims against the ledger (SEN-1…3).

The verdict comes only from the ledger. Supporting signals (payee, time, UTR format, image replay, edit
level) are listed for the owner but never decide anything. User-facing wording is dignified: the screen
says "payment abhi tak nahi aaya", never that a customer cheated.
"""

import json
import re
from datetime import timedelta
from typing import Any

from arth.core.clock import iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.commerce_tables import payment_events, payments, sentinel_checks, sentinel_signals
from arth.domains.merchants import domain_event, settings_view
from arth.domains.patron_identity import identity_value
from arth.governance.commands import CommandBus
from arth.governance.repository import Repository

HEADLINES = {
    "received": "sentinel.received",
    "not_received": "sentinel.not_received_yet",
    "pending": "sentinel.pending",
    "unclear": "sentinel.unclear",
}
UTR_PATTERN = re.compile(r"^[0-9]{12}$")
EDITED_BP = 6000
PLAUSIBLE = timedelta(hours=48)


async def _status(repo: Repository, payment_id: str) -> str:
    rows = await repo.select(payment_events, payment_events.c.payment_id == payment_id)
    return max(rows, key=lambda r: r["seq"])["status"] if rows else "success"


async def reconcile(repo: Repository, fields: dict[str, Any], now: str) -> tuple[str, dict[str, Any] | None]:
    """Verdict from the ledger only. Without a UTR, an amount match alone is never 'received'."""
    if fields.get("utr"):
        rows = await repo.select(payments, payments.c.utr == fields["utr"])
        if not rows:
            return "not_received", None
        row = rows[0]
        status = await _status(repo, row["id"])
        if status == "pending":
            return "pending", row
        if status != "success":
            return "not_received", row
        return ("received" if row["amount_paise"] == fields["amount_paise"] else "unclear"), row
    candidates = [
        r
        for r in await repo.select(payments, payments.c.amount_paise == fields["amount_paise"])
        if r["source"] == "rails" and await _status(repo, r["id"]) == "success"
    ]
    if fields.get("paid_at"):
        claimed = parse_iso(fields["paid_at"])
        candidates = [
            r for r in candidates if abs(parse_iso(r["received_at"]) - claimed) <= timedelta(minutes=15)
        ]
    return ("unclear" if candidates else "not_received"), None


async def signals(repo: Repository, fields: dict[str, Any], now: str) -> list[dict[str, str]]:
    result = []
    vpa = (await settings_view(repo)).get("vpa")
    if fields.get("payee_ref") and vpa:
        expected = identity_value(repo.merchant_id, "vpa", vpa)[1]
        result.append({"kind": "payee", "state": "match" if fields["payee_ref"] == expected else "mismatch"})
    if fields.get("paid_at"):
        claimed = parse_iso(fields["paid_at"])
        plausible = parse_iso(now) - PLAUSIBLE <= claimed <= parse_iso(now) + timedelta(minutes=5)
        result.append({"kind": "time", "state": "plausible" if plausible else "implausible"})
    if fields.get("utr"):
        result.append(
            {"kind": "utr_format", "state": "valid" if UTR_PATTERN.fullmatch(fields["utr"]) else "invalid"}
        )
    if fields.get("phash"):
        seen = await repo.select(sentinel_checks, sentinel_checks.c.phash == fields["phash"])
        result.append({"kind": "image_replay", "state": "seen_before" if seen else "new"})
    if fields.get("ela_score_bp") is not None:
        result.append(
            {"kind": "edit_level", "state": "high" if fields["ela_score_bp"] >= EDITED_BP else "low"}
        )
    return result


async def verdict_view(repo: Repository, check_id: str) -> dict[str, Any]:
    rows = await repo.select(sentinel_checks, sentinel_checks.c.id == check_id)
    if not rows:
        from arth.governance.commands import CommandError

        raise CommandError("sentinel.check_not_found")
    row = rows[0]
    fields = json.loads(row["fields"])
    ledger = (
        (await repo.select(payments, payments.c.id == row["payment_id"]))[0] if row["payment_id"] else None
    )
    evidence = []
    for kind, claimed, actual in [
        ("amount", fields.get("amount_paise"), ledger["amount_paise"] if ledger else None),
        ("utr", fields.get("utr"), ledger["utr"] if ledger else None),
        ("time", fields.get("paid_at"), ledger["received_at"] if ledger else None),
    ]:
        if actual is None or claimed is None:
            state = "missing"
        elif kind == "time":
            close = abs(parse_iso(str(claimed)) - parse_iso(str(actual))) <= timedelta(minutes=15)
            state = "match" if close else "mismatch"
        else:
            state = "match" if str(claimed) == str(actual) else "mismatch"
        evidence.append(
            {
                "kind": kind,
                "claimed": None if claimed is None else str(claimed),
                "ledger": None if actual is None else str(actual),
                "state": state,
            }
        )
    return {
        "check_id": row["id"],
        "verdict": row["verdict"],
        "headline_key": HEADLINES[row["verdict"]],
        "evidence": evidence,
        "signals": [
            {"kind": r["kind"], "state": r["state"]}
            for r in await repo.select(sentinel_signals, sentinel_signals.c.check_id == row["id"])
        ],
        "footnote_key": "sentinel.ledger_only",
        "invalidate_on": ["sentinel.verdict", "payment.received"],
    }


def register_sentinel(bus: CommandBus) -> None:
    async def check(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        now = iso_utc(bus.clock.now())
        verdict, payment = await reconcile(repo, payload, now)
        found = await signals(repo, payload, now)
        identity = new_id("sentinel")
        await repo.insert(
            sentinel_checks,
            {
                "id": identity,
                "verdict": verdict,
                "fields": json.dumps(payload),
                "payment_id": payment["id"] if payment else None,
                "phash": payload.get("phash"),
                "occurred_at": now,
            },
        )
        for signal in found:
            await repo.insert(sentinel_signals, {"id": new_id("signal"), "check_id": identity, **signal})
        await domain_event(bus, repo, "sentinel.verdict", {"check_id": identity, "verdict": verdict})
        return {
            "check_id": identity,
            "verdict": verdict,
            "headline_key": HEADLINES[verdict],
            "signals": found,
        }

    bus.register("sentinel.check", schema("sentinel_check"), check)
