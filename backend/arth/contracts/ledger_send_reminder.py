# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, constr


class LedgerSendReminder(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    account_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    template_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    manual: bool | None = Field(
        None,
        description='The owner sends this reminder now, by hand: quiet hours, weekly cap, minimum age and spacing do not apply (consent, a due balance and no dispute still do; agents cannot set it).',
    )
