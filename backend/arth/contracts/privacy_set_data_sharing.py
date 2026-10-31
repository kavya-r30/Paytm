# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PrivacySetDataSharing(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    peer_benchmarks: bool
