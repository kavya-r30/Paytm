# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class DeviceReportHealth(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    device_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    connected: bool
    battery_pct: conint(ge=0, le=100)
    mic_muted: bool
    volume_pct: conint(ge=0, le=100)
    queue_size: conint(ge=0)
    last_sync_at: AwareDatetime | None = None
