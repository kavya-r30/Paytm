# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, constr

from . import common


class NeedsYouItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    gate_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    thread_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    tier: common.Tier
    type: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    expires_at: AwareDatetime
    title_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    summary_params: dict[str, str | int | None]


class DoneItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    command_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    type: constr(min_length=1, max_length=200)
    tier: common.Tier
    occurred_at: AwareDatetime
    undo_until: AwareDatetime | None
    bill_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None = (
        Field(
            ...,
            description='Bill of an undoable line command (counter.undo takes the bill); null for everything else.',
        )
    )


class SnoozedItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    gate_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    thread_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    tier: common.Tier
    type: constr(min_length=1, max_length=200)
    status: constr(min_length=1, max_length=200)
    expires_at: AwareDatetime
    title_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    summary_params: dict[str, str | int | None]


class NotificationsView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    needs_you: list[NeedsYouItem]
    done: list[DoneItem]
    snoozed: list[SnoozedItem]
    invalidate_on: list[constr(min_length=1, max_length=200)]
