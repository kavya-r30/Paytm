"""L4 state: the shared turn log (session memory across device, console and WhatsApp; T4.15)."""

from sqlalchemy import Column, String, Table, Text

from arth.core.db import metadata
from arth.governance.tables import tenant

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
