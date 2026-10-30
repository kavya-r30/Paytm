# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, constr


class MemoryPropose(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    subject: constr(min_length=1, max_length=200)
    predicate: constr(min_length=1, max_length=200)
    value: constr(min_length=1, max_length=200)
    evidence: list[constr(min_length=1, max_length=200)] = Field(
        ..., max_length=20, min_length=0
    )
