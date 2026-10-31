# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, conint, constr


class Status(Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'


class Mode(Enum):
    upi_qr = 'upi_qr'
    upi_static = 'upi_static'
    upi_link = 'upi_link'


class TreasuryRailsEvent(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    status: Status
    utr: constr(min_length=1, max_length=200)
    amount_paise: conint(ge=1)
    mode: Mode
    order_ref: constr(min_length=1, max_length=200) | None = None
    payer_ref: constr(min_length=1, max_length=200) | None = None
    payer_name: constr(min_length=1, max_length=200) | None = None
