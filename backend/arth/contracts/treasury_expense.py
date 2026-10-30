# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Category(Enum):
    rent = 'rent'
    salary = 'salary'
    electricity = 'electricity'
    transport = 'transport'
    supplies = 'supplies'
    repairs = 'repairs'
    other = 'other'


class PaidFrom(Enum):
    cash = 'cash'
    upi = 'upi'
    bank = 'bank'


class TreasuryExpense(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    category: Category
    amount_paise: conint(ge=1)
    paid_from: PaidFrom
    note_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) | None = (
        Field(
            None,
            description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
        )
    )
