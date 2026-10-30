"""Persona engine (T2.6): persona cards with scripted and manual reply modes; LLM mode is wired in L4."""

from collections import deque
from pathlib import Path
from typing import Any

import yaml

from arth.core.paths import CONFIG_DIR


def load_personas(path: Path = CONFIG_DIR / "personas.yaml") -> dict[str, dict[str, Any]]:
    cards = yaml.safe_load(path.read_text(encoding="utf-8"))["personas"]
    return {card["id"]: card for card in cards}


class PersonaEngine:
    def __init__(self, cards: dict[str, dict[str, Any]] | None = None) -> None:
        self.cards = cards or load_personas()
        self.mode: dict[str, str] = {}
        self.manual: dict[str, deque[str]] = {}

    def set_mode(self, persona_id: str, mode: str) -> None:
        if mode not in {"scripted", "manual", "llm"}:
            raise ValueError("persona.unknown_mode")
        self.mode[persona_id] = mode

    def queue(self, persona_id: str, text: str) -> None:
        self.manual.setdefault(persona_id, deque()).append(text)

    def reply(self, persona_id: str, cue: str) -> str | None:
        card = self.cards[persona_id]
        mode = self.mode.get(persona_id, "scripted")
        if mode == "manual":
            pending = self.manual.get(persona_id)
            return pending.popleft() if pending else None
        if mode == "llm":
            raise NotImplementedError("persona LLM mode arrives with the AI platform (T4.16)")
        script: dict[str, str] = card.get("script", {})
        return script.get(cue)
