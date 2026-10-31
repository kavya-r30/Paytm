"""Identity matching never infers households or grants consent."""

import hashlib
import unicodedata
from difflib import SequenceMatcher
from typing import Any

from arth.domains.patron_tables import consents, patron_identities, patron_links, patrons
from arth.domains.resolution import normalize
from arth.governance.commands import CommandError
from arth.governance.repository import Repository

PURPOSES = ("marketing", "reminders", "receipts")


def identity_value(merchant_id: str, kind: str, value: str) -> tuple[str, str]:
    if kind in {"vpa", "vpa_hash"}:
        return "vpa_hash", hashlib.sha256((merchant_id + "|" + value.strip().casefold()).encode()).hexdigest()
    if kind == "phone":
        digits = "".join(str(unicodedata.digit(char)) for char in value if char.isdecimal())
        if not 10 <= len(digits) <= 15:
            raise CommandError("patron.invalid_phone")
        return kind, digits
    if kind not in {"spoken_name", "payer_name"}:
        raise CommandError("patron.invalid_identity_kind")
    return kind, normalize(value)


async def patron_row(repo: Repository, identity: str) -> dict[str, Any]:
    rows = await repo.select(patrons, patrons.c.id == identity, patrons.c.erased == 0)
    if not rows:
        raise CommandError("patron.not_found")
    return rows[0]


async def canonical_patron(repo: Repository, identity: str) -> str:
    await patron_row(repo, identity)
    links = {row["source_id"]: row["target_id"] for row in await repo.select(patron_links)}
    seen = set()
    while identity in links:
        if identity in seen:
            raise CommandError("patron.merge_cycle")
        seen.add(identity)
        identity = links[identity]
    return identity


async def related_ids(repo: Repository, identity: str) -> list[str]:
    root = await canonical_patron(repo, identity)
    ids = {root}
    for row in await repo.select(patron_links):
        if await canonical_patron(repo, row["source_id"]) == root:
            ids.add(row["source_id"])
    return sorted(ids)


async def resolve_identity(repo: Repository, kind: str, value: str) -> dict[str, Any]:
    kind, key = identity_value(repo.merchant_id, kind, value)
    scores: dict[str, float] = {}
    for row in await repo.select(patron_identities, patron_identities.c.kind == kind):
        score = (
            1.0
            if row["value"] == key
            else min(0.89, SequenceMatcher(None, row["value"], key).ratio())
            if kind in {"spoken_name", "payer_name"}
            else 0
        )
        if score >= 0.6:
            try:
                identity = await canonical_patron(repo, row["patron_id"])
            except CommandError:
                continue
            scores[identity] = max(scores.get(identity, 0), score)
    candidates: list[dict[str, Any]] = [
        {"patron_id": identity, "confidence": round(score, 4)}
        for identity, score in sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))[:5]
    ]
    selected = (
        candidates[0]["patron_id"]
        if candidates
        and candidates[0]["confidence"] > 0.9
        and (len(candidates) == 1 or candidates[0]["confidence"] - candidates[1]["confidence"] >= 0.08)
        else None
    )
    return {
        "selected": selected,
        "candidates": candidates,
        "needs_clarification": bool(candidates and selected is None),
    }


async def has_consent(repo: Repository, identity: str, purpose: str) -> bool:
    if purpose not in PURPOSES:
        return False
    ids = await related_ids(repo, identity)
    rows = await repo.select(consents, consents.c.patron_id.in_(ids), consents.c.purpose == purpose)
    for patron in ids:
        history = [row for row in rows if row["patron_id"] == patron]
        if not history or not max(history, key=lambda row: row["seq"])["granted"]:
            return False
    return True
