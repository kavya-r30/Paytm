"""L1d commerce records: counter, treasury, orders, supply, offers, books, trust, capital, sentinel.

Money rows are append-only (enforced by migration triggers); corrections are new rows.
"""

from typing import Any

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, Text, UniqueConstraint

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


# Counter (T1.12)
bills = record(
    "bills",
    Column("status", String, nullable=False),
    Column("patron_id", String),
    Column("staff_id", String, nullable=False),
    Column("opened_at", String, nullable=False),
    Column("closed_at", String),
    Column("total_paise", Integer),
    Column("account_id", String),
)
bill_lines = record(
    "bill_lines",
    Column("bill_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    Column("unit_price_paise", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("modifiers", Text, nullable=False, server_default="[]"),
    Column("added_via", String, nullable=False),
    Column("status", String, nullable=False, server_default="active"),
    Column("price_override", Integer, nullable=False, server_default="0"),
    Column("override_reason", String),
    Column("batch_id", String),
    Column("occurred_at", String, nullable=False),
    constraints=(
        CheckConstraint("qty_milli > 0 AND amount_paise >= 0"),
        CheckConstraint("json_valid(modifiers)"),
    ),
)
bill_ops = record(
    "bill_ops",
    Column("bill_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("line_added", String),
    Column("line_voided", String),
    Column("undone", Integer, nullable=False, server_default="0"),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
bill_payments = record(
    "bill_payments",
    Column("bill_id", String, nullable=False),
    Column("mode", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("tendered_paise", Integer),
    Column("change_paise", Integer),
    Column("ref_id", String),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(CheckConstraint("amount_paise > 0"),),
)
upi_intents = record(
    "upi_intents",
    Column("bill_id", String, nullable=False),
    Column("order_ref", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("expires_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "order_ref"), CheckConstraint("amount_paise > 0")),
)
tickets = record(
    "tickets",
    Column("bill_id", String, nullable=False),
    Column("token", Integer, nullable=False),
    Column("day", String, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
    constraints=(
        UniqueConstraint("merchant_id", "day", "token", name="uq_tickets_token"),
        UniqueConstraint("merchant_id", "bill_id", name="uq_tickets_bill"),
    ),
)
ticket_events = record(
    "ticket_events",
    Column("ticket_id", String, nullable=False),
    Column("from_state", String),
    Column("to_state", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
returns = record(
    "returns",
    Column("bill_id", String, nullable=False),
    Column("reason_key", String, nullable=False),
    Column("refund_mode", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
return_lines = record(
    "return_lines",
    Column("return_id", String, nullable=False),
    Column("line_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    sequenced=True,
    constraints=(CheckConstraint("qty_milli > 0"),),
)
rx_records = record(
    "rx_records",
    Column("bill_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("staff_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)

# Treasury (T1.13)
payments = record(
    "payments",
    Column("mode", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("utr", String),
    Column("order_ref", String),
    Column("payer_ref", String),
    Column("source", String, nullable=False),
    Column("staff_id", String),
    Column("received_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "utr"), CheckConstraint("amount_paise > 0")),
)
payment_events = record(
    "payment_events",
    Column("payment_id", String, nullable=False),
    Column("status", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
payment_matches = record(
    "payment_matches",
    Column("payment_id", String, nullable=False),
    Column("target_kind", String, nullable=False),
    Column("target_id", String, nullable=False),
    Column("matched_by", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "payment_id"),),
)
payment_exceptions = record(
    "payment_exceptions",
    Column("kind", String, nullable=False),
    Column("payment_id", String),
    Column("bill_id", String),
    Column("status", String, nullable=False),
    Column("detail", Text, nullable=False, server_default="{}"),
    Column("opened_at", String, nullable=False),
    Column("resolved_at", String),
    constraints=(CheckConstraint("json_valid(detail)"),),
)
refunds = record(
    "refunds",
    Column("payment_id", String),
    Column("bill_id", String),
    Column("amount_paise", Integer, nullable=False),
    Column("mode", String, nullable=False),
    Column("reason_key", String, nullable=False),
    Column("staff_id", String),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(CheckConstraint("amount_paise > 0"),),
)
settlements = record(
    "settlements",
    Column("external_ref", String, nullable=False),
    Column("date", String, nullable=False),
    Column("gross_paise", Integer, nullable=False),
    Column("net_paise", Integer, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "external_ref"),),
)
settlement_lines = record(
    "settlement_lines",
    Column("settlement_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("payment_id", String),
    sequenced=True,
)
expenses = record(
    "expenses",
    Column("category", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("paid_from", String, nullable=False),
    Column("note_key", String),
    Column("staff_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(CheckConstraint("amount_paise > 0"),),
)
daily_closes = record(
    "daily_closes",
    Column("date", String, nullable=False),
    Column("summary", Text, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "date"), CheckConstraint("json_valid(summary)")),
)

# Orders and appointments (T1.16)
orders = record(
    "orders",
    Column("status", String, nullable=False),
    Column("channel", String, nullable=False),
    Column("patron_id", String),
    Column("message_ref", String),
    Column("total_paise", Integer, nullable=False),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
)
order_lines = record(
    "order_lines",
    Column("order_id", String, nullable=False),
    Column("item_id", String),
    Column("text", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    Column("unit_price_paise", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("confidence_bp", Integer, nullable=False),
    Column("status", String, nullable=False, server_default="active"),
    constraints=(CheckConstraint("qty_milli > 0"),),
)
order_events = record(
    "order_events",
    Column("order_id", String, nullable=False),
    Column("from_state", String),
    Column("to_state", String, nullable=False),
    Column("actor_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
appointments = record(
    "appointments",
    Column("service_item_id", String, nullable=False),
    Column("staff_id", String),
    Column("patron_id", String),
    Column("start_at", String),
    Column("end_at", String),
    Column("status", String, nullable=False),
    Column("source", String, nullable=False),
    Column("created_at", String, nullable=False),
)
staff_skills = Table(
    "staff_skills",
    metadata,
    tenant(),
    Column("staff_id", String, nullable=False),
    Column("skill", String, nullable=False),
    UniqueConstraint("merchant_id", "staff_id", "skill"),
)

# Supply (T1.17)
suppliers = record(
    "suppliers",
    Column("name", String, nullable=False),
    Column("phone", String),
    Column("lang", String, nullable=False),
    Column("lead_days", Integer, nullable=False),
    Column("created_at", String, nullable=False),
)
purchase_orders = record(
    "purchase_orders",
    Column("supplier_id", String, nullable=False),
    Column("status", String, nullable=False),
    Column("total_paise", Integer, nullable=False),
    Column("due_on", String),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
)
po_lines = record(
    "po_lines",
    Column("po_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    Column("unit_price_paise", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    constraints=(CheckConstraint("qty_milli > 0"),),
)
quotes = record(
    "quotes",
    Column("supplier_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("unit_price_paise", Integer, nullable=False),
    Column("valid_until", String),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
grns = record(
    "grns",
    Column("po_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "po_id"),),
)
grn_lines = record(
    "grn_lines",
    Column("grn_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    Column("batch_id", String),
    sequenced=True,
)
supplier_bills = record(
    "supplier_bills",
    Column("po_id", String, nullable=False),
    Column("bill_ref", String, nullable=False),
    Column("total_paise", Integer, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "po_id"),),
)
supplier_bill_lines = record(
    "supplier_bill_lines",
    Column("bill_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    Column("unit_price_paise", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    sequenced=True,
)
grn_variances = record(
    "grn_variances",
    Column("po_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("expected", Integer, nullable=False),
    Column("actual", Integer, nullable=False),
    Column("delta_paise", Integer, nullable=False),
    sequenced=True,
)
claims = record(
    "claims",
    Column("po_id", String, nullable=False),
    Column("supplier_id", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column("lang", String, nullable=False),
    Column("created_at", String, nullable=False),
    constraints=(UniqueConstraint("merchant_id", "po_id"),),
)
price_history = record(
    "price_history",
    Column("supplier_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("unit_price_paise", Integer, nullable=False),
    Column("source", String, nullable=False),
    Column("ref_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)

# Offers (T1.18): liabilities extend the shared offer_liability rows from L1c.
offer_programs = record(
    "offer_programs",
    Column("type", String, nullable=False),
    Column("status", String, nullable=False),
    Column("rules", Text, nullable=False),
    Column("terms", Text, nullable=False),
    Column("budget_paise", Integer, nullable=False),
    Column("daily_budget_paise", Integer),
    Column("funding", String, nullable=False),
    Column("holdout_bp", Integer, nullable=False),
    Column("include_regulars", Integer, nullable=False, server_default="0"),
    Column("valid_from", String, nullable=False),
    Column("valid_until", String, nullable=False),
    Column("created_at", String, nullable=False),
    constraints=(CheckConstraint("json_valid(rules) AND json_valid(terms)"),),
)
offer_assignments = record(
    "offer_assignments",
    Column("program_id", String, nullable=False),
    Column("payer_ref", String, nullable=False),
    Column("arm", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "program_id", "payer_ref"),),
)
offer_issuances = record(
    "offer_issuances",
    Column("program_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("payer_ref", String),
    Column("patron_id", String),
    Column("amount_paise", Integer, nullable=False),
    Column("min_spend_paise", Integer, nullable=False),
    Column("code", String),
    Column("item_id", String),
    Column("source_ref", String, nullable=False),
    Column("funding", String, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "code"), CheckConstraint("amount_paise > 0")),
)
offer_events = record(
    "offer_events",
    Column("issuance_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("ref_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "issuance_id", "kind"),),
)

# Tax and books (T1.19)
invoices = record(
    "invoices",
    Column("bill_id", String, nullable=False),
    Column("number", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("profile", String, nullable=False),
    Column("month", String, nullable=False),
    Column("taxable_paise", Integer, nullable=False),
    Column("cgst_paise", Integer, nullable=False),
    Column("sgst_paise", Integer, nullable=False),
    Column("total_paise", Integer, nullable=False),
    Column("issued_at", String, nullable=False),
    sequenced=True,
    constraints=(
        UniqueConstraint("merchant_id", "bill_id", name="uq_invoices_bill"),
        UniqueConstraint("merchant_id", "number", name="uq_invoices_number"),
    ),
)
invoice_lines = record(
    "invoice_lines",
    Column("invoice_id", String, nullable=False),
    Column("item_id", String, nullable=False),
    Column("hsn", String, nullable=False),
    Column("rate_bp", Integer, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("taxable_paise", Integer, nullable=False),
    Column("cgst_paise", Integer, nullable=False),
    Column("sgst_paise", Integer, nullable=False),
    sequenced=True,
)
month_closes = record(
    "month_closes",
    Column("month", String, nullable=False),
    Column("pnl", Text, nullable=False),
    Column("gst", Text, nullable=False),
    Column("occurred_at", String, nullable=False),
    constraints=(
        UniqueConstraint("merchant_id", "month"),
        CheckConstraint("json_valid(pnl) AND json_valid(gst)"),
    ),
)

# Storefront, feedback, privacy, device (T1.20)
storefront_settings = Table(
    "storefront_settings",
    metadata,
    tenant(),
    Column("slug", String, nullable=False, unique=True),
    Column("published", Integer, nullable=False),
    Column("show_offers", Integer, nullable=False),
    Column("updated_at", String, nullable=False),
    UniqueConstraint("merchant_id"),
)
ratings = record(
    "ratings",
    Column("target_kind", String, nullable=False),
    Column("target_id", String, nullable=False),
    Column("rating", Integer, nullable=False),
    Column("patron_id", String),
    Column("complaint_key", String),
    Column("occurred_at", String, nullable=False),
    constraints=(
        UniqueConstraint("merchant_id", "target_kind", "target_id"),
        CheckConstraint("rating BETWEEN 1 AND 5"),
    ),
)
data_requests = record(
    "data_requests",
    Column("kind", String, nullable=False),
    Column("patron_id", String, nullable=False),
    Column("command_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)
data_sharing = Table(
    "data_sharing",
    metadata,
    tenant(),
    Column("peer_benchmarks", Integer, nullable=False),
    Column("updated_at", String, nullable=False),
    UniqueConstraint("merchant_id"),
)
device_health = record(
    "device_health",
    Column("device_id", String, nullable=False),
    Column("connected", Integer, nullable=False),
    Column("battery_pct", Integer, nullable=False),
    Column("mic_muted", Integer, nullable=False),
    Column("volume_pct", Integer, nullable=False),
    Column("queue_size", Integer, nullable=False),
    Column("last_sync_at", String),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
)

# Capital (T1.21): read models plus Console-only applications.
loan_offers = record(
    "loan_offers",
    Column("lender", String, nullable=False),
    Column("amount_paise", Integer, nullable=False),
    Column("tenor_days", Integer, nullable=False),
    Column("apr_bp", Integer, nullable=False),
    Column("edi_paise", Integer, nullable=False),
    Column("processing_fee_paise", Integer, nullable=False),
    Column("kfs_url", String, nullable=False),
    Column("cooling_off_days", Integer, nullable=False),
    Column("purpose_ref", String),
    Column("expires_at", String, nullable=False),
    Column("received_at", String, nullable=False),
)
loan_applications = record(
    "loan_applications",
    Column("offer_id", String, nullable=False),
    Column("status", String, nullable=False),
    Column("staff_id", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(UniqueConstraint("merchant_id", "offer_id"),),
)

# Sentinel (T1.22)
sentinel_checks = record(
    "sentinel_checks",
    Column("verdict", String, nullable=False),
    Column("fields", Text, nullable=False),
    Column("payment_id", String),
    Column("phash", String),
    Column("occurred_at", String, nullable=False),
    sequenced=True,
    constraints=(CheckConstraint("json_valid(fields)"),),
)
sentinel_signals = record(
    "sentinel_signals",
    Column("check_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("state", String, nullable=False),
    sequenced=True,
)

APPEND_ONLY = (
    "bill_payments",
    "ticket_events",
    "returns",
    "return_lines",
    "rx_records",
    "payments",
    "payment_events",
    "payment_matches",
    "refunds",
    "settlements",
    "settlement_lines",
    "expenses",
    "order_events",
    "quotes",
    "grns",
    "grn_lines",
    "supplier_bills",
    "supplier_bill_lines",
    "grn_variances",
    "price_history",
    "offer_assignments",
    "offer_issuances",
    "offer_events",
    "invoices",
    "invoice_lines",
    "data_requests",
    "device_health",
    "sentinel_checks",
    "sentinel_signals",
)
