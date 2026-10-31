from conftest import seed_repo
from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.core.schemas import validator
from arth.main import create_app


def test_api_uses_server_session_not_body_or_headers(tmp_path):
    from arth.governance.policy import Session
    from arth.governance.tables import merchant_settings, merchants

    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path))
    with TestClient(app) as client:
        app.state.sessions["test-owner"] = Session("a", "o", "owner", channel="console")
        bus = app.state.commands

        async def seed():
            async with app.state.db.write() as conn:
                await seed_repo(conn, "a").insert(merchants, {"id": "a", "name": "A", "pack": "kirana"})

        client.portal.call(seed)
        bus.policy.policies.tiers["test.write"] = "R1"

        async def save(repo, payload):
            await repo.insert(merchant_settings, {"settings": "{}"})
            return {"saved": True}

        bus.register("test.write", {"type": "object", "additionalProperties": False}, save)
        body = {"type": "test.write", "payload": {}}
        assert client.post("/v1/commands", json=body).status_code == 401
        headers = {"Authorization": "Bearer test-owner", "Idempotency-Key": "one", "X-Merchant-Id": "b"}
        response = client.post("/v1/commands", json=body, headers=headers)
        assert response.status_code == 200, response.text
        validator("command_result").validate(response.json())
        assert client.post("/v1/commands", json=body, headers=headers).json() == response.json()
        assert (
            client.post("/v1/commands", json={**body, "merchant_id": "b"}, headers=headers).status_code == 422
        )
        audit = client.get("/v1/audit/verify", headers=headers)
        assert audit.json()["valid"] and audit.json()["checked"] == 1
        app.state.sessions["test-other"] = Session("b", "o2", "owner", channel="console")
        assert (
            client.get("/v1/audit/verify", headers={"Authorization": "Bearer test-other"}).json()["checked"]
            == 0
        )


async def test_sse_domain_events_and_view_invalidation_are_tenant_filtered(db):
    import asyncio

    from arth.core.clock import SimClock
    from arth.governance.events import Dispatcher, emit_event
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    clock = SimClock(Settings(_env_file=None).clock_start)
    dispatcher = Dispatcher(db, clock)
    dispatcher.declare_view("trust", {"command.executed"})
    a, b = dispatcher.subscribe("a"), dispatcher.subscribe("b")
    async with db.write() as conn:
        from arth.core.ids import new_id

        await emit_event(
            Repository(conn, "a"),
            clock,
            Session("a", "o", "owner"),
            "command.executed",
            new_id("cmd"),
            {"command_id": new_id("cmd"), "status": "executed"},
        )
    await asyncio.wait_for(dispatcher.dispatch("a"), 0.2)
    validator("command_executed").validate(a.get_nowait())
    event = a.get_nowait()
    validator("view_invalidate").validate(event)
    assert event["payload"] == {"views": ["trust"]}
    assert b.empty()
