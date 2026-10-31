# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, constr


class Role(Enum):
    owner = 'owner'
    manager = 'manager'
    cashier = 'cashier'
    helper = 'helper'


class StaffItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1)
    name: str
    role: Role


class StaffView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    staff: list[StaffItem]
    invalidate_on: list[str]
