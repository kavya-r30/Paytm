# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, constr


class Verdict(Enum):
    received = 'received'
    not_received = 'not_received'
    pending = 'pending'
    unclear = 'unclear'


class State(Enum):
    match = 'match'
    mismatch = 'mismatch'
    missing = 'missing'


class EvidenceItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: constr(min_length=1, max_length=200)
    claimed: constr(min_length=1, max_length=200) | None
    ledger: constr(min_length=1, max_length=200) | None
    state: State


class Signal(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: constr(min_length=1, max_length=200)
    state: constr(min_length=1, max_length=200)


class VerdictView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    check_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    verdict: Verdict
    headline_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    evidence: list[EvidenceItem]
    signals: list[Signal]
    footnote_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    invalidate_on: list[constr(min_length=1, max_length=200)]
