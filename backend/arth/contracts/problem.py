# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, conint, constr


class Problem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: str
    title: constr(min_length=1)
    status: conint(ge=400, le=599)
    code: constr(pattern=r'^[a-z_]+(\.[a-z_]+)+$') = Field(
        ...,
        description='A stable dotted code such as an event topic (clock.ticked) or an error code (policy.quiet_hours).',
    )
    message_key: constr(pattern=r'^[a-z0-9_]+(\.[a-z0-9_]+)+$', min_length=1) = Field(
        ...,
        description='An i18n message key: two or more dot-separated segments, e.g. chip.aaj_kitna_aaya.',
    )
    detail: str | None = None
    params: dict[str, str | int | float | bool] | None = Field(
        None, description='Values interpolated into the message_key text.'
    )
