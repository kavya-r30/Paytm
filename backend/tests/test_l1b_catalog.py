import json
from time import perf_counter

import pytest
from l1b_helpers import make_bus

from arth.core.paths import CONTRACTS_DIR


def item():
    return json.loads((CONTRACTS_DIR / "examples/catalog_add_item.example.json").read_text(encoding="utf-8"))


async def setup_catalog(db):
    from arth.domains.catalog import register_catalog
    from arth.domains.merchants import provision_shop
    from arth.governance.policy import Session

    bus = make_bus(db)
    register_catalog(bus, bus.packs)
    shop = await provision_shop(bus, "Shop", "kirana", "Owner", "4826", "device-a", key="catalog-shop")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
    return bus, owner


async def test_catalog_import_is_confirmed_atomic_and_search_is_scoped(db):
    from arth.domains.catalog import catalog_rows
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    with pytest.raises(CommandError):
        await bus.submit(owner, "catalog.import_items", {"confirmed": False, "items": [item()]}, "unreviewed")
    added = await bus.submit(owner, "catalog.add_item", item(), "add")
    identity = added["data"]["item_id"]
    bad = {**item(), "sku": "OTHER-SALT"}
    with pytest.raises(CommandError, match="barcode"):
        await bus.submit(
            owner,
            "catalog.import_items",
            {"confirmed": True, "items": [{**item(), "sku": "NEW", "barcodes": []}, bad]},
            "collision",
        )
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        assert len(await catalog_rows(repo)) == 1
        start = perf_counter()
        results = await repo.search_catalog("टाटा")
        assert perf_counter() - start < 0.05
        assert [r["id"] for r in results] == [identity]
        assert await Repository(conn, "other").search_catalog("टाटा") == []


async def test_price_history_r2_and_r4_are_enforced(db):
    from arth.domains.catalog import catalog_rows
    from arth.domains.tables import item_prices
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    identity = (await bus.submit(owner, "catalog.add_item", item(), "add"))["data"]["item_id"]
    gate = await bus.submit(
        owner, "catalog.change_price", {"item_id": identity, "price_paise": 2600}, "price"
    )
    assert gate["status"] == "needs_approval"
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    with pytest.raises(CommandError, match="console"):
        await bus.submit(
            owner, "catalog.bulk_price", {"prices": [{"item_id": identity, "price_paise": 2500}]}, "bulk"
        )
    stepped = Session(owner.merchant_id, owner.actor_id, "owner", channel="console", step_up=True)
    await bus.submit(
        stepped, "catalog.bulk_price", {"prices": [{"item_id": identity, "price_paise": 2500}]}, "bulk"
    )
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        assert (await catalog_rows(repo))[0]["price_paise"] == 2500
        assert [r["price_paise"] for r in await repo.select(item_prices)] == [2700, 2600, 2500]


async def test_pack_fields_and_modifier_prices(db):
    from arth.domains.catalog import get_item, modifier_total, validate_pack_item
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    manifest = bus.packs.get("kirana")
    medicine = manifest.model_copy(deep=True)
    medicine.catalog.schema_ = "medicine"
    with pytest.raises(CommandError, match="medicine"):
        validate_pack_item(item(), medicine)
    service = manifest.model_copy(deep=True)
    service.catalog.schema_ = "service"
    with pytest.raises(CommandError, match="service"):
        validate_pack_item(item(), service)
    coffee = {
        **item(),
        "sku": "COFFEE",
        "barcodes": [],
        "modifier_groups": [
            {"name": "Size", "required": True, "options": [{"name": "Large", "delta_paise": 1500}]}
        ],
    }
    # Modifier groups are accepted only by the menu schema, not by a kirana SKU schema.
    menu = manifest.model_copy(deep=True)
    menu.catalog.schema_ = "menu"
    bus.packs._manifests["kirana"] = menu
    identity = (await bus.submit(owner, "catalog.add_item", coffee, "coffee"))["data"]["item_id"]
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        row = await get_item(repo, identity)
        group = row["modifier_groups"][0]
        with pytest.raises(CommandError, match="modifier"):
            await modifier_total(repo, identity, {})
        assert await modifier_total(repo, identity, {group["id"]: [group["options"][0]["id"]]}) == 4200
