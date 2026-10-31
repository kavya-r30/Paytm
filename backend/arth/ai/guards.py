"""Guards around every model call: PII vault (T4.6), Injection Shield (T4.7), Grounding Guard (T4.9), Critic
(T4.10) and scope classifier (T4.14). All deterministic; they run whether or not a model is reachable.
"""

import re
from dataclasses import dataclass, field
from typing import Any

from arth.ai.language import money, number, tokens

# ---- PII vault (AIQ-2): names, phones and VPAs leave the process only as placeholders ---
PHONE = re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)")
VPA = re.compile(r"\b[\w.\-]{2,}@[a-z]{2,}\b", re.I)


@dataclass
class Vault:
    names: list[str] = field(default_factory=list)
    values: dict[str, str] = field(default_factory=dict)

    def mask(self, text: str) -> str:
        def token(value: str, kind: str) -> str:
            for key, existing in self.values.items():
                if existing == value:
                    return key
            key = f"⟦{kind}{len(self.values) + 1}⟧"
            self.values[key] = value
            return key

        for name in sorted(self.names, key=len, reverse=True):
            if name and name.lower() in text.lower():
                text = re.sub(re.escape(name), lambda m: token(m.group(0), "P"), text, flags=re.I)
        text = PHONE.sub(lambda m: token(m.group(0), "T"), text)
        return VPA.sub(lambda m: token(m.group(0), "V"), text)

    def fill(self, text: str) -> str:
        for key, value in self.values.items():
            text = text.replace(key, value)
        return text


def contains_pii(text: str, names: list[str]) -> bool:
    return bool(PHONE.search(text) or VPA.search(text) or any(n and n.lower() in text.lower() for n in names))


# ---- Injection Shield (GOV-4, AIQ-6) ---
INJECTION = [
    r"ignore (all |the )?(previous|prior|above) (instructions|rules)",
    r"system prompt",
    r"you are now",
    r"act as (an? )?(admin|owner|developer)",
    r"approve (my|this|the) (order|payment|request)",
    r"\b(discount|cashback) (of )?\d{2,}\s?%",
    r"\d{2,}\s?% (discount|off|cashback)",
    r"forget (your|all) (rules|instructions)",
    r"developer mode",
    r"jailbreak",
    r"pichhle (saare )?nirdesh (bhool|ignore)",
    r"mera order approve",
    r"owner (ne|bola) .*approve",
    r"</?(system|assistant|tool)>",
    r"\bsudo\b",
]


def injection(text: str) -> list[str]:
    lowered = text.lower()
    return [p for p in INJECTION if re.search(p, lowered)]


def sanitise_metadata(value: str, limit: int = 60) -> str:
    """Untrusted metadata (payer names, captions) is shown as data only: strip markup and control text."""
    cleaned = re.sub(r"[<>{}\[\]`]|https?://\S+", "", value)
    return cleaned[:limit].strip()


# ---- Scope (AI-28, AIQ-12, PHAR-4, TAX-4) -----------------------------------------------------------------
MEDICAL = r"\b(dawai|dawa|medicine|tablet|bukhar|fever|dard|pain|dose|kaunsi dawa|prescri\w*|symptom|ilaaj)\b"
TAX_ADVICE = (
    r"\b(tax bach|tax kaise|itr|file kar|gst file|return file|tax saving|tax advice|deduction claim)\b"
)
SHOP = (
    r"\b(bikri|sale|sales|khata|udhaar|stock|bill|payment|aaya|order|supplier|customer|grahak|offer|cashback|"
    r"forecast|andaaza|kitna|hisaab|report|maal|item|paisa|diwali|loan)\b"
)


def scope(text: str, pack: str) -> str:
    lowered = text.lower()
    if re.search(MEDICAL, lowered) and not re.search(r"\b(stock|kitna|bika|bikri|order|recall)\b", lowered):
        return "medical"  # never medical advice from any chatbot (PHAR-4)
    if re.search(TAX_ADVICE, lowered):
        return "tax_advice"  # Arth reports figures, never advises (TAX-4)
    return "shop" if re.search(SHOP, lowered) else "other"


# ---- Grounding Guard (AI-7, AIQ-4) ------------------------------------------------------------------------
def numbers_in(text: str) -> set[int]:
    """Every number a sentence asserts, in base units (₹ → paise, plain numbers as integers)."""
    found: set[int] = set()
    for match in re.finditer(r"₹\s?([\d,]+(?:\.\d{1,2})?)", text):
        value = match.group(1).replace(",", "")
        rupees, _, paise = value.partition(".")
        found.add(int(rupees) * 100 + int((paise + "00")[:2] if paise else 0))
    stripped = re.sub(r"₹\s?[\d,]+(?:\.\d{1,2})?", " ", text)
    for match in re.finditer(r"(?<![\w⟦])\d[\d,]*(?![\w⟧])", stripped):
        found.add(int(match.group(0).replace(",", "")))
    return found


def allowed_numbers(values: Any) -> set[int]:
    """Numbers present in tool outputs: paise amounts also allow their whole-rupee form."""
    found: set[int] = set()

    def walk(value: Any, key: str = "") -> None:
        if isinstance(value, bool):
            return
        if isinstance(value, int):
            found.add(value)
            if key.endswith("paise"):
                found.add(value)
                if value % 100 == 0:
                    found.add(value // 100)
        elif isinstance(value, dict):
            for k, v in value.items():
                walk(v, k)
        elif isinstance(value, list):
            for v in value:
                walk(v, key)
        elif isinstance(value, str):
            found.update(numbers_in(value))

    walk(values)
    return found


def ground(text: str, facts: Any) -> list[int]:
    """Numbers in `text` that no tool output supports. Empty list = grounded."""
    allowed = allowed_numbers(facts)
    return sorted(n for n in numbers_in(text) if n not in allowed and n > 10)


# ---- Critic (AI-17, WFL-6, OFR-11) -----------------------------------------------------------------------
HARD_RULES = {
    "dignity": r"\bfake\b|\bnakli\b|\bfraud\b|\bdhokha\b",
    "interest": r"\b(interest|byaaj|vyaj|late fee|penalty|jurmana)\b",
    "medical": r"\b(take|lijiye|lo) .*(tablet|dawa|dawai|dose)\b|\bdose\b",
    "tax_advice": r"\b(tax bachane|itr file|file kar dijiye)\b",
    "fake_urgency": r"\b(sirf aaj|only today|jaldi karo|hurry|last chance|abhi nahi to kabhi nahi)\b",
    "misleading_free": r"\bfree\b",
}
EARNED = r"\b(visit|stamp|earned|10th|dasvi|\d+(st|nd|rd|th) (visit|purchase))\b"


def critic(text: str, *, outbound: bool = False) -> list[str]:
    """Hard-rule violations (recall 1.00 on the rule set). Outbound customer text gets every rule."""
    lowered = text.lower()
    rules = HARD_RULES if outbound else {k: v for k, v in HARD_RULES.items() if k not in {"fake_urgency"}}
    found = [name for name, pattern in rules.items() if re.search(pattern, lowered)]
    if "misleading_free" in found and re.search(EARNED, lowered):
        found.remove("misleading_free")  # an earned, unconditional reward may say "free" (OFR-11)
    return found


__all__ = [
    "Vault",
    "injection",
    "sanitise_metadata",
    "scope",
    "ground",
    "critic",
    "contains_pii",
    "money",
    "number",
    "tokens",
]
