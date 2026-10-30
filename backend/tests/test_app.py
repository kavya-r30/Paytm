from pathlib import Path

import yaml
from fastapi.testclient import TestClient
from jsonschema import Draft7Validator
from sqlalchemy import create_engine, select

from arth.core.config import Settings
from arth.core.paths import CONTRACTS_DIR
from arth.core.schemas import validator
from arth.core.spans import Span
from arth.core.tables import spans
from arth.main import create_app

OPENAPI = yaml.safe_load((CONTRACTS_DIR / "openapi.yaml").read_text(encoding="utf-8"))


def client(tmp_path: Path) -> TestClient:
    settings = Settings(_env_file=None, mode="test", data_dir=tmp_path, tick_interval_s=0.05)
    return TestClient(create_app(settings))


def test_health_reports_mode_clock_and_packs(tmp_path: Path) -> None:
    with client(tmp_path) as c:
        response = c.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    Draft7Validator(OPENAPI["components"]["schemas"]["Health"]).validate(body)
    providers = body.pop("providers")
    assert body == {
        "status": "ok",
        "mode": "test",
        "clock": "2026-10-29T02:15:00.000000Z",
        "packs": ["kirana"],
    }
    assert set(providers) == {"mistral", "groq", "sarvam"}
    assert all(isinstance(v, bool) for v in providers.values())


def test_director_requires_its_token(tmp_path: Path) -> None:
    with client(tmp_path) as c:
        denied = c.get("/v1/director/ping")
        wrong = c.get("/v1/director/ping", headers={"Authorization": "Bearer dev-device"})
        allowed = c.get("/v1/director/ping", headers={"Authorization": "Bearer dev-director"})
    assert denied.status_code == 401 and wrong.status_code == 401
    assert denied.headers["content-type"].startswith("application/problem+json")
    validator("problem").validate(denied.json())
    assert denied.json()["code"] == "auth.missing_token"
    assert allowed.json() == {"ok": True}


def test_boot_migrates_the_database(tmp_path: Path) -> None:
    with client(tmp_path):
        pass
    assert (tmp_path / "arth.db").is_file()


def test_lifespan_runs_span_persister_and_flushes_on_shutdown(tmp_path: Path) -> None:
    with client(tmp_path) as c:
        bus = c.app.state.spans  # type: ignore[attr-defined]
        assert bus._task is not None and not bus._task.done(), "span persister must run while the app is up"
        assert c.portal is not None
        c.portal.call(bus.emit, _span())
    engine = create_engine(f"sqlite:///{(tmp_path / 'arth.db').as_posix()}")
    with engine.connect() as conn:
        names = [row.name for row in conn.execute(select(spans.c.name))]
    engine.dispose()
    assert names == ["lifespan-check"], "spans emitted before shutdown must be persisted by aclose()"


def _span() -> Span:
    return Span(
        id="span_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
        trace_id="trace_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1",
        parent_id=None,
        kind="test",
        name="lifespan-check",
        start_at="2026-10-29T02:15:00.000000Z",
        dur_ms=1.0,
        mode="none",
        cost_paise=0,
    )
