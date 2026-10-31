# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, constr


class ActionsSnooze(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    key: constr(min_length=1, max_length=200)
    until: AwareDatetime
