"""L1b identity and catalog tables (all domain queries are merchant scoped)."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, Text, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant

devices = Table(
    "devices",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("edition", String, nullable=False),
    Column("capabilities", Text, nullable=False, server_default="{}"),
    CheckConstraint("json_valid(capabilities)"),
)
onboarding_progress = Table(
    "onboarding_progress",
    metadata,
    tenant(),
    Column("step", String, nullable=False),
    Column("completed_at", String, nullable=False),
    UniqueConstraint("merchant_id", "step"),
)
staff_credentials = Table(
    "staff_credentials",
    metadata,
    Column("staff_id", String, primary_key=True),
    tenant(),
    Column("pin_hash", Text, nullable=False),
    Column("failed", Integer, nullable=False, server_default="0"),
    Column("locked_until", String),
)
staff_sessions = Table(
    "staff_sessions",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("staff_id", String, nullable=False),
    Column("device_id", String, nullable=False),
    Column("channel", String, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("revoked", Integer, nullable=False, server_default="0"),
)
shifts = Table(
    "shifts",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("staff_id", String, nullable=False),
    Column("opened_at", String, nullable=False),
    Column("closed_at", String),
    Column("float_paise", Integer, nullable=False),
    Column("expected_paise", Integer, nullable=False),
    Column("counted_paise", Integer),
    Column("variance_paise", Integer),
    CheckConstraint("float_paise >= 0 AND expected_paise >= 0"),
)

items = Table(
    "items",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("sku", String, nullable=False),
    Column("names", Text, nullable=False),
    Column("unit", String, nullable=False),
    Column("category", String, nullable=False),
    Column("mrp_paise", Integer, nullable=False),
    Column("price_paise", Integer, nullable=False),
    Column("cost_paise", Integer, nullable=False),
    Column("details", Text, nullable=False, server_default="{}"),
    Column("search_text", Text, nullable=False),
    Column("frequency", Integer, nullable=False, server_default="0"),
    UniqueConstraint("merchant_id", "sku"),
    CheckConstraint("json_valid(names) AND json_valid(details)"),
    CheckConstraint("mrp_paise >= 0 AND price_paise >= 0 AND cost_paise >= 0"),
)
item_aliases = Table(
    "item_aliases",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("alias", String, nullable=False),
    UniqueConstraint("merchant_id", "item_id", "alias"),
)
item_barcodes = Table(
    "item_barcodes",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("barcode", String, nullable=False),
    UniqueConstraint("merchant_id", "barcode"),
)
item_prices = Table(
    "item_prices",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("price_paise", Integer, nullable=False),
    Column("effective_from", String, nullable=False),
    Column("command_id", String, nullable=False),
    CheckConstraint("price_paise >= 0"),
)
item_tax = Table(
    "item_tax",
    metadata,
    Column("item_id", String, primary_key=True),
    tenant(),
    Column("hsn", String, nullable=False, server_default=""),
    Column("gst_rate_bp", Integer, nullable=False, server_default="0"),
    CheckConstraint("gst_rate_bp >= 0 AND gst_rate_bp <= 10000"),
)
modifier_groups = Table(
    "modifier_groups",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("required", Integer, nullable=False),
)
modifiers = Table(
    "modifiers",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("group_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("delta_paise", Integer, nullable=False),
)
recipes = Table(
    "recipes",
    metadata,
    tenant(),
    Column("item_id", String, nullable=False),
    Column("ingredient_id", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    UniqueConstraint("merchant_id", "item_id", "ingredient_id"),
    CheckConstraint("qty_milli > 0"),
)
services = Table(
    "services",
    metadata,
    Column("item_id", String, primary_key=True),
    tenant(),
    Column("duration_minutes", Integer, nullable=False),
    Column("required_skill", String, nullable=False),
    CheckConstraint("duration_minutes > 0"),
)
