import pytest
from sqlalchemy import Column, String, Table

from arth.core.db import metadata


async def test_repository_isolates_and_rejects_tenant_override(db):
    from arth.governance.repository import Repository
    from arth.governance.tables import merchants

    async with db.write() as conn:
        a = Repository(conn, "shop-a")
        b = Repository(conn, "shop-b")
        await a.insert(merchants, {"id": "shop-a", "name": "A", "pack": "kirana"})
        await b.insert(merchants, {"id": "shop-b", "name": "B", "pack": "kirana"})
        assert [r["name"] for r in await a.select(merchants)] == ["A"]
        assert await a.update(merchants, {"name": "stolen"}, merchants.c.id == "shop-b") == 0
        with pytest.raises(ValueError):
            await a.insert(merchants, {"merchant_id": "shop-b"})
        with pytest.raises(ValueError):
            await a.update(merchants, {"merchant_id": "shop-b"})


async def test_repository_rejects_unscoped_table(db):
    from arth.governance.repository import Repository

    table = Table("unscoped_probe", metadata, Column("id", String), extend_existing=True)
    try:
        async with db.read() as conn:
            with pytest.raises(ValueError):
                await Repository(conn, "a").select(table)
    finally:
        metadata.remove(table)
