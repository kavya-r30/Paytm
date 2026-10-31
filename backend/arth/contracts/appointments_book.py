# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr


class Source(Enum):
    device = 'device'
    whatsapp = 'whatsapp'
    storefront = 'storefront'


class AppointmentsBook(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    service_item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = (
        Field(
            ...,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    staff_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    start_at: AwareDatetime
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        Field(
            None,
            description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
        )
    )
    source: Source
