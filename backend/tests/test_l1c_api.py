from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.core.ids import new_id
from arth.core.schemas import validator
from arth.domains.merchants import provision_shop
from arth.governance.policy import Session
from arth.main import create_app


def test_scoped_stock_patron_ledger_views_commands_and_events(tmp_path):
    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path, tick_interval_s=0.05))
    with TestClient(app) as client:

        async def seed():
            shop = await provision_shop(
                app.state.commands, "Shop", "kirana", "Owner", "4826", "test-device", key="l1c-api"
            )
            actor = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
            return actor

        actor = client.portal.call(seed)
        app.state.sessions["test-l1c"] = actor
        auth = {"Authorization": "Bearer test-l1c"}

        def command(kind, payload, key):
            r = client.post(
                "/v1/commands",
                json={"type": kind, "payload": payload},
                headers={**auth, "Idempotency-Key": key},
            )
            assert r.status_code == 200, r.text
            return r.json()

        item = command(
            "catalog.add_item",
            {
                "sku": "SALT",
                "names": {"en": "Salt"},
                "unit": "pcs",
                "mrp_paise": 3000,
                "price_paise": 2700,
                "cost_paise": 2000,
                "category": "staples",
            },
            "item",
        )["data"]["item_id"]
        command("stock.receive", {"item_id": item, "qty_milli": 10000}, "receipt")
        r = client.post(
            "/v1/patrons",
            json={
                "display_name": "Example Patron",
                "lang": "hi",
                "identities": [{"kind": "spoken_name", "value": "Example Patron"}],
            },
            headers={**auth, "Idempotency-Key": "patron"},
        )
        assert r.status_code == 200, r.text
        patron = r.json()["data"]["patron_id"]
        gate = command("ledger.open_account", {"patron_id": patron, "limit_paise": 50000}, "account")
        r = client.post(
            "/v1/approvals/" + gate["thread_id"],
            json={"decision": "approve"},
            headers={**auth, "Idempotency-Key": "open"},
        )
        assert r.status_code == 200, r.text
        account = r.json()["data"]["account_id"]
        for path, name in [
            ("stock", "stock_view"),
            ("expiry", "expiry_view"),
            ("customers/search?q=Example%20Patron", "customer_search_view"),
            ("patron/" + patron, "patron_view"),
            ("khata", "khata_view"),
            ("khata/" + patron, "khata_account_view"),
            ("statement/" + account, "ledger_statement_view"),
            ("promises", "promises_view"),
            ("payables", "payables_view"),
        ]:
            response = client.get("/v1/views/" + path, headers=auth)
            assert response.status_code == 200, response.text
            validator(name).validate(response.json())
            assert client.get("/v1/views/" + path).status_code == 401
        assert client.get("/v1/views/khata/" + new_id("pat"), headers=auth).status_code == 409
        assert client.get("/v1/audit/verify", headers=auth).json()["valid"]

        async def check_events():
            from arth.governance.repository import Repository
            from arth.governance.tables import outbox

            async with app.state.db.read() as conn:
                rows = await Repository(conn, actor.merchant_id).select(outbox)
            import json

            for row in rows:
                event = json.loads(row["payload"])
                validator("event").validate(event)
            assert any(json.loads(r["payload"])["type"] == "stock.changed" for r in rows)

        client.portal.call(check_events)
