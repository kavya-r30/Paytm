# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, constr


class CommandRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: constr(pattern=r'^[a-z_]+(\.[a-z_]+)+$') = Field(
        ...,
        description='A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours).',
    )
    payload: dict[str, Any]
