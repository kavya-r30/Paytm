# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr


class BooksCloseMonth(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    month: constr(pattern=r'^[0-9]{4}-(0[1-9]|1[0-2])$')
