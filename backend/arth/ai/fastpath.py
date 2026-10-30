"""Fast-path grammar (T4.5): the common counter and owner utterances resolve without any model call.

Each match is an *intent*: a command proposal (executed through the bus at its tier), a read (analytics tool
→ template narration) or a navigation. Quantities and amounts come from the normaliser, never from a model.
"""

import re
from dataclasses import dataclass, field
from typing import Any

from arth.ai.language import money, quantity

FILLER = r"\b(aur|ek aur|bhi|add|karo|kar do|daal do|dena|de do|please|plz|ji)\b"


@dataclass
class Intent:
    kind: str  # add_lines, remove_last, set_last_qty, pay_qr, pay_cash, khata_payment, read, nav, undo, park
    params: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


READS = [
    (r"\b(aaj|today)\b.*\b(kitna|kitni|how much)\b|\bkitna aaya\b|\baaj ki bikri\b|सेल|बिक्री", "today_sales"),
    (r"\b(khata|udhaar|udhar)\b.*\b(kitna|baaki|total)\b|\bkitna udhaar\b", "khata_total"),
    (r"\b(kya pending|pending kya|kitne kaam|needs you)\b", "pending"),
    (r"\b(kal|tomorrow)\b.*\b(bikri|sale)\b.*\b(hogi|hoga)\b|\bandaaza\b|\bforecast\b", "forecast"),
    (r"\b(stock|maal)\b.*\b(kam|khatam|low)\b|\bkya khatam\b", "low_stock"),
    (r"\bsabse zyada\b.*\b(bika|bikta)\b|\btop items?\b", "top_items"),
]
NAV = [
    (r"\bkhata (dikhao|kholo)\b|\bkhata screen\b", "khata"),
    (r"\b(stock|maal) (dikhao|kholo)\b", "stock"),
    (r"\b(hisaab|hisab) (dikhao|kholo)\b", "hisaab"),
    (r"\boffers? (dikhao|kholo)\b", "offers"),
    (r"\b(orders?) (dikhao|kholo)\b", "orders"),
    (r"\breports? (dikhao|kholo)\b", "reports"),
]


def parse(text: str) -> Intent | None:
    lowered = text.lower().strip(" .!?।")
    if not lowered:
        return None
    match = re.fullmatch(
        r"(haan|haa|ha|yes|ok|theek hai|teeno haan|sab haan|sabko haan)[, ]*"
        r"(?:(.+?) (?:ko |)(?:chhod ?ke|chhodkar|ko chhod do)|except (.+))?",
        lowered,
    )
    if match:
        return Intent("approve_all", {"exclude": (match.group(2) or match.group(3) or "").strip()})
    if re.fullmatch(r"(hatao|hata do|remove|cancel (last|ye)|nikalo)", lowered):
        return Intent("remove_last")
    if re.fullmatch(r"(woh wapas lo|undo|wapas karo|galti ho gayi)", lowered):
        return Intent("undo")
    if re.fullmatch(r"(bill rok do|park karo|rok do|hold karo)", lowered):
        return Intent("park")
    match = re.fullmatch(r"(nahi|no|nahin),?\s*(.+)", lowered)
    if match and quantity(match.group(2)):
        qty, _ = quantity(match.group(2)) or (0, None)
        return Intent("set_last_qty", {"qty_milli": qty})
    if re.search(r"\b(qr|upi) (dikhao|do|lagao)\b|\bqr\b", lowered):
        return Intent("pay_qr")
    if re.search(r"\bcash (mein|me) (lo|le lo)\b|\bcash liya\b", lowered):
        return Intent("pay_cash")
    match = re.search(r"(.+?)\s+(ne|ka|ke)\s+(.+?)\s+(jama|diye|de diye|paid|aaya)", lowered)
    if match and money(match.group(3)):
        return Intent(
            "khata_payment",
            {"who": match.group(1).replace(" ji", "").strip(), "amount_paise": money(match.group(3))},
            0.9,
        )
    for pattern, screen in NAV:
        if re.search(pattern, lowered):
            return Intent("nav", {"screen": screen})
    for pattern, tool in READS:
        if re.search(pattern, lowered):
            return Intent("read", {"tool": tool})
    lines = []
    for part in re.split(r"\s+(?:aur|and|,)\s+|,", lowered):
        part = re.sub(FILLER, " ", part).strip()
        if not part:
            continue
        by_amount = re.search(r"₹\s?\d+|\d+\s?(rupaye|rupees|rs)\b.*\bka\b|(\d+|₹\d+) ka\b", part)
        if by_amount:
            amount = money(part)
            name = re.sub(r"₹\s?\d+|\d+\s?(rupaye|rupees|rs)?|\bka\b|\bki\b|\bke\b", " ", part).strip()
            if amount and name:
                lines.append({"text": name, "amount_paise": amount})
            continue
        found = quantity(part)
        qty = found[0] if found else 1000
        name = re.sub(
            r"\b\d+(\.\d+)?\b|\b(ek|do|teen|char|chaar|paanch|aadha|adha|pav|dedh|dhai|kilo|kg|gram|"
            r"packet|pkt|litre|piece|dabba|strip|cup)\b",
            " ",
            part,
        )
        name = re.sub(r"\s+", " ", name).strip()
        if name:
            lines.append({"text": name, "qty_milli": qty})
    if lines:
        return Intent("add_lines", {"lines": lines}, 0.85)
    return None
