# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class GrowthCreatePlan(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    goal_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    levers: list[constr(min_length=1, max_length=200)] = Field(
        ..., max_length=6, min_length=1
    )
    budget_paise: conint(ge=0)
    holdout_bp: conint(ge=1000, le=5000)
