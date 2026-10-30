# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, constr


class SessionResult(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    token: str
    staff_id: constr(min_length=1)
    expires_at: AwareDatetime
