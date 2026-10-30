# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class Decision(Enum):
    approve = 'approve'
    snooze = 'snooze'
    edit = 'edit'
    decline = 'decline'


class Decisions(Enum):
    approve = 'approve'
    snooze = 'snooze'
    decline = 'decline'


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    decision: Decision
    edits: dict[str, Any] | None = None
    decisions: dict[str, Decisions] | None = None
