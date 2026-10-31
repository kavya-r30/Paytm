# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, conint, constr


class OfflineQueue(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    size: conint(ge=0)
    last_sync_at: AwareDatetime | None


class Mode(Enum):
    live = 'live'
    fallback = 'fallback'
    replay = 'replay'
    unknown = 'unknown'


class Provider(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: constr(min_length=1, max_length=200)
    configured: bool
    mode: Mode


class Backup(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    last_snapshot_at: AwareDatetime | None


class HealthView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    device: dict[str, Any] | None
    offline_queue: OfflineQueue
    providers: list[Provider]
    ai_spend_today_paise: conint(ge=0)
    backup: Backup
    invalidate_on: list[constr(min_length=1, max_length=200)]
