"""SQLAlchemy Core tables owned by L0. Later layers add their own table modules."""

from __future__ import annotations

from sqlalchemy import Column, Float, Integer, String, Table, Text

from arth.core.db import metadata

jobs = Table(
    "jobs",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("due_at", String, nullable=False, index=True),
    Column("every_seconds", Integer, nullable=True),
    Column("daily_at", String, nullable=True),
    Column("payload", Text, nullable=False, server_default="{}"),
    Column("status", String, nullable=False, server_default="pending"),
    Column("attempts", Integer, nullable=False, server_default="0"),
    Column("last_error", Text, nullable=True),
    Column("ran_at", String, nullable=True),
)

spans = Table(
    "spans",
    metadata,
    Column("id", String, primary_key=True),
    Column("trace_id", String, nullable=False, index=True),
    Column("parent_id", String, nullable=True),
    Column("kind", String, nullable=False),
    Column("name", String, nullable=False),
    Column("start_at", String, nullable=False),
    Column("dur_ms", Float, nullable=False),
    Column("mode", String, nullable=False, server_default="none"),
    Column("cost_paise", Integer, nullable=False, server_default="0"),
    Column("attrs", Text, nullable=False, server_default="{}"),
)
