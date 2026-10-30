"""Patron identity, consent, households and immutable reward accounting."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant

patrons = Table(
    "patrons",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("display_name", String, nullable=False),
    Column("lang", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("erased", Integer, nullable=False, server_default="0"),
)
patron_identities = Table(
    "patron_identities",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("patron_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("value", String, nullable=False),
    UniqueConstraint("merchant_id", "patron_id", "kind", "value"),
)
patron_links = Table(
    "patron_links",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("source_id", String, nullable=False),
    Column("target_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    UniqueConstraint("merchant_id", "source_id"),
)
merge_proposals = Table(
    "merge_proposals",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("source_id", String, nullable=False),
    Column("target_id", String, nullable=False),
    Column("confidence_bp", Integer, nullable=False),
    Column("status", String, nullable=False),
)
consents = Table(
    "consents",
    metadata,
    Column("seq", Integer, primary_key=True),
    Column("id", String, nullable=False, unique=True),
    tenant(),
    Column("patron_id", String, nullable=False),
    Column("purpose", String, nullable=False),
    Column("granted", Integer, nullable=False),
    Column("source_ref", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    UniqueConstraint("merchant_id", "patron_id", "purpose", "source_ref"),
)
households = Table(
    "households",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("patron_id", String, nullable=False),
    UniqueConstraint("merchant_id", "patron_id"),
)
household_members = Table(
    "household_members",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("patron_id", String, nullable=False),
    Column("display_name", String, nullable=False),
    Column("active", Integer, nullable=False, server_default="1"),
)
patron_contacts = Table(
    "patron_contacts",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("patron_id", String, nullable=False),
    Column("purpose", String, nullable=False),
    Column("command_id", String, nullable=False),
    Column("status", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    UniqueConstraint("merchant_id", "command_id", "purpose"),
)
reward_programs = Table(
    "reward_programs",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("threshold", Integer, nullable=False),
    Column("value_paise", Integer, nullable=False),
    Column("budget_paise", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    CheckConstraint("threshold > 0 AND value_paise >= 0 AND budget_paise >= 0"),
)
reward_ledger = Table(
    "reward_ledger",
    metadata,
    Column("seq", Integer, primary_key=True),
    Column("id", String, nullable=False, unique=True),
    tenant(),
    Column("patron_id", String, nullable=False),
    Column("program_id", String),
    Column("kind", String, nullable=False),
    Column("source_ref", String, nullable=False),
    Column("issued_ref", String),
    Column("delta_stamps", Integer, nullable=False),
    Column("stamps_required", Integer, nullable=False, server_default="0"),
    Column("value_paise", Integer, nullable=False, server_default="0"),
    Column("occurred_at", String, nullable=False),
    UniqueConstraint("merchant_id", "kind", "source_ref"),
)
offer_liability = Table(
    "offer_liability",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("program_id", String, nullable=False),
    Column("patron_id", String),
    Column("source_ref", String, nullable=False),
    Column("date", String, nullable=False),
    Column("issued_paise", Integer, nullable=False, server_default="0"),
    Column("redeemed_paise", Integer, nullable=False, server_default="0"),
    Column("expired_paise", Integer, nullable=False, server_default="0"),
    CheckConstraint("issued_paise >= 0 AND redeemed_paise >= 0 AND expired_paise >= 0"),
)
