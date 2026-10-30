"""L5 state: playbook runs and steps, work items, contact locks, agent controls, memory facts, briefs."""

from sqlalchemy import Column, Integer, String, Table, Text, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant

playbook_runs = Table(
    "playbook_runs",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("playbook", String, nullable=False),
    Column("agent", String, nullable=False),
    Column("subject", String, nullable=False),
    Column("status", String, nullable=False),
    Column("step", String, nullable=False),
    Column("context", Text, nullable=False),
    Column("wait_topic", String),
    Column("wait_match", Text),
    Column("wait_until", String),
    Column("cost_paise", Integer, nullable=False, server_default="0"),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
)
playbook_steps = Table(
    "playbook_steps",
    metadata,
    Column("seq", Integer, primary_key=True),
    Column("id", String, nullable=False, unique=True),
    tenant(),
    Column("run_id", String, nullable=False),
    Column("step", String, nullable=False),
    Column("status", String, nullable=False),
    Column("detail", Text, nullable=False),
    Column("occurred_at", String, nullable=False),
)
work_items = Table(
    "work_items",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("kind", String, nullable=False),
    Column("agent", String, nullable=False),
    Column("run_id", String),
    Column("title_key", String, nullable=False),
    Column("params", Text, nullable=False),
    Column("urgency", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", String, nullable=False),
)
contact_locks = Table(
    "contact_locks",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("subject", String, nullable=False),
    Column("run_id", String, nullable=False),
    Column("until", String, nullable=False),
    UniqueConstraint("merchant_id", "subject"),
)
agent_controls = Table(
    "agent_controls",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("agent", String, nullable=False),
    Column("paused", Integer, nullable=False),
    Column("updated_at", String, nullable=False),
    UniqueConstraint("merchant_id", "agent"),
)
memory_facts = Table(
    "memory_facts",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("subject", String, nullable=False),
    Column("predicate", String, nullable=False),
    Column("value", Text, nullable=False),
    Column("evidence", Text, nullable=False),
    Column("source", String, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", String, nullable=False),
)
briefs = Table(
    "briefs",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("date", String, nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", String, nullable=False),
    UniqueConstraint("merchant_id", "date"),
)
