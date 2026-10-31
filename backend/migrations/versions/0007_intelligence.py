"""Frozen L3 alerts and action snoozes."""
from typing import Any

from alembic import op
from sqlalchemy import Column, String, Table, Text, UniqueConstraint
from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "pk": "pk_%(table_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)


def tenant() -> Any:
    return Column("merchant_id", String, nullable=False, index=True)

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


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    metadata.create_all(op.get_bind())


def downgrade() -> None:
    metadata.drop_all(op.get_bind())
