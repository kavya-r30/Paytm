# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, constr


class Channel(Enum):
    device = 'device'
    console = 'console'


class StaffLogin(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    device_credential: constr(min_length=1, max_length=200)
    staff_id: constr(min_length=1)
    pin: constr(pattern=r'^[0-9]{4,8}$')
    channel: Channel
