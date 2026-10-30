from l1b_helpers import make_bus

from arth.core.ids import new_id
from arth.domains.catalog import register_catalog
from arth.domains.merchants import provision_shop
from arth.governance.policy import Session


async def fixture_shop(db, key=None):
    bus = make_bus(db)
    register_catalog(bus, bus.packs)
    shop = await provision_shop(
        bus, "Fixture", "kirana", "Owner", "4826", new_id("device"), key=key or new_id("seed")
    )
    actor = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
    item = {
        "sku": "SALT",
        "names": {"en": "Salt"},
        "unit": "pcs",
        "mrp_paise": 3000,
        "price_paise": 2700,
        "cost_paise": 2000,
        "category": "staples",
    }
    item_id = (await bus.submit(actor, "catalog.add_item", item, "item"))["data"]["item_id"]
    return bus, actor, item_id
