"""L6 growth: exact diagnostics, pack levers, hints with holdout, plan-bounded campaigns, guardrails, ledger;
plus Lane B requests 8 (step-up), 9 (storefront orders) and 10 (envelope on the stream)."""

import time
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from l2_helpers import build_world

from arth.core.config import Settings
from arth.governance.commands import CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository


async def growth_world(db, days=21):
    bus, sim, dispatcher, manifest = await build_world(
        db, "kirana", days=days, seed=31, patrons=16, size="micro"
    )
    owner = Session(manifest["merchant_id"], manifest["owner_id"], "owner", channel="console")
    return bus, sim, dispatcher, manifest, owner


async def approve(bus, owner, gate):
    result = await bus.decide(owner, gate["thread_id"], "approve", "ok-" + gate["gate_id"])
    if result["status"] == "queued":
        bus.clock.set(bus.clock.now() + timedelta(seconds=31))
        await bus.run_due(owner.merchant_id)
    return result


async def test_growth_end_to_end_on_a_generated_world(db):
    from arth.domains.commerce_tables import bills
    from arth.growth.engine import bundles, credit_advice, diagnostics, hint_for, ledger, levers
    from arth.growth.tables import campaign_assignments, campaigns, hints

    bus, sim, dispatcher, manifest, owner = await growth_world(db)
    mid = manifest["merchant_id"]
    async with db.read() as conn:
        repo = Repository(conn, mid)
        diag = await diagnostics(repo, bus.clock, days=7)
        assert sum(diag["parts"].values()) == diag["change_paise"]  # exact decomposition (T6.1)
        names = {lv["name"] for lv in await levers(repo, bus.clock, bus.packs)}
        assert {"counter_hint", "winback", "replenish"} <= names and "slot_fill" not in names
        for bundle in await bundles(repo, 0.15):
            assert bundle["margin_bp"] >= 1500
        advice = await credit_advice(repo, bus.clock)
        assert all(a["suggested_limit_paise"] > a["current_limit_paise"] for a in advice)
    with pytest.raises(CommandError, match="growth.lever_not_in_pack"):
        await bus.submit(
            owner,
            "growth.create_plan",
            {"goal_key": "goal.more_visits", "levers": ["slot_fill"], "budget_paise": 0, "holdout_bp": 2000},
            "bad-plan",
        )
    plan = await bus.submit(
        owner,
        "growth.create_plan",
        {
            "goal_key": "goal.more_visits",
            "levers": ["winback", "repeat_order"],
            "budget_paise": 50000,
            "holdout_bp": 2000,
        },
        "plan",
    )
    assert plan["tier"] == "R3"
    await approve(bus, owner, plan)
    async with db.read() as conn:
        from arth.growth.tables import growth_plans

        plan_id = (await Repository(conn, mid).select(growth_plans))[0]["id"]
    with pytest.raises(CommandError, match="growth.outside_plan_scope"):
        await bus.submit(
            owner,
            "outreach.send_campaign",
            {"plan_id": plan_id, "lever": "replenish", "template": "outreach.replenish"},
            "outside",
        )
    gate = await bus.submit(
        owner,
        "outreach.send_campaign",
        {"plan_id": plan_id, "lever": "repeat_order", "template": "outreach.repeat_order"},
        "campaign",
    )
    await approve(bus, owner, gate)
    await dispatcher.dispatch(mid)
    async with db.read() as conn:
        repo = Repository(conn, mid)
        rows = await repo.select(campaign_assignments)
        assert rows and all(not r["sent"] for r in rows if r["arm"] == "holdout")  # holdout never messaged
        assert all(r["reason"] == "policy.consent" for r in rows if r["arm"] == "treated" and not r["sent"])
        result = await ledger(repo)
        assert (
            len(result["entries"]) == 1
            and result["entries"][0]["treated_n"] + result["entries"][0]["holdout_n"]
        )
    patron = next(t["patron_id"] for t in await sim.threads(mid) if t["patron_id"])
    bill = (await bus.submit(owner, "counter.open_bill", {"patron_id": patron}, "hint-bill"))["data"][
        "bill_id"
    ]
    async with db.read() as conn:
        repo = Repository(conn, mid)
        row = (await repo.select(hints, hints.c.bill_id == bill))[0]
        started = time.monotonic()
        hint = await hint_for(repo, bus.clock, bill)
        assert time.monotonic() - started < 0.3  # GRW-4: hint < 300 ms
        assert (hint is None) == (row["arm"] == "holdout" or row["item_id"] is None)
        if hint:
            assert hint["audience"] == "owner"
        assert await repo.select(bills, bills.c.id == bill)
    from arth.domains.commerce_tables import ratings

    closed = next(b for b in (await _bills(db, mid)) if b["status"] == "closed")
    await bus.submit(
        owner,
        "feedback.record",
        {"target_kind": "bill", "target_id": closed["id"], "rating": 1, "complaint_key": "feedback.rude"},
        "complaint",
    )
    from arth.api.growth import install_guardrails

    install_guardrails(dispatcher, bus.clock)
    await dispatcher.dispatch(mid)
    async with db.read() as conn:
        repo = Repository(conn, mid)
        assert {c["status"] for c in await repo.select(campaigns)} == {"stopped"}  # FBK-3 auto-stop
        assert await repo.select(ratings)


async def _bills(db, mid):
    from arth.domains.commerce_tables import bills

    async with db.read() as conn:
        return await Repository(conn, mid).select(bills)


async def test_preorder_deposit_is_an_advance(db):
    from arth.domains.ledger_projection import statement
    from arth.domains.ledger_tables import credit_accounts

    bus, sim, dispatcher, manifest, owner = await growth_world(db, days=2)
    mid = manifest["merchant_id"]
    async with db.read() as conn:
        account = (await Repository(conn, mid).select(credit_accounts))[0]
    gate = await bus.submit(
        owner,
        "preorders.create",
        {
            "patron_id": account["patron_id"],
            "account_id": account["id"],
            "items": [{"item_id": manifest["items"]["SUGAR-LOOSE"], "qty_milli": 5000}],
            "deposit_paise": 10000,
        },
        "preorder",
    )
    result = await approve(bus, owner, gate)
    assert result["data"]["total_paise"] == 22500
    async with db.read() as conn:
        report = await statement(Repository(conn, mid), account["id"], bus.clock)
    assert report["advance_paise"] >= 10000


def test_growth_views_step_up_storefront_orders_and_envelope_stream(tmp_path):
    from arth.core.schemas import validator
    from arth.main import create_app

    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path))
    director = {"Authorization": "Bearer dev-director"}
    with TestClient(app) as client:
        world = client.post(
            "/v1/director/world",
            json={"pack": "kirana", "days": 3, "patrons": 6, "size": "micro"},
            headers=director,
        ).json()
        mid = world["merchant_id"]
        token = client.post(
            "/v1/director/session", json={"merchant_id": mid, "surface": "console"}, headers=director
        ).json()["token"]
        auth = {"Authorization": "Bearer " + token}
        for path, name in [
            ("grow", "grow_view"),
            ("grow/ledger", "growth_ledger_view"),
            ("grow/bundles", "bundles_view"),
        ]:
            body = client.get("/v1/views/" + path, headers=auth).json()
            assert not [e.message for e in validator(name).iter_errors(body)], (path, body)
        bill = client.post(
            "/v1/commands",
            json={"type": "counter.open_bill", "payload": {}},
            headers={**auth, "Idempotency-Key": "b"},
        ).json()["data"]["bill_id"]
        body = client.get(f"/v1/views/bill/{bill}", headers=auth).json()
        assert body["hint"] is None and not list(validator("bill_view").iter_errors(body))
        refund = {"type": "privacy.set_data_sharing", "payload": {"peer_benchmarks": True}}
        assert (
            client.post("/v1/commands", json=refund, headers={**auth, "Idempotency-Key": "r2"}).status_code
            == 200
        )
        r4 = {"type": "capital.apply", "payload": {"offer_id": "loan_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"}}
        assert (
            client.post("/v1/commands", json=r4, headers={**auth, "Idempotency-Key": "r4a"}).json()["code"]
            == "policy.console_required"
        )
        assert client.post("/v1/auth/step-up", json={"otp": "000000"}, headers=auth).status_code == 403
        assert client.post("/v1/auth/step-up", json={"otp": "123456"}, headers=auth).status_code == 200
        after = client.post("/v1/commands", json=r4, headers={**auth, "Idempotency-Key": "r4b"}).json()
        assert (
            after["code"] == "capital.offer_not_available"
        )  # past the R4 gate: the offer simply does not exist
        slug = client.get("/v1/views/storefront", headers=auth).json()["slug"]
        item = client.get(f"/v1/public/storefront/{slug}").json()["items"][0]["item_id"]
        order = client.post(
            f"/v1/public/storefront/{slug}/orders", json={"lines": [{"item_id": item, "qty_milli": 1000}]}
        )
        assert order.status_code == 200 and order.json()["status"] == "draft"
        queue = app.state.events.subscribe(mid)
        client.post(
            "/v1/turns",
            json={"text": "Aaj kitna aaya?", "surface": "console"},
            headers={**auth, "Idempotency-Key": "env"},
        )
        seen = []
        while not queue.empty():
            seen.append(queue.get_nowait()["type"])
        assert "envelope" in seen
