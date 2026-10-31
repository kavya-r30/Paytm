"""Simulator state (the bank, the phone network, the lender) plus L2 domain tables.

`sim_*` tables belong to simulated outside parties, not to Arth: they are written directly by the
simulators. `local_events` and `messages_in` are Arth domain tables and change only through the bus.
"""

from typing import Any

from sqlalchemy import Column, Integer, String, Table, Text, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant


def record(name: str, *columns: Column[Any], constraints: tuple[Any, ...] = ()) -> Table:
    return Table(name, metadata, Column("id", String, primary_key=True), tenant(), *columns, *constraints)


sim_rails_orders = record(
    "sim_rails_orders",
    Column("order_ref", String, nullable=False),
    Column("token", String, nullable=False, unique=True),
    Column("amount_paise", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("expires_at", String, nullable=False),
)
sim_rails_payments = record(
    "sim_rails_payments",
    Column("utr", String, nullable=False, unique=True),
    Column("order_ref", String),
    Column("mode", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("payer_vpa", String, nullable=False),
    Column("payer_name", String, nullable=False),
    Column("status", String, nullable=False),
    Column("platform_offer_paise", Integer, nullable=False, server_default="0"),
    Column("settled", Integer, nullable=False, server_default="0"),
    Column("created_at", String, nullable=False),
)
sim_rails_cashbacks = record(
    "sim_rails_cashbacks",
    Column("payment_ref", String, nullable=False),
    Column("program_ref", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("funding", String, nullable=False),
    Column("created_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "payment_ref", "program_ref"),),
)
sim_rails_refunds = record(
    "sim_rails_refunds",
    Column("refund_ref", String, nullable=False, unique=True),
    Column("amount_paise", Integer, nullable=False),
    Column("created_at", String, nullable=False),
)
sim_rails_faults = record(
    "sim_rails_faults",
    Column("kind", String, nullable=False),
    Column("remaining", Integer, nullable=False),
    Column("arg", Integer, nullable=False, server_default="0"),
)
sim_rails_settlements = record(
    "sim_rails_settlements",
    Column("date", String, nullable=False),
    Column("gross_paise", Integer, nullable=False),
    Column("net_paise", Integer, nullable=False),
    Column("lines", Text, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "date"),),
)
sim_threads = record(
    "sim_threads",
    Column("persona_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("phone", String, nullable=False),
    Column("role", String, nullable=False),
    Column("lang", String, nullable=False),
    Column("patron_id", String),
    Column("supplier_id", String),
    constraints=(UniqueConstraint("merchant_id", "persona_id"),),
)
sim_messages = record(
    "sim_messages",
    Column("thread_id", String, nullable=False),
    Column("direction", String, nullable=False),
    Column("category", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("body", Text, nullable=False),
    Column("source_ref", String),
    Column("created_at", String, nullable=False),
)
sim_lender_apps = record(
    "sim_lender_apps",
    Column("offer_id", String, nullable=False, unique=True),
    Column("status", String, nullable=False),
    Column("principal_paise", Integer, nullable=False),
    Column("edi_paise", Integer, nullable=False),
    Column("days_left", Integer, nullable=False),
    Column("created_at", String, nullable=False),
)
sim_peer_metrics = Table(
    "sim_peer_metrics",
    metadata,
    Column("pack", String, nullable=False),
    Column("metric", String, nullable=False),
    Column("n", Integer, nullable=False),
    Column("p10", Integer, nullable=False),
    Column("p25", Integer, nullable=False),
    Column("p50", Integer, nullable=False),
    Column("p75", Integer, nullable=False),
    Column("p90", Integer, nullable=False),
    UniqueConstraint("pack", "metric"),
)

# Arth domain tables added in L2 (bus writes only)
local_events = record(
    "local_events",
    Column("name", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("start", String, nullable=False),
    Column("end", String, nullable=False),
    Column("created_at", String, nullable=False),
)
messages_in = record(
    "messages_in",
    Column("thread_ref", String, nullable=False),
    Column("persona_ref", String, nullable=False),
    Column("patron_id", String),
    Column("supplier_id", String),
    Column("kind", String, nullable=False),
    Column("text", Text, nullable=False),
    Column("received_at", String, nullable=False),
)
