# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr


class Current(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1)
    staff_id: constr(min_length=1)
    opened_at: str
    closed_at: str | None = None
    float_paise: int
    expected_paise: int
    counted_paise: int | None = None
    variance_paise: int | None = None


class ShiftView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    current: Current | None
    invalidate_on: list[str]
