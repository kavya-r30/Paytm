"""Interest-free credit records. Balances are projections, never mutable columns."""

from typing import Any

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant


def record(
    name: str, *columns: Column[Any], sequenced: bool = False, constraints: tuple[Any, ...] = ()
) -> Table:
    identity = (
        [Column("seq", Integer, primary_key=True), Column("id", String, nullable=False, unique=True)]
        if sequenced
        else [Column("id", String, primary_key=True)]
    )
    return Table(name, metadata, *identity, tenant(), *columns, *constraints)


credit_accounts = record(
    "credit_accounts",
    Column("patron_id", String, nullable=False),
    Column("limit_paise", Integer, nullable=False),
    Column("created_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "patron_id"), CheckConstraint("limit_paise >= 0")),
)
credit_entries = record(
    "credit_entries",
    Column("account_id", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("source", String, nullable=False),
    Column("ref_id", String),
    Column("member_id", String),
    Column("reversal_of", String),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "reversal_of"),),
)
credit_entry_lines = record(
    "credit_entry_lines",
    Column("entry_id", String, nullable=False),
    Column("item_id", String),
    Column("description_key", String),
    Column("qty_milli", Integer, nullable=False),
    Column("unit_price_paise", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False),
)
credit_entry_events = record(
    "credit_entry_events",
    Column("entry_id", String, nullable=False),
    Column("status", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
ledger_payments = record(
    "ledger_payments",
    Column("account_id", String, nullable=False),
    Column("payment_ref", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("mode", String, nullable=False),
    Column("link_ref", String),
    Column("result", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(
        UniqueConstraint("merchant_id", "payment_ref"),
        CheckConstraint("amount_paise > 0 AND json_valid(result)"),
    ),
)
credit_allocations = record(
    "credit_allocations",
    Column("account_id", String, nullable=False),
    Column("entry_id", String, nullable=False),
    Column("payment_ref", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(
        UniqueConstraint("merchant_id", "payment_ref", "entry_id"),
        CheckConstraint("amount_paise > 0"),
    ),
)
advances = record(
    "advances",
    Column("account_id", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("source_ref", String, nullable=False),
    Column("purpose_ref", String),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "source_ref"), CheckConstraint("amount_paise > 0")),
)
advance_applications = record(
    "advance_applications",
    Column("account_id", String, nullable=False),
    Column("advance_id", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("ref_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(
        UniqueConstraint("merchant_id", "advance_id", "ref_id"),
        CheckConstraint("amount_paise > 0"),
    ),
)
promises = record(
    "promises",
    Column("account_id", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("due_on", String, nullable=False),
    Column("occurred_at", String, nullable=False),
)
reminders = record(
    "reminders",
    Column("account_id", String, nullable=False),
    Column("patron_id", String, nullable=False),
    Column("link_id", String, nullable=False),
    Column("template_key", String, nullable=False),
    Column("balance_paise", Integer, nullable=False),
    Column("command_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "link_id"), UniqueConstraint("merchant_id", "command_id")),
)
payables = record(
    "payables",
    Column("supplier_ref", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("due_on", String, nullable=False),
    Column("source_ref", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "source_ref"), CheckConstraint("amount_paise > 0")),
)
payable_allocations = record(
    "payable_allocations",
    Column("payable_id", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("payment_ref", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "payment_ref"), CheckConstraint("amount_paise > 0")),
)
