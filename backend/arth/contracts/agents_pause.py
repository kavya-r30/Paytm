# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, constr


class AgentsPause(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    agent: constr(min_length=1, max_length=200)
    paused: bool
