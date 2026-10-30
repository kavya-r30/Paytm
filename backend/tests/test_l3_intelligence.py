"""L3 intelligence on generated worlds: analytics = Treasury, honest forecast accuracy, planted signals."""

from datetime import timedelta

from fastapi.testclient import TestClient
from l2_helpers import build_world

from arth.core.config import Settings
from arth.governance.repository import Repository
from arth.intel import analytics as a


async def test_l3_on_one_generated_world(db):
    """One 35-day world, checked by every L3 component (built once: world generation dominates runtime)."""
    bus, _, _, manifest = await build_world(db, "kirana", days=35, seed=3, patrons=14, size="micro")
    for check in (
        analytics_match_treasury,
        forecast_band_accuracy_and_cashflow,
        demand_clusters_alerts_dedupe_and_decision_budget,
        charts_reproducible_and_uplift_ci,
    ):
        await check((bus, manifest, db))


async def analytics_match_treasury(world):
    from arth.domains.treasury import day_summary
    from arth.intel.analytics import ist_date

    bus, manifest, db = world
    async with db.read() as conn:
        repo = Repository(conn, manifest["merchant_id"])
        day = a.today(bus.clock) - timedelta(days=2)
        modes = {r["mode"]: r["amount_paise"] for r in await a.payments_by_mode(repo, day, day)}
        assert modes == (await day_summary(repo, bus.clock, day.isoformat()))["by_mode"]
        bills = await a.closed_bills(repo)
        sales = await a.daily_sales(repo, day, day)
        assert sales[0]["sales_paise"] == sum(
            b["total_paise"] for b in bills if ist_date(b["closed_at"]) == day
        )
        states = {r["patron_id"]: r["state"] for r in await a.lifecycle(repo, bus.clock)}
        for patron in manifest["planted"]["lapsing_patrons"]:
            assert states.get(patron) in {"lapsing", "lost"}, (patron, states.get(patron))
        aging = await a.khata_aging(repo, bus.clock)
        assert [r["bucket"] for r in aging] == ["0-7", "8-30", "31-60", "60+"]


async def forecast_band_accuracy_and_cashflow(world):
    from arth.intel.forecast import cashflow, sales_forecast

    bus, manifest, db = world
    async with db.read() as conn:
        repo = Repository(conn, manifest["merchant_id"])
        result = await sales_forecast(repo, bus.clock)
        assert result["status"] == "ready" and len(result["days"]) == 7
        assert all(d["p10_paise"] <= d["p50_paise"] <= d["p90_paise"] for d in result["days"])
        assert 5000 <= result["accuracy"]["coverage_bp"] <= 10000  # ~80% band, prototype tolerance
        assert result["accuracy"]["wape_bp"] is not None
        flow = await cashflow(repo, bus.clock)
        assert len(flow["days"]) == 14


async def demand_clusters_alerts_dedupe_and_decision_budget(world):
    from arth.governance.policy import Session
    from arth.intel.commands import register_intel
    from arth.intel.insight import demand_clusters, next_best_actions

    bus, manifest, db = world
    async with db.read() as conn:
        repo = Repository(conn, manifest["merchant_id"])
        clusters = await demand_clusters(repo)
        assert clusters and clusters[0]["count"] == 2  # planted "ghee" cluster
        actions = await next_best_actions(repo, bus.clock, set())
        assert len(actions["proactive"]) <= 1  # attention budget
        first = actions["proactive"][0]["key"] if actions["proactive"] else None
    register_intel(bus)
    system = Session(manifest["merchant_id"], "system_x", "system", actor_kind="system")
    raised = (await bus.submit(system, "alerts.scan", {}, "scan-1"))["data"]["raised"]
    again = (await bus.submit(system, "alerts.scan", {}, "scan-2"))["data"]["raised"]
    assert raised and again == []  # PEX duplicate exception planted by the world → alert, raised once
    if first:
        owner = Session(manifest["merchant_id"], manifest["owner_id"], "owner", channel="console")
        until = (bus.clock.now() + timedelta(days=1)).isoformat().replace("+00:00", "Z")
        await bus.submit(owner, "actions.snooze", {"key": first, "until": until}, "snooze-1")
        from arth.intel.commands import active_snoozes

        async with db.read() as conn:
            repo = Repository(conn, manifest["merchant_id"])
            snoozed = await active_snoozes(repo, bus.clock.now().isoformat())
            assert first in snoozed
            after = await next_best_actions(repo, bus.clock, snoozed)
            assert all(c["key"] != first for c in after["proactive"] + after["queued"])


async def charts_reproducible_and_uplift_ci(world):
    from arth.intel.charts import build, svg
    from arth.intel.forecast import bootstrap_ci

    bus, manifest, db = world
    async with db.read() as conn:
        repo = Repository(conn, manifest["merchant_id"])
        for n in range(1, 13):
            first, second = await build(n, repo, bus.clock), await build(n, repo, bus.clock)
            assert first["chart_no"] == n and first["data"] == second["data"]
            assert svg(first).startswith("<svg")
    assert bootstrap_ci([1] * 5, [0] * 5)["mode"] == "counts"
    result = bootstrap_ci([10, 12, 11, 9] * 10, [8, 9, 7, 8] * 5)
    assert result["mode"] == "ci" and result["ci90"][0] <= result["uplift"] <= result["ci90"][1]


def test_intel_api_views_charts_exports(tmp_path):
    from arth.core.schemas import validator
    from arth.main import create_app

    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path))
    director = {"Authorization": "Bearer dev-director"}
    with TestClient(app) as client:
        world = client.post(
            "/v1/director/world",
            json={"pack": "kirana", "days": 16, "patrons": 8, "size": "micro"},
            headers=director,
        ).json()
        token = client.post(
            "/v1/director/session", json={"merchant_id": world["merchant_id"]}, headers=director
        )
        auth = {"Authorization": "Bearer " + token.json()["token"]}
        for path, name in [
            ("forecast?metric=sales", "forecast_view"),
            ("forecast?metric=items", "forecast_view"),
            ("insights", "insights_view"),
        ]:
            r = client.get("/v1/views/" + path, headers=auth)
            assert r.status_code == 200, r.text
            assert not [e.message for e in validator(name).iter_errors(r.json())], path
        for n in (1, 6, 7):
            r = client.get(f"/v1/charts/{n}", headers=auth)
            assert r.status_code == 200 and not list(validator("chart_card").iter_errors(r.json()))
        assert client.get("/v1/charts/6?format=svg", headers=auth).text.startswith("<svg")
        for tool in (
            "sales",
            "payments",
            "compare",
            "top",
            "khata_aging",
            "lifecycle",
            "hourly",
            "cycles",
            "affinity",
        ):
            assert client.get(f"/v1/analytics/{tool}", headers=auth).status_code == 200, tool
        assert client.get("/v1/analytics/drop_tables", headers=auth).status_code == 404
        assert "net_paise" in client.get("/v1/books/export/pnl", headers=auth).json()["csv"]
