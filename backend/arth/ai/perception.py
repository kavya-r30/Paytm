"""Perception and extraction (T4.11, T4.12): models read images and messages; code decides.

Every extractor has a deterministic fallback: a blocked provider degrades to "needs review", never a guess.
"""

import json
import re
from typing import Any

from arth.ai.fastpath import parse
from arth.ai.guards import Vault, injection
from arth.ai.prompts import prompt
from arth.ai.router import ProviderRouter, ProviderUnavailable
from arth.domains.resolution import resolve
from arth.governance.repository import Repository

UTR = re.compile(r"\b(\d{12})\b")
AMOUNT = re.compile(r"₹\s?([\d,]+(?:\.\d{1,2})?)")


def screenshot_fields(text: str) -> dict[str, Any]:
    """Fields from OCR text of a payment screenshot (SEN-1 input); Sentinel decides, not this function."""
    fields: dict[str, Any] = {}
    if match := AMOUNT.search(text):
        value = match.group(1).replace(",", "")
        rupees, _, paise = value.partition(".")
        fields["amount_paise"] = int(rupees) * 100 + int((paise + "00")[:2] if paise else 0)
    if match := UTR.search(text):
        fields["utr"] = match.group(1)
    return fields


async def read_screenshot(router: ProviderRouter | None, image: bytes) -> dict[str, Any]:
    if router is None:
        return {"status": "needs_review", "fields": {}}
    try:
        result = await router.ocr(image)
    except ProviderUnavailable:
        return {"status": "needs_review", "fields": {}}
    return {"status": "extracted", "fields": screenshot_fields(result.text), "mode": result.mode}


async def extract_order(repo: Repository, router: ProviderRouter | None, text: str) -> dict[str, Any]:
    """ORD-1/ORD-5: customer text → draft lines; unknown lines flagged, never guessed; injections ignored."""
    flagged = bool(injection(text))
    lines: list[dict[str, Any]] = []
    parsed = parse(text)
    candidates = parsed.params["lines"] if parsed and parsed.kind == "add_lines" else []
    if not candidates and router is not None and not flagged:
        spec = prompt("order_extract.v1")
        try:
            result = await router.chat(
                spec["role"],
                [
                    {"role": "system", "content": spec["system"]},
                    {"role": "user", "content": Vault().mask(text)},
                ],
                json_mode=True,
            )
            candidates = [
                {"text": r["text"], "qty_milli": int(float(r.get("qty", 1)) * 1000)}
                for r in json.loads(result.text or "{}").get("lines", [])
            ]
        except (ProviderUnavailable, json.JSONDecodeError, KeyError, ValueError, TypeError):
            candidates = []
    for spec in candidates:
        found = await resolve(repo, spec["text"])
        item = found["selected"]
        lines.append(
            {
                "item_id": item["id"] if item else None,
                "text": spec["text"][:200],
                "qty_milli": max(1, spec.get("qty_milli", 1000)),
                "confidence_bp": int(item["confidence"] * 10000) if item else 0,
            }
        )
    return {"lines": lines, "injection_flagged": flagged}
