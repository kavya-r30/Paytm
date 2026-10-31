"""L0 foundations: jobs and spans.

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("due_at", sa.String(), nullable=False),
        sa.Column("every_seconds", sa.Integer(), nullable=True),
        sa.Column("daily_at", sa.String(), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("ran_at", sa.String(), nullable=True),
    )
    op.create_index("ix_jobs_due_at", "jobs", ["due_at"])
    op.create_table(
        "spans",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("trace_id", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), nullable=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("start_at", sa.String(), nullable=False),
        sa.Column("dur_ms", sa.Float(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False, server_default="none"),
        sa.Column("cost_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attrs", sa.Text(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_spans_trace_id", "spans", ["trace_id"])


def downgrade() -> None:
    op.drop_table("spans")
    op.drop_table("jobs")
