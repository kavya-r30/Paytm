"""Only scoped table operations are exposed to domain handlers."""

from typing import Any

from sqlalchemy import Table, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.elements import ColumnElement

from arth.governance.policy import Session
from arth.governance.tables import merchants

# Governance bookkeeping may be written outside a command's execution (gates, audit, outbox, offsets).
# Every other table is domain state and can only change while the Command Bus executes a command.
BUS_INFRASTRUCTURE = frozenset({"commands", "approvals", "audit_log", "outbox", "consumer_offsets"})


class Repository:
    @staticmethod
    async def merchant_directory(conn: AsyncConnection) -> set[str]:
        """Startup control-plane inventory: tenant IDs only, never business rows or an HTTP API."""
        rows = await conn.execute(
            select(merchants.c.merchant_id).where(merchants.c.id == merchants.c.merchant_id)
        )
        return {str(identity) for identity in rows.scalars()}

    @staticmethod
    async def storefront_slug_owner(conn: AsyncConnection, slug: str) -> str | None:
        """Control-plane lookup: storefront slugs are globally unique; returns the owning tenant ID only."""
        from arth.domains.commerce_tables import storefront_settings

        row = await conn.execute(
            select(storefront_settings.c.merchant_id).where(storefront_settings.c.slug == slug)
        )
        found = row.scalar()
        return str(found) if found else None

    def __init__(
        self,
        conn: AsyncConnection,
        merchant_id: str,
        *,
        session: Session | None = None,
        private: dict[str, Any] | None = None,
    ) -> None:
        if not merchant_id:
            raise ValueError("merchant_id required")
        self.conn, self.merchant_id = conn, merchant_id
        self.session, self.private = session, private or {}
        self.command_id: str | None = None
        self.approval_conditions: dict[str, Any] = {}

    def _scope(self, table: Table) -> ColumnElement[bool]:
        if "merchant_id" not in table.c:
            raise ValueError("unscoped table")
        return table.c.merchant_id == self.merchant_id

    def _values(self, values: dict[str, Any]) -> dict[str, Any]:
        if "merchant_id" in values and values["merchant_id"] != self.merchant_id:
            raise ValueError("tenant override")
        return {**values, "merchant_id": self.merchant_id}

    async def select(self, table: Table, *where: ColumnElement[bool]) -> list[dict[str, Any]]:
        rows = await self.conn.execute(select(table).where(self._scope(table), *where))
        return [dict(row) for row in rows.mappings()]

    def _writable(self, table: Table) -> None:
        if table.name not in BUS_INFRASTRUCTURE and self.command_id is None:
            raise ValueError("write outside the command bus: " + table.name)

    async def insert(self, table: Table, values: dict[str, Any]) -> None:
        self._scope(table)
        self._writable(table)
        await self.conn.execute(insert(table).values(**self._values(values)))

    async def update(self, table: Table, values: dict[str, Any], *where: ColumnElement[bool]) -> int:
        self._writable(table)
        result = await self.conn.execute(
            update(table).where(self._scope(table), *where).values(**self._values(values))
        )
        return result.rowcount

    async def search_catalog(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        query = query.strip().lower()
        if not query:
            return []
        limit = min(max(limit, 1), 5)
        if len(query) >= 3:
            statement = text(
                "SELECT i.* FROM items AS i JOIN items_fts AS f "
                "ON i.id=f.id AND i.merchant_id=f.merchant_id "
                "WHERE i.merchant_id=:merchant_id AND f.merchant_id=:merchant_id "
                "AND items_fts MATCH :query ORDER BY rank, i.frequency DESC, i.id LIMIT :limit"
            )
            query = '"' + query.replace('"', '""') + '"'
        else:
            statement = text(
                "SELECT * FROM items WHERE merchant_id=:merchant_id "
                "AND instr(lower(search_text),:query)>0 ORDER BY frequency DESC,id LIMIT :limit"
            )
        rows = await self.conn.execute(
            statement, {"merchant_id": self.merchant_id, "query": query, "limit": limit}
        )
        return [dict(row) for row in rows.mappings()]
