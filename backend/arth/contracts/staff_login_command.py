# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, constr


class Channel(Enum):
    device = 'device'
    console = 'console'


class StaffLoginCommand(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    staff_id: constr(min_length=1)
    device_id: constr(min_length=1)
    channel: Channel
