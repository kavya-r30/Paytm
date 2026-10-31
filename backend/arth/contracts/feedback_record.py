# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class TargetKind(Enum):
    order = 'order'
    bill = 'bill'


class FeedbackRecord(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    target_kind: TargetKind
    target_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    rating: conint(ge=1, le=5)
    complaint_key: (
        constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) | None
    ) = Field(
        None,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
