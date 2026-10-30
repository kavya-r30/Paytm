# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, conint

from . import khata_account_view


class KhataView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    accounts: list[khata_account_view.KhataAccountView]
    balance_paise: conint(ge=0)
    advance_paise: conint(ge=0)
    invalidate_on: list[str]
