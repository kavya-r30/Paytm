# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class Step(Enum):
    language = 'language'
    pack = 'pack'
    details = 'details'
    catalog = 'catalog'
    people = 'people'


class OnboardingCompleteStep(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    step: Step
