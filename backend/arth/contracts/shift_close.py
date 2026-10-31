# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, conint, constr


class ShiftClose(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    shift_id: constr(min_length=1)
    counted_paise: conint(ge=0)
