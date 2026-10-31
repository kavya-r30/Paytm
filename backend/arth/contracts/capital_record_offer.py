# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class CapitalRecordOffer(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    lender: constr(min_length=1, max_length=200)
    amount_paise: conint(ge=1)
    tenor_days: conint(ge=1, le=1095)
    apr_bp: conint(ge=0, le=6000)
    edi_paise: conint(ge=1)
    processing_fee_paise: conint(ge=0)
    kfs_url: constr(min_length=1, max_length=200)
    cooling_off_days: conint(ge=0, le=30)
    purpose_ref: (
        constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    ) = Field(
        None,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    expires_at: AwareDatetime
