"""Frozen L4 turn log."""
from typing import Any

from alembic import op
from sqlalchemy import Column, String, Table, Text
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

turns = Table(
    "turns",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("session_ref", String, nullable=False),
    Column("surface", String, nullable=False),
    Column("heard", Text, nullable=False),
    Column("intent", String, nullable=False),
    Column("envelope", Text, nullable=False),
    Column("created_at", String, nullable=False),
)


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    metadata.create_all(op.get_bind())


def downgrade() -> None:
    metadata.drop_all(op.get_bind())
