# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, conint, constr


class SentinelCheck(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    amount_paise: conint(ge=1)
    utr: constr(min_length=1, max_length=200) | None = None
    paid_at: AwareDatetime | None = None
    payee_ref: constr(min_length=1, max_length=200) | None = None
    phash: constr(min_length=1, max_length=200) | None = None
    ela_score_bp: conint(ge=0, le=10000) | None = None
