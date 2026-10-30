"""Deterministic item resolution; ambiguity is data, never an arbitrary choice."""

import math
import re
import unicodedata
from collections.abc import Awaitable, Callable
from difflib import SequenceMatcher
from typing import Any

from arth.domains.catalog import public_item
from arth.domains.tables import item_aliases, items
from arth.governance.repository import Repository

EmbeddingHook = Callable[[str, list[dict[str, Any]]], Awaitable[dict[str, float]]]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join("".join(char if unicodedata.category(char)[0] in "LNM" else " " for char in text).split())


CONSONANTS = dict(
    zip(
        "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
        [
            "k",
            "kh",
            "g",
            "gh",
            "ng",
            "ch",
            "chh",
            "j",
            "jh",
            "ny",
            "t",
            "th",
            "d",
            "dh",
            "n",
            "t",
            "th",
            "d",
            "dh",
            "n",
            "p",
            "ph",
            "b",
            "bh",
            "m",
            "y",
            "r",
            "l",
            "v",
            "sh",
            "sh",
            "s",
            "h",
        ],
        strict=True,
    )
)
VOWELS = dict(zip("अआइईउऊऋएऐओऔ", ["a", "aa", "i", "ii", "u", "uu", "ri", "e", "ai", "o", "au"], strict=True))
SIGNS = dict(zip("ािीुूृेैोौ", ["aa", "i", "ii", "u", "uu", "ri", "e", "ai", "o", "au"], strict=True))


def transliterate(text: str) -> str:
    words = []
    for word in normalize(text).split():
        out = ""
        devanagari = False
        for char in word:
            if char in CONSONANTS:
                out += CONSONANTS[char] + "a"
                devanagari = True
            elif char in SIGNS:
                out = out.removesuffix("a") + SIGNS[char]
            elif char == "्":
                out = out.removesuffix("a")
            elif char in VOWELS:
                out += VOWELS[char]
                devanagari = True
            elif char in "ंँ":
                out += "n"
            elif char != "़":
                out += char
        if devanagari:
            out = out.removesuffix("a")
        words.append(re.sub(r"([aeiou])\1+", r"\1", out).replace("ee", "i").replace("oo", "u"))
    return " ".join(words)


async def resolve(repo: Repository, text: str, embedding_hook: EmbeddingHook | None = None) -> dict[str, Any]:
    query = normalize(text)
    rows = await repo.select(items)
    aliases: dict[str, list[str]] = {row["id"]: [] for row in rows}
    for alias in await repo.select(item_aliases):
        if alias["item_id"] in aliases:
            aliases[alias["item_id"]].append(alias["alias"])
    candidates = [public_item(row) for row in rows]

    def response(stage: str, scores: dict[str, float]) -> dict[str, Any]:
        ranked = sorted(
            (
                dict(row, confidence=round(scores[row["id"]], 4))
                for row in candidates
                if scores.get(row["id"], 0) >= 0.72
            ),
            key=lambda r: (-r["confidence"], -r["frequency"], r["id"]),
        )[:5]
        ambiguous = len(ranked) > 1 and ranked[0]["confidence"] - ranked[1]["confidence"] < 0.08
        return {
            "stage": stage,
            "candidates": ranked,
            "selected": ranked[0] if ranked and not ambiguous else None,
            "needs_clarification": ambiguous,
            "invalidate_on": ["catalog.item_added", "catalog.price_changed"],
        }

    if not query or not rows:
        return response("none", {})
    names = {row["id"]: [*row["names"].values(), row["sku"]] for row in candidates}
    exact = {
        identity: 1.0 for identity, values in names.items() if query in [normalize(value) for value in values]
    }
    if exact:
        return response("normalize", exact)
    exact = {
        identity: 1.0
        for identity, values in aliases.items()
        if query in [normalize(value) for value in values]
    }
    if exact:
        return response("alias", exact)
    keys = {
        identity: [transliterate(value) for value in names[identity] + aliases[identity]]
        for identity in names
    }
    roman = transliterate(text)
    exact = {identity: 0.98 for identity, values in keys.items() if roman in values}
    if exact:
        return response("transliteration", exact)
    fuzzy = {
        identity: max(SequenceMatcher(None, roman, value).ratio() for value in values)
        for identity, values in keys.items()
    }
    result = response("fuzzy", fuzzy)
    if result["candidates"]:
        return result
    if embedding_hook:
        scores = await embedding_hook(text, candidates)
        safe = {
            identity: float(score)
            for identity, score in scores.items()
            if identity in names and type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1
        }
        return response("embedding", safe)
    return response("none", {})
