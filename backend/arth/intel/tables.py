"""L3 state: raised alerts (deduplicated by key) and snoozed next-best actions."""

from sqlalchemy import Column, String, Table, Text, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant

alerts = Table(
    "alerts",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("key", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("severity", String, nullable=False),
    Column("params", Text, nullable=False),
    Column("raised_at", String, nullable=False),
    UniqueConstraint("merchant_id", "key"),
)
action_snoozes = Table(
    "action_snoozes",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("key", String, nullable=False),
    Column("until", String, nullable=False),
    Column("created_at", String, nullable=False),
)
