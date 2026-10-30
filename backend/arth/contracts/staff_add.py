# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, constr


class Role(Enum):
    owner = 'owner'
    manager = 'manager'
    cashier = 'cashier'
    helper = 'helper'


class StaffAdd(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    role: Role
    pin: constr(pattern=r'^[0-9]{4,8}$')
