# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, conint


class AuditVerification(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    valid: bool
    checked: conint(ge=0)
    bad_seq: conint(ge=1) | None
