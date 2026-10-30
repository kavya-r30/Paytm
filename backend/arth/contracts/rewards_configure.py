# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, conint


class RewardsConfigure(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    threshold: conint(ge=1)
    value_paise: conint(ge=0)
    budget_paise: conint(ge=0)
