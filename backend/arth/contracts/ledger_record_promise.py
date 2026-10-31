# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class LedgerRecordPromise(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    account_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    amount_paise: conint(ge=1)
    due_on: date
