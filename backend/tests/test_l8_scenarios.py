"""L8: the scenario library validates, cue cards render, snapshots restore in < 3 s, demo scenarios pass."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from arth.sim.scenario import SCENARIOS_DIR, cue_cards, isolated_settings, load, run_file

LIBRARY = sorted(SCENARIOS_DIR.glob("*/scenario.yaml"))


def test_library_is_complete_and_schema_valid():
    names = {p.parent.name for p in LIBRARY}
    assert {
        "gupta_diwali",
        "cafe_morning_rush",
        "pharmacy_batch_recall",
        "salon_wedding_season",
        "kirana_cold_start",
        "kirana_month_end",
    } <= names
    assert len([n for n in names if n.startswith("edge_")]) >= 6
    for path in LIBRARY:
        scenario = load(path)
        cards = cue_cards(scenario)
        assert cards.startswith("# ") and all(
            beat["id"] in cards for s in scenario["scenes"] for beat in s["beats"]
        )
    bad = {"scenario": "x", "title": "x", "pack": "bakery", "world": {}, "scenes": []}
    from arth.core.schemas import validator

    assert list(validator("scenario").iter_errors(bad))


@pytest.mark.parametrize("name", ["gupta_diwali", "edge_injection"])
def test_demo_scenarios_pass_headless(tmp_path, name):
    report = run_file(SCENARIOS_DIR / name / "scenario.yaml", isolated_settings(data_dir=tmp_path))
    assert report["beats"] and all(b["ok"] for b in report["beats"])
    assert (tmp_path / "snapshots").exists()  # one snapshot per scene, restorable from the Director


def test_gupta_short_cut_runs_only_its_scenes(tmp_path):
    report = run_file(
        SCENARIOS_DIR / "gupta_diwali" / "scenario.yaml", isolated_settings(data_dir=tmp_path), "short"
    )
    assert {b["scene"] for b in report["beats"]} == {"1", "2", "3", "5", "6b", "7", "8"}


def test_director_snapshot_restore_under_three_seconds_and_scenario_list(tmp_path):
    from arth.main import create_app

    app = create_app(isolated_settings(data_dir=tmp_path))
    director = {"Authorization": "Bearer dev-director"}
    with TestClient(app) as client:
        world = client.post(
            "/v1/director/world",
            json={"pack": "kirana", "days": 2, "patrons": 6, "size": "micro"},
            headers=director,
        ).json()
        saved = client.post("/v1/director/snapshot", json={"name": "scene-1"}, headers=director)
        assert saved.status_code == 200
        client.post("/v1/director/clock", json={"advance_minutes": 600}, headers=director)
        token = client.post(
            "/v1/director/session", json={"merchant_id": world["merchant_id"]}, headers=director
        ).json()["token"]
        bill = client.post(
            "/v1/commands",
            json={"type": "counter.open_bill", "payload": {}},
            headers={"Authorization": "Bearer " + token, "Idempotency-Key": "after"},
        ).json()
        restored = client.post("/v1/director/restore", json={"name": "scene-1"}, headers=director)
        assert restored.status_code == 200 and restored.json()["ms"] < 3000
        assert restored.json()["clock"] == saved.json()["clock"]
        token = client.post(
            "/v1/director/session", json={"merchant_id": world["merchant_id"]}, headers=director
        ).json()["token"]
        assert (
            client.get(
                f"/v1/views/bill/{bill['data']['bill_id']}", headers={"Authorization": "Bearer " + token}
            ).status_code
            == 409
        )  # gone after restore
        listed = client.get("/v1/director/scenarios", headers=director).json()["scenarios"]
        assert {s["scenario"] for s in listed} >= {"gupta_diwali", "billing_smoke"}
        assert client.post("/v1/director/restore", json={"name": "nope"}, headers=director).status_code == 404
    assert Path(tmp_path).exists()
