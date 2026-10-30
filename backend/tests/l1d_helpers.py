"""Hand-built fixture shops for every pack, wired exactly like the app."""

from types import SimpleNamespace

from l1b_helpers import make_bus

from arth.core.ids import new_id
from arth.domains.merchants import provision_shop
from arth.governance.policy import Session

KEY = "synthetic-l1d-signing-key"


def kirana_items() -> list[dict]:
    return [
        {
            "sku": "SUGAR",
            "names": {"en": "Sugar", "hi-Latn": "Cheeni"},
            "unit": "kg",
            "mrp_paise": 5000,
            "price_paise": 4500,
            "cost_paise": 4000,
            "category": "staples",
            "hsn": "1701",
            "gst_rate_bp": 500,
        },
        {
            "sku": "SALT",
            "names": {"en": "Salt"},
            "unit": "pcs",
            "mrp_paise": 3000,
            "price_paise": 2700,
            "cost_paise": 2000,
            "category": "staples",
            "hsn": "2501",
            "gst_rate_bp": 0,
        },
        {
            "sku": "PARLE",
            "names": {"en": "Parle-G"},
            "unit": "pcs",
            "mrp_paise": 1000,
            "price_paise": 1000,
            "cost_paise": 800,
            "category": "snacks",
            "hsn": "1905",
            "gst_rate_bp": 1800,
        },
    ]


async def _add(bus, owner, items, pack):
    ids = {}
    for spec in items[pack]:
        if pack == "cafe" and spec["sku"] == "CHAI":
            spec = {**spec, "recipe": [{"item_id": ids["MILK"], "qty_milli": 150000}]}
        ids[spec["sku"]] = (await bus.submit(owner, "catalog.add_item", spec, "item-" + spec["sku"]))["data"][
            "item_id"
        ]
    return ids


ITEMS = {
    "kirana": kirana_items(),
    "cafe": [
        {
            "sku": "MILK",
            "names": {"en": "Milk"},
            "unit": "ml",
            "mrp_paise": 6,
            "price_paise": 6,
            "cost_paise": 5,
            "category": "ingredient",
        },
        {
            "sku": "CHAI",
            "names": {"en": "Masala chai"},
            "unit": "cup",
            "mrp_paise": 2000,
            "price_paise": 2000,
            "cost_paise": 600,
            "category": "tea",
            "hsn": "9963",
            "gst_rate_bp": 500,
            "modifier_groups": [
                {
                    "name": "Size",
                    "required": True,
                    "options": [
                        {"name": "Regular", "delta_paise": 0},
                        {"name": "Large", "delta_paise": 1000},
                    ],
                },
                {"name": "Sugar", "required": False, "options": [{"name": "Less sugar", "delta_paise": 0}]},
            ],
        },
    ],
    "pharmacy": [
        {
            "sku": "PARA",
            "names": {"en": "Paracetamol 500"},
            "unit": "strip",
            "mrp_paise": 3500,
            "price_paise": 3000,
            "cost_paise": 2000,
            "category": "otc",
            "hsn": "3004",
            "gst_rate_bp": 1200,
            "details": {
                "salt": "paracetamol",
                "strength": "500mg",
                "form": "tablet",
                "pack_size": "10",
                "schedule": "otc",
                "rx_required": False,
            },
        },
        {
            "sku": "AMOX",
            "names": {"en": "Amoxicillin 250"},
            "unit": "strip",
            "mrp_paise": 9000,
            "price_paise": 9000,
            "cost_paise": 6000,
            "category": "antibiotic",
            "hsn": "3004",
            "gst_rate_bp": 1200,
            "details": {
                "salt": "amoxicillin",
                "strength": "250mg",
                "form": "capsule",
                "pack_size": "10",
                "schedule": "H",
                "rx_required": True,
            },
        },
    ],
    "salon": [
        {
            "sku": "HAIRCUT",
            "names": {"en": "Haircut"},
            "unit": "service",
            "mrp_paise": 20000,
            "price_paise": 20000,
            "cost_paise": 0,
            "category": "hair",
            "hsn": "9997",
            "gst_rate_bp": 1800,
            "details": {"duration_minutes": 30, "required_skill": "hair"},
        },
    ],
}


async def shop(db, pack="kirana", key=None):
    from arth.domains.wiring import register_commerce

    bus = make_bus(db)
    services = register_commerce(bus, bus.packs, KEY)
    key = key or new_id("seed")
    created = await provision_shop(bus, pack.title() + " Fixture", pack, "Owner", "4826", key, key=key)
    owner = Session(created["merchant_id"], created["owner_id"], "owner", channel="console")
    items = await _add(bus, owner, ITEMS, pack)
    return SimpleNamespace(
        bus=bus,
        owner=owner,
        items=items,
        services=services,
        mid=created["merchant_id"],
        device_id=created["device_id"],
        pack=pack,
    )


async def staff(s, role, key):
    added = await s.services.staff.add(s.owner, role.title(), role, "1357", "staff-" + key)
    return Session(s.mid, added["data"]["staff_id"], role, channel="device")


def system(s):
    return Session(s.mid, new_id("system"), "system", actor_kind="system")


async def run(s, kind, payload, key=None, actor=None, **kw):
    return await s.bus.submit(actor or s.owner, kind, payload, key or new_id("key"), **kw)


async def approve(s, gate, actor=None):
    assert gate["status"] == "needs_approval", gate
    return await s.bus.decide(actor or s.owner, gate["thread_id"], "approve", new_id("okay"))


async def receive(s, sku, qty, batch=None):
    payload = {"item_id": s.items[sku], "qty_milli": qty}
    if batch:
        payload["batch"] = batch
    return await run(s, "stock.receive", payload)


async def new_bill(s, lines, actor=None, patron_id=None):
    bill = (await run(s, "counter.open_bill", {"patron_id": patron_id} if patron_id else {}, actor=actor))[
        "data"
    ]["bill_id"]
    if lines:
        await run(s, "counter.add_lines", {"bill_id": bill, "lines": lines}, actor=actor)
    return bill


async def view(s, fn, *args):
    from arth.governance.repository import Repository

    async with s.bus.db.read() as conn:
        return await fn(Repository(conn, s.mid), *args)


async def patron_account(s, name="Customer", limit=500000, vpa=None):
    profile = {"display_name": name, "lang": "hi"}
    if vpa:
        profile["identities"] = [{"kind": "vpa", "value": vpa}]
    patron = (await s.services.patrons.submit(s.owner, "patrons.add", profile, new_id("pat")))["data"][
        "patron_id"
    ]
    gate = await run(s, "ledger.open_account", {"patron_id": patron, "limit_paise": limit})
    account = (await approve(s, gate))["data"]["account_id"]
    return patron, account


async def release(s):
    """Let approved R3 sends leave the 30 s send queue."""
    from datetime import timedelta

    s.bus.clock.set(s.bus.clock.now() + timedelta(seconds=31))
    return await s.bus.run_due(s.mid)
