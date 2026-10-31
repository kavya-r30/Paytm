# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Status(Enum):
    ready = 'ready'
    learning = 'learning'


class SufficiencyItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    feature: constr(min_length=1, max_length=200)
    status: Status
    days_of_history: conint(ge=0)
    days_needed: conint(ge=0)
    bills: conint(ge=0)
    bills_needed: conint(ge=0)
    reason_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )


class Alert(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    key: constr(min_length=1, max_length=200)
    kind: constr(min_length=1, max_length=200)
    severity: constr(min_length=1, max_length=200)
    params: dict[str, Any]
    raised_at: AwareDatetime


class Actions(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    proactive: list[dict[str, Any]]
    queued: list[dict[str, Any]]
    snoozed: list[constr(min_length=1, max_length=200)]


class DemandCluster(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    label: constr(min_length=1, max_length=200)
    count: conint(ge=1)
    demand_ids: list[constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$')]


class InsightsView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    sufficiency: list[SufficiencyItem]
    alerts: list[Alert]
    actions: Actions
    lifecycle: dict[str, int]
    demand_clusters: list[DemandCluster]
    invalidate_on: list[constr(min_length=1, max_length=200)]
