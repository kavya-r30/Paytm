# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, conint, constr


class Profile(Enum):
    unregistered = 'unregistered'
    composition = 'composition'
    regular = 'regular'


class Expense(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    category: constr(min_length=1, max_length=200)
    amount_paise: int


class Pnl(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    month: constr(pattern=r'^[0-9]{4}-(0[1-9]|1[0-2])$')
    sales_paise: int
    returns_paise: int
    cogs_paise: int
    gross_profit_paise: int
    expenses: list[Expense]
    expenses_paise: int
    reward_cost_paise: int
    net_paise: int


class Rate(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    rate_bp: conint(ge=0)
    taxable_paise: int
    cgst_paise: int
    sgst_paise: int
    total_paise: int


class Totals(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    taxable_paise: int
    cgst_paise: int
    sgst_paise: int
    total_paise: int


class Gst(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    month: constr(pattern=r'^[0-9]{4}-(0[1-9]|1[0-2])$')
    invoices: conint(ge=0)
    rates: list[Rate]
    totals: Totals


class ClosedMonth(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    month: constr(pattern=r'^[0-9]{4}-(0[1-9]|1[0-2])$')
    net_paise: int


class ScheduledItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1, max_length=200)
    cadence: constr(min_length=1, max_length=200)


class ReportsView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    month: constr(pattern=r'^[0-9]{4}-(0[1-9]|1[0-2])$')
    profile: Profile
    pnl: Pnl
    gst: Gst
    closed_months: list[ClosedMonth]
    scheduled: list[ScheduledItem]
    invalidate_on: list[constr(min_length=1, max_length=200)]
