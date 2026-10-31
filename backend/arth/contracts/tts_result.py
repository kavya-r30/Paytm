# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, constr


class Mode(Enum):
    live = 'live'
    replay = 'replay'
    unavailable = 'unavailable'


class TtsResult(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    text: constr(min_length=1, max_length=200)
    spoken_text: constr(max_length=2000)
    lang: constr(min_length=1, max_length=200)
    audio_b64: constr(min_length=1, max_length=200) | None
    mode: Mode
    invalidate_on: list[constr(min_length=1, max_length=200)]
