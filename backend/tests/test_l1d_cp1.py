"""CP-1: a hand-built fixture shop per pack, driven through the real API; every J9 view is schema-valid."""

import pytest
from fastapi.testclient import TestClient
from l1d_helpers import ITEMS

from arth.core.config import Settings
from arth.core.schemas import validator
from arth.domains.merchants import provision_shop
from arth.governance.policy import Session
from arth.main import create_app

VIEWS = [
    ("home", "home_view"),
    ("ask?session=s1", "layer_pending_view"),
    ("forecast?metric=sales", "layer_pending_view"),
    ("notifications", "notifications_view"),
    ("park", "park_view"),
    ("orders", "orders_view"),
    ("stock", "stock_view"),
    ("stock/expiry", "expiry_view"),
    ("suppliers", "suppliers_view"),
    ("grow", "layer_pending_view"),
    ("grow/plans/plan_1", "layer_pending_view"),
    ("grow/demand", "demand_view"),
    ("grow/bundles", "layer_pending_view"),
    ("grow/ledger", "layer_pending_view"),
    ("campaigns/c1", "layer_pending_view"),
    ("offers", "offers_view"),
    ("storefront", "storefront_view"),
    ("team", "layer_pending_view"),
    ("runs/r1", "layer_pending_view"),
    ("memory", "layer_pending_view"),
    ("hisaab", "hisaab_view"),
    ("reports", "reports_view"),
    ("feedback", "feedback_view"),
    ("settings/language", "settings_view"),
    ("settings/staff", "staff_view"),
    ("trust", "trust_view"),
    ("health", "health_view"),
    ("capital", "capital_view"),
    ("onboarding", "onboarding_view"),
    ("shift", "shift_view"),
    ("kot", "kot_view"),
    ("appointments?date=2026-10-29", "appointments_view"),
    ("rx", "rx_view"),
    ("khata", "khata_view"),
    ("promises", "promises_view"),
    ("payables", "payables_view"),
]


@pytest.mark.parametrize("pack", ["kirana", "cafe", "pharmacy", "salon"])
def test_cp1_fixture_shop_views_valid_and_audit_verifies(tmp_path, pack):
    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path, tick_interval_s=0.05))
    with TestClient(app) as client:

        async def seed():
            shop = await provision_shop(
                app.state.commands, "Shop", pack, "Owner", "4826", "dev-" + pack, key="cp1-" + pack
            )
            return Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")

        app.state.sessions["cp1"] = client.portal.call(seed)
        auth = {"Authorization": "Bearer cp1"}
        n = iter(range(10_000))

        def command(kind, payload):
            r = client.post(
                "/v1/commands",
                json={"type": kind, "payload": payload},
                headers={**auth, "Idempotency-Key": f"k{next(n)}"},
            )
            assert r.status_code == 200, r.text
            return r.json()

        def approve(result):
            r = client.post(
                "/v1/approvals/" + result["thread_id"],
                json={"decision": "approve"},
                headers={**auth, "Idempotency-Key": f"a{next(n)}"},
            )
            assert r.status_code == 200, r.text
            return r.json()

        ids = {}
        for spec in ITEMS[pack]:
            if pack == "cafe" and spec["sku"] == "CHAI":
                spec = {**spec, "recipe": [{"item_id": ids["MILK"], "qty_milli": 150000}]}
            ids[spec["sku"]] = command("catalog.add_item", spec)["data"]["item_id"]
        sku = {"kirana": "SALT", "cafe": "MILK", "pharmacy": "PARA", "salon": "HAIRCUT"}[pack]
        if pack != "salon":
            batch = {"batch_no": "B1", "expires_on": "2027-06-30", "mrp_paise": 3500, "cost_paise": 2000}
            command(
                "stock.receive",
                {
                    "item_id": ids[sku],
                    "qty_milli": 1_000_000,
                    **({"batch": batch} if pack == "pharmacy" else {}),
                },
            )
        sell = "CHAI" if pack == "cafe" else sku
        bill = command("counter.open_bill", {})["data"]["bill_id"]
        line = {"item_id": ids[sell], "qty_milli": 1000, "added_via": "tap"}
        if pack == "cafe":
            item = client.get("/v1/views/item/" + ids["CHAI"], headers=auth).json()
            line["modifier_ids"] = [item["modifier_groups"][0]["options"][0]["id"]]
        command("counter.add_lines", {"bill_id": bill, "lines": [line]})
        if pack == "cafe":
            command("counter.send_to_kitchen", {"bill_id": bill})
        total = client.get(f"/v1/views/bill/{bill}", headers=auth).json()["bill"]["total_paise"]
        command("counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": total}]})
        command("storefront.publish", {"slug": f"cp1-{pack}", "published": True, "show_offers": True})
        order = command(
            "orders.create_draft",
            {
                "channel": "whatsapp",
                "lines": [{"item_id": ids[sell], "text": "ek", "qty_milli": 1000, "confidence_bp": 9900}],
            },
        )["data"]["order_id"]
        supplier = command("supply.add_supplier", {"name": "Dist", "lang": "hi", "lead_days": 2})["data"][
            "supplier_id"
        ]
        po = command(
            "supply.draft_po",
            {
                "supplier_id": supplier,
                "lines": [{"item_id": ids[sell], "qty_milli": 1000, "unit_price_paise": 100}],
            },
        )["data"]["po_id"]
        gate = command("supply.place_po", {"po_id": po})
        check = command("sentinel.check", {"amount_paise": 999})["data"]["check_id"]
        dynamic = [
            (f"bill/{bill}", "bill_view"),
            (f"bill/{bill}/pay", "bill_pay_view"),
            (f"bill/{bill}/paid", "bill_paid_view"),
            (f"orders/{order}", "order_view"),
            (f"po/{po}", "po_view"),
            (f"grn/{po}", "grn_view"),
            (f"gates/{gate['gate_id']}", "gate_view"),
            (f"verdict/{check}", "verdict_view"),
            (f"item/{ids[sell]}", "catalog_item_view"),
        ]
        for path, name in VIEWS + dynamic:
            r = client.get("/v1/views/" + path, headers=auth)
            assert r.status_code == 200, (path, r.text)
            errors = [e.message for e in validator(name).iter_errors(r.json())]
            assert not errors, (path, errors)
        public = client.get(f"/v1/public/storefront/cp1-{pack}")
        assert public.status_code == 200 and not list(
            validator("public_storefront").iter_errors(public.json())
        )
        prices = {i["item_id"]: i["price_paise"] for i in public.json()["items"]}
        for item_id, price in prices.items():  # storefront price = catalog price
            assert client.get("/v1/views/item/" + item_id, headers=auth).json()["price_paise"] == price
        audit = client.get("/v1/audit/verify", headers=auth).json()
        assert audit["valid"] is True and audit["checked"] > 10
