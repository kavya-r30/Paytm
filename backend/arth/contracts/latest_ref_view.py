# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, constr


class Kind(StrEnum):
    bill_open = 'bill_open'
    bill_closed = 'bill_closed'
    gate = 'gate'
    po = 'po'
    claim = 'claim'
    offer = 'offer'
    plan = 'plan'
    campaign = 'campaign'
    run = 'run'
    order = 'order'
    verdict = 'verdict'
    item = 'item'
    patron = 'patron'


class LatestRefView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: Kind
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    invalidate_on: list[str]
