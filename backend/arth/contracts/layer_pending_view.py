# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, constr


class Status(Enum):
    needs_more_data = 'needs_more_data'
    not_built_yet = 'not_built_yet'


class Layer(Enum):
    L3 = 'L3'
    L4 = 'L4'
    L5 = 'L5'
    L6 = 'L6'


class LayerPendingView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    screen: constr(min_length=1, max_length=200)
    status: Status
    layer: Layer
    reason_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    items: list[dict[str, Any]]
    invalidate_on: list[constr(min_length=1, max_length=200)]
