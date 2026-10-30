# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr

from . import common


class Tier(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    tier: common.Tier
    commands: list[constr(min_length=1, max_length=200)]
    confirm_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )


class Role(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    role: constr(min_length=1, max_length=200)
    max_tier: common.Tier
    approve: list[common.Tier]


class ActivityItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    command_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    type: constr(min_length=1, max_length=200)
    tier: common.Tier
    status: constr(min_length=1, max_length=200)
    actor_id: constr(min_length=1, max_length=200) | None
    occurred_at: AwareDatetime


class Audit(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    ok: bool
    rows: conint(ge=0)


class UndoItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    command_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    type: constr(min_length=1, max_length=200)
    until: AwareDatetime


class DataSharing(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    peer_benchmarks: bool


class DataRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: constr(min_length=1, max_length=200)
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    occurred_at: AwareDatetime


class TrustView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    tiers: list[Tier]
    roles: list[Role]
    activity: list[ActivityItem]
    audit: Audit
    undo: list[UndoItem]
    data_sharing: DataSharing
    data_requests: list[DataRequest]
    invalidate_on: list[constr(min_length=1, max_length=200)]
