"""Frozen L1c stock, patrons and ledger schema."""
from sqlalchemy import MetaData
from alembic import op
from sqlalchemy import Column, String
metadata=MetaData(naming_convention={'ix':'ix_%(table_name)s_%(column_0_name)s','uq':'uq_%(table_name)s_%(column_0_name)s','pk':'pk_%(table_name)s','fk':'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s'})
def tenant():
    return Column('merchant_id',String,nullable=False,index=True)
"""Append-only inventory and receipt-batch metadata."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, UniqueConstraint




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


"""Patron identity, consent, households and immutable reward accounting."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, UniqueConstraint




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


def record(name, *columns, sequenced=False, constraints=()):
    identity = (
        [Column("seq", Integer, primary_key=True), Column("id", String, nullable=False, unique=True)]
        if sequenced else [Column("id", String, primary_key=True)]
    )
    return Table(name, metadata, *identity, tenant(), *columns, *constraints)


credit_accounts = record("credit_accounts",
    Column("patron_id", String, nullable=False), Column("limit_paise", Integer, nullable=False),
    Column("created_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "patron_id"), CheckConstraint("limit_paise >= 0")))
credit_entries = record("credit_entries",
    Column("account_id", String, nullable=False), Column("amount_paise", Integer, nullable=False),
    Column("source", String, nullable=False), Column("ref_id", String), Column("member_id", String),
    Column("reversal_of", String), Column("occurred_at", String, nullable=False), sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "reversal_of"),))
credit_entry_lines = record("credit_entry_lines",
    Column("entry_id", String, nullable=False), Column("item_id", String), Column("description_key", String),
    Column("qty_milli", Integer, nullable=False), Column("unit_price_paise", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False))
credit_entry_events = record("credit_entry_events",
    Column("entry_id", String, nullable=False), Column("status", String, nullable=False),
    Column("occurred_at", String, nullable=False), sequenced=True)
ledger_payments = record("ledger_payments",
    Column("account_id", String, nullable=False), Column("payment_ref", String, nullable=False),
    Column("amount_paise", Integer, nullable=False), Column("mode", String, nullable=False),
    Column("link_ref", String), Column("result", String, nullable=False), Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "payment_ref"), CheckConstraint("amount_paise > 0 AND json_valid(result)")))
credit_allocations = record("credit_allocations",
    Column("account_id", String, nullable=False), Column("entry_id", String, nullable=False),
    Column("payment_ref", String, nullable=False), Column("amount_paise", Integer, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "payment_ref", "entry_id"), CheckConstraint("amount_paise > 0")))
advances = record("advances",
    Column("account_id", String, nullable=False), Column("amount_paise", Integer, nullable=False),
    Column("source_ref", String, nullable=False), Column("purpose_ref", String),
    Column("occurred_at", String, nullable=False), sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "source_ref"), CheckConstraint("amount_paise > 0")))
advance_applications = record("advance_applications",
    Column("account_id", String, nullable=False), Column("advance_id", String, nullable=False),
    Column("amount_paise", Integer, nullable=False), Column("ref_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "advance_id", "ref_id"), CheckConstraint("amount_paise > 0")))
promises = record("promises",
    Column("account_id", String, nullable=False), Column("amount_paise", Integer, nullable=False),
    Column("due_on", String, nullable=False), Column("occurred_at", String, nullable=False))
reminders = record("reminders",
    Column("account_id", String, nullable=False), Column("patron_id", String, nullable=False),
    Column("link_id", String, nullable=False), Column("template_key", String, nullable=False),
    Column("balance_paise", Integer, nullable=False), Column("command_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "link_id", name="uq_reminders_link"), UniqueConstraint("merchant_id", "command_id", name="uq_reminders_command")))
payables = record("payables",
    Column("supplier_ref", String, nullable=False), Column("amount_paise", Integer, nullable=False),
    Column("due_on", String, nullable=False), Column("source_ref", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "source_ref"), CheckConstraint("amount_paise > 0")))
payable_allocations = record("payable_allocations",
    Column("payable_id", String, nullable=False), Column("amount_paise", Integer, nullable=False),
    Column("payment_ref", String, nullable=False), Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "payment_ref"), CheckConstraint("amount_paise > 0")))


revision='0004'
down_revision='0003'
branch_labels=None
depends_on=None

def upgrade():
    metadata.create_all(op.get_bind())
    for table in ('stock_moves','stock_counts','consents','patron_links','reward_ledger','offer_liability','credit_entries','credit_entry_lines','credit_entry_events','ledger_payments','credit_allocations','advances','advance_applications','promises','reminders','payables','payable_allocations'):
        for action in ('UPDATE','DELETE'):
            op.execute(f"CREATE TRIGGER {table}_no_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'append-only {table}'); END")

def downgrade():
    metadata.drop_all(op.get_bind())
