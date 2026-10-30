import json

from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.core.paths import CONTRACTS_DIR
from arth.core.schemas import validator
from arth.main import create_app


def test_login_settings_import_search_price_gate_and_restart(tmp_path):
    from arth.domains.merchants import provision_shop

    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path, tick_interval_s=0.05))
    with TestClient(app) as client:

        async def seed():
            return await provision_shop(
                app.state.commands, "Shop", "kirana", "Owner", "4826", "device-api", key="api-shop"
            )

        shop = client.portal.call(seed)
        credential = app.state.staff.device_credential(shop["merchant_id"], shop["device_id"])
        login_body = {
            "device_credential": credential,
            "staff_id": shop["owner_id"],
            "pin": "4826",
            "channel": "console",
        }
        login = client.post(
            "/v1/staff/login",
            json=login_body,
            headers={"Authorization": "Bearer dev-console", "Idempotency-Key": "login"},
        )
        assert login.status_code == 200, login.text
        validator("session_result").validate(login.json())
        token = login.json()["token"]
        import hashlib
        import hmac

        signed_body = token.rsplit(".", 1)[0]
        forged = signed_body + "." + hmac.new(b"dev-device", signed_body.encode(), hashlib.sha256).hexdigest()
        assert (
            client.get(
                "/v1/views/settings/language", headers={"Authorization": "Bearer " + forged}
            ).status_code
            == 401
        )
        auth = {"Authorization": "Bearer " + token}

        def command(kind, payload, key):
            response = client.post(
                "/v1/commands",
                json={"type": kind, "payload": payload},
                headers={**auth, "Idempotency-Key": key},
            )
            assert response.status_code == 200, response.text
            return response.json()

        command(
            "merchant.update_settings",
            {
                "screen_lang": "ta",
                "speech_lang": "hi-IN",
                "customer_lang": "en",
                "vpa": "example@paytm",
                "address": "Example Market",
            },
            "lang",
        )
        settings = client.get("/v1/views/settings/language", headers=auth).json()
        validator("settings_view").validate(settings)
        assert (settings["screen_lang"], settings["speech_lang"], settings["customer_lang"]) == (
            "ta",
            "hi-IN",
            "en",
        )
        item = json.loads(
            (CONTRACTS_DIR / "examples/catalog_add_item.example.json").read_text(encoding="utf-8")
        )
        identity = command("catalog.import_items", {"confirmed": True, "items": [item]}, "import")["data"][
            "item_ids"
        ][0]
        for path, name in [
            ("/v1/catalog/search?q=namak", "catalog_search_view"),
            ("/v1/catalog/resolve?q=Tata%20Salt", "resolution_view"),
            ("/v1/views/item/" + identity, "catalog_item_view"),
            ("/v1/views/onboarding", "onboarding_view"),
            ("/v1/views/settings/staff", "staff_view"),
            ("/v1/views/shift", "shift_view"),
        ]:
            response = client.get(path, headers=auth)
            assert response.status_code == 200, response.text
            validator(name).validate(response.json())
        for step in ["language", "pack", "details", "catalog", "people"]:
            command("onboarding.complete_step", {"step": step}, "step-" + step)
        assert client.get("/v1/views/onboarding", headers=auth).json()["next_step"] is None
        gate = command("catalog.change_price", {"item_id": identity, "price_paise": 2600}, "change")
        assert gate["status"] == "needs_approval"
        assert gate["envelope"]["lang"]["screen"] == "ta"
        approval = client.post(
            "/v1/approvals/" + gate["thread_id"],
            json={"decision": "approve"},
            headers={**auth, "Idempotency-Key": "approve"},
        )
        assert approval.status_code == 200, approval.text
        assert client.get("/v1/views/item/" + identity, headers=auth).json()["price_paise"] == 2600
        assert client.get("/v1/audit/verify", headers=auth).json()["valid"]
        assert (
            client.post(
                "/v1/staff/login",
                json={**login_body, "role": "owner", "owner_ptt": True},
                headers={"Authorization": "Bearer dev-console", "Idempotency-Key": "spoof"},
            ).status_code
            == 422
        )
    with TestClient(create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path))) as restarted:
        assert restarted.get("/v1/views/item/" + identity, headers=auth).status_code == 200
