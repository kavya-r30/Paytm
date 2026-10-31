# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, conint, constr


class Status(Enum):
    ready = 'ready'
    insufficient_peers = 'insufficient_peers'


class Metric(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    metric: constr(min_length=1, max_length=200)
    p10: int
    p25: int
    p50: int
    p75: int
    p90: int


class PeersView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    pack: constr(min_length=1, max_length=200)
    status: Status
    n: conint(ge=0)
    metrics: list[Metric]
    invalidate_on: list[constr(min_length=1, max_length=200)]
