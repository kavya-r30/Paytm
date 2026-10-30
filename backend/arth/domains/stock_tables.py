"""Append-only inventory and receipt-batch metadata."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant

batches = Table(
    "batches",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("batch_no", String, nullable=False),
    Column("expires_on", String),
    Column("received_at", String, nullable=False),
    Column("mrp_paise", Integer, nullable=False),
    Column("cost_paise", Integer, nullable=False),
    Column("recalled", Integer, nullable=False, server_default="0"),
    UniqueConstraint("merchant_id", "item_id", "batch_no"),
    CheckConstraint("mrp_paise >= 0 AND cost_paise >= 0"),
)
stock_moves = Table(
    "stock_moves",
    metadata,
    Column("seq", Integer, primary_key=True),
    Column("id", String, nullable=False, unique=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("batch_id", String),
    Column("delta_qty_milli", Integer, nullable=False),
    Column("reason", String, nullable=False),
    Column("ref_id", String, nullable=False),
    Column("buyer_id", String),
    Column("occurred_at", String, nullable=False),
)
stock_counts = Table(
    "stock_counts",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("batch_id", String),
    Column("counted_qty_milli", Integer, nullable=False),
    Column("previous_qty_milli", Integer, nullable=False),
    Column("command_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    CheckConstraint("counted_qty_milli >= 0"),
)
unmet_demand = Table(
    "unmet_demand",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("text", String, nullable=False),
    Column("item_id", String),
    Column("occurred_at", String, nullable=False),
)
