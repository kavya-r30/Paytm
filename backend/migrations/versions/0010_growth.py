"""Frozen L6 hints, plans, campaigns, assignments, pre-orders."""
from typing import Any

from alembic import op
from sqlalchemy import Column, Integer, String, Table, Text, UniqueConstraint
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

hints = Table(
    "hints",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("bill_id", String, nullable=False),
    Column("patron_id", String, nullable=False),
    Column("item_id", String),
    Column("arm", String, nullable=False),
    Column("reason_key", String, nullable=False),
    Column("accepted", Integer, nullable=False, server_default="0"),
    Column("created_at", String, nullable=False),
    UniqueConstraint("merchant_id", "bill_id"),
)
growth_plans = Table(
    "growth_plans",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("goal_key", String, nullable=False),
    Column("levers", Text, nullable=False),
    Column("budget_paise", Integer, nullable=False),
    Column("holdout_bp", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("diagnosis", Text, nullable=False),
    Column("created_at", String, nullable=False),
)
campaigns = Table(
    "campaigns",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("plan_id", String, nullable=False),
    Column("lever", String, nullable=False),
    Column("template", String, nullable=False),
    Column("status", String, nullable=False),
    Column("stop_reason", String),
    Column("created_at", String, nullable=False),
)
campaign_assignments = Table(
    "campaign_assignments",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("campaign_id", String, nullable=False),
    Column("patron_id", String, nullable=False),
    Column("arm", String, nullable=False),
    Column("sent", Integer, nullable=False),
    Column("reason", String),
    Column("created_at", String, nullable=False),
    UniqueConstraint("merchant_id", "campaign_id", "patron_id"),
)
preorders = Table(
    "preorders",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("patron_id", String, nullable=False),
    Column("items", Text, nullable=False),
    Column("total_paise", Integer, nullable=False),
    Column("deposit_paise", Integer, nullable=False),
    Column("advance_ref", String, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", String, nullable=False),
)


revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    metadata.create_all(op.get_bind())


def downgrade() -> None:
    metadata.drop_all(op.get_bind())
