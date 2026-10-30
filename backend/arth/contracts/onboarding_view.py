# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OnboardingView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    steps: list[str]
    completed: list[str]
    next_step: str | None
    invalidate_on: list[str]
