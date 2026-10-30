"""Headless scenario runner core (T2.11): YAML beats driven through the real HTTP API.

A beat has inputs (`do`) and expectations (`expect`). Inputs: `command`, `pay_qr` (customer pays the
bill's dynamic QR through the Rails simulator), `inbound` (persona message), `clock`, `settle`. Expectations:
`view` + dotted `path` compared with `equals`/`gte`/`lte`/`len`, and `invariants: true`.
Values like `${bill}` are substituted from earlier `save:` results.
"""

import json
import re
from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.governance.policy import Session

TOKEN = "scenario-owner"


def _sub(value: Any, saved: dict[str, Any]) -> Any:
    if isinstance(value, str):
        whole = re.fullmatch(r"\$\{(\w+)\}", value)
        if whole:
            return saved[whole.group(1)]
        return re.sub(r"\$\{(\w+)\}", lambda m: str(saved[m.group(1)]), value)
    if isinstance(value, list):
        return [_sub(v, saved) for v in value]
    if isinstance(value, dict):
        return {k: _sub(v, saved) for k, v in value.items()}
    return value


def _dig(data: Any, path: str) -> Any:
    for part in path.split(".") if path else []:
        data = data[int(part)] if isinstance(data, list) else data[part]
    return data


class ScenarioRunner:
    def __init__(self, client: TestClient) -> None:
        self.client, self.app = client, client.app
        self.saved: dict[str, Any] = {}
        self.n = 0
        self.auth = {"Authorization": "Bearer " + TOKEN}

    def call(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        return self.client.portal.call(lambda: fn(*args, **kwargs))  # type: ignore[union-attr]

    def setup(self, scenario: dict[str, Any]) -> None:
        from arth.sim.world import WorldBuilder, WorldSpec

        state = self.app.state  # type: ignore[attr-defined]
        world = scenario.get("world", {})
        spec = WorldSpec(
            pack=scenario.get("pack", "kirana"),
            days=world.get("days", 2),
            seed=world.get("seed", 1),
            size=world.get("size", "micro"),
            patrons=world.get("patrons", 8),
            key=scenario["name"],
        )
        manifest = self.call(WorldBuilder(state.sim, state.patrons, spec).build)
        state.commands.merchant_ids.add(manifest["merchant_id"])
        state.sessions[TOKEN] = Session(
            manifest["merchant_id"], manifest["owner_id"], "owner", channel="console", step_up=True
        )
        self.saved.update(merchant_id=manifest["merchant_id"], manifest=manifest)
        self.saved.update({sku.lower().replace("-", "_"): item for sku, item in manifest["items"].items()})

    def command(self, spec: dict[str, Any]) -> dict[str, Any]:
        self.n += 1
        response = self.client.post(
            "/v1/commands",
            json={"type": spec["type"], "payload": spec.get("payload", {})},
            headers={**self.auth, "Idempotency-Key": f"scenario-{self.n}"},
        )
        if response.status_code != 200:
            raise AssertionError(f"{spec['type']} refused: {response.text}")
        result: dict[str, Any] = response.json()
        if result["status"] == "needs_approval" and spec.get("approve", True):
            self.n += 1
            response = self.client.post(
                "/v1/approvals/" + result["thread_id"],
                json={"decision": "approve"},
                headers={**self.auth, "Idempotency-Key": f"scenario-{self.n}"},
            )
            assert response.status_code == 200, response.text
            result = response.json()
            if result["status"] == "queued":
                self.clock(1)
                self.call(self.app.state.commands.run_due, self.saved["merchant_id"])  # type: ignore[attr-defined]
        return result

    def clock(self, minutes: int) -> None:
        response = self.client.post(
            "/v1/director/clock",
            json={"advance_minutes": minutes},
            headers={"Authorization": "Bearer dev-director"},
        )
        assert response.status_code == 200, response.text

    def act(self, action: dict[str, Any]) -> None:
        action = _sub(action, self.saved)
        sim = self.app.state.sim  # type: ignore[attr-defined]
        mid = self.saved["merchant_id"]
        result: Any = None
        if "command" in action:
            result = self.command(action["command"])
        elif "pay_qr" in action:
            spec = action["pay_qr"]
            intent = self.command({"type": "counter.request_upi", "payload": {"bill_id": spec["bill_id"]}})[
                "data"
            ]
            qr = self.call(sim.create_qr, mid, intent["order_ref"], intent["amount_paise"])
            result = self.call(
                sim.pay,
                mid,
                token=qr["token"],
                payer_vpa=spec.get("payer_vpa", "customer@okbank"),
                outcome=spec.get("outcome", "success"),
            )
        elif "inbound" in action:
            result = self.call(sim.inbound, mid, action["inbound"]["persona_id"], action["inbound"]["text"])
        elif "clock" in action:
            self.clock(action["clock"]["advance_minutes"])
        elif "settle" in action:
            result = self.call(sim.settle, mid, action["settle"]["date"])
        else:
            raise AssertionError(f"unknown action {action}")
        if action.get("save"):
            for name, path in action["save"].items():
                self.saved[name] = _dig(result, path)

    def expect(self, check: dict[str, Any]) -> None:
        check = _sub(check, self.saved)
        if check.get("invariants"):
            from arth.governance.repository import Repository
            from arth.sim.invariants import check as invariants

            async def run() -> list[str]:
                state = self.app.state  # type: ignore[attr-defined]
                async with state.db.read() as conn:
                    return await invariants(Repository(conn, self.saved["merchant_id"]), state.clock)

            problems = self.call(run)
            assert not problems, problems
            return
        response = self.client.get("/v1/views/" + check["view"], headers=self.auth)
        assert response.status_code == 200, response.text
        value = _dig(response.json(), check.get("path", ""))
        if "equals" in check:
            assert value == check["equals"], (check, value)
        if "gte" in check:
            assert value >= check["gte"], (check, value)
        if "lte" in check:
            assert value <= check["lte"], (check, value)
        if "len" in check:
            assert len(value) == check["len"], (check, value)

    def run(self, scenario: dict[str, Any]) -> dict[str, Any]:
        self.setup(scenario)
        report = []
        for beat in scenario["beats"]:
            for action in beat.get("do", []):
                self.act(action)
            for check in beat.get("expect", []):
                self.expect(check)
            report.append({"beat": beat["name"], "ok": True})
        return {"scenario": scenario["name"], "beats": report, "merchant_id": self.saved["merchant_id"]}


def isolated_settings(**overrides: Any) -> Settings:
    """Test-mode settings that never read backend/.env."""
    return Settings(**{"_env_file": None, "mode": "test", **overrides})


def run_file(path: Path, settings: Settings | None = None) -> dict[str, Any]:
    from arth.main import create_app

    scenario = yaml.safe_load(path.read_text(encoding="utf-8"))
    app = create_app(settings or isolated_settings())
    with TestClient(app) as client:
        return ScenarioRunner(client).run(scenario)


if __name__ == "__main__":
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        print(
            json.dumps(
                run_file(Path(sys.argv[1]), isolated_settings(data_dir=Path(tmp))),
                indent=2,
            )
        )
