"""Foundation storage; all domain rows carry explicit merchant ownership."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, Text, UniqueConstraint

from arth.core.db import metadata


def tenant() -> Column[str]:
    return Column("merchant_id", String, nullable=False, index=True)


merchants = Table(
    "merchants",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("name", String, nullable=False),
    Column("pack", String, nullable=False),
)
merchant_settings = Table(
    "merchant_settings",
    metadata,
    tenant(),
    Column("settings", Text, nullable=False, server_default="{}"),
    UniqueConstraint("merchant_id"),
    CheckConstraint("json_valid(settings)"),
)
staff = Table(
    "staff",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("role", String, nullable=False),
    Column("name", String, nullable=False),
)
commands = Table(
    "commands",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("idempotency_key", String, nullable=False),
    Column("type", String, nullable=False),
    Column("scope_hash", String, nullable=False),
    Column("tier", String, nullable=False),
    Column("status", String, nullable=False),
    Column("payload", Text, nullable=False),
    Column("result", Text, nullable=False, server_default="{}"),
    UniqueConstraint("merchant_id", "idempotency_key"),
    CheckConstraint("json_valid(payload) AND json_valid(result)"),
)
approvals = Table(
    "approvals",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("thread_id", String, nullable=False),
    Column("command_id", String, nullable=False),
    Column("scope_hash", String, nullable=False),
    Column("tier", String, nullable=False),
    Column("status", String, nullable=False),
    Column("conditions", Text, nullable=False),
    Column("scope", Text, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("due_at", String),
    Column("approved_by", String),
    CheckConstraint("json_valid(conditions) AND json_valid(scope)"),
)
audit_log = Table(
    "audit_log",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("command_id", String, nullable=False),
    Column("action", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    Column("data", Text, nullable=False),
    Column("prev_hash", String, nullable=False),
    Column("hash", String, nullable=False),
    CheckConstraint("json_valid(data)"),
)
outbox = Table(
    "outbox",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("event_id", String, nullable=False, unique=True),
    Column("type", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    Column("payload", Text, nullable=False),
    CheckConstraint("json_valid(payload)"),
)
consumer_offsets = Table(
    "consumer_offsets",
    metadata,
    tenant(),
    Column("consumer", String, nullable=False),
    Column("last_seq", Integer, nullable=False),
    UniqueConstraint("merchant_id", "consumer"),
)
