# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, confloat, conint, constr


class Stage(Enum):
    none = 'none'
    normalize = 'normalize'
    alias = 'alias'
    transliteration = 'transliteration'
    fuzzy = 'fuzzy'
    embedding = 'embedding'


class Details(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    salt: constr(min_length=1, max_length=200) | None = None
    strength: constr(min_length=1, max_length=200) | None = None
    form: constr(min_length=1, max_length=200) | None = None
    pack_size: constr(min_length=1, max_length=200) | None = None
    schedule: constr(min_length=1, max_length=200) | None = None
    rx_required: bool | None = None
    duration_minutes: conint(ge=1) | None = None
    required_skill: constr(min_length=1, max_length=200) | None = None


class Candidate(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1)
    sku: str
    names: dict[str, constr(min_length=1)] = Field(..., min_length=1)
    unit: str
    category: str | None = None
    mrp_paise: int | None = None
    price_paise: int
    cost_paise: int | None = None
    details: Details | None = None
    frequency: int
    confidence: confloat(ge=0.0, le=1.0) | None = None


class Selected(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(min_length=1)
    sku: str
    names: dict[str, constr(min_length=1)] = Field(..., min_length=1)
    unit: str
    category: str | None = None
    mrp_paise: int | None = None
    price_paise: int
    cost_paise: int | None = None
    details: Details | None = None
    frequency: int
    confidence: confloat(ge=0.0, le=1.0) | None = None


class ResolutionView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    stage: Stage
    candidates: list[Candidate] = Field(..., max_length=5)
    selected: Selected | None
    needs_clarification: bool
    invalidate_on: list[str]
