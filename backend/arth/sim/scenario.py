"""Headless scenario runner (T2.11 core, completed in T8.1–T8.2): scenario YAML driven through the real API.

Language: `contracts/scenario.schema.json`. A scene is snapshotted before it runs (restorable from
the Director); each beat has inputs (`say_for_me`, `command`,
`approve_all`, `persona_action`, `clock`, `fault`, `locale`,
`settle`, `tick`), saved values, `expect_turn`, `expect` (view paths, outbound messages, invariants) and
`within_ms`. `${world.patrons.priya.id}` and `${bill}` resolve against the world manifest and saved values.
"""

import json
import re
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from arth.core.clock import iso_utc
from arth.core.config import Settings
from arth.core.schemas import validator
from arth.governance.policy import Session

CONSOLE, DEVICE = "scenario-console", "scenario-device"
SCENARIOS_DIR = Path(__file__).resolve().parents[2] / "scenarios"
DIRECTOR = {"Authorization": "Bearer dev-director"}


class BeatFailed(AssertionError):
    pass


def isolated_settings(**overrides: Any) -> Settings:
    """Test-mode settings that never read backend/.env, on a fresh data dir unless one is given."""
    data_dir = overrides.pop("data_dir", None) or Path(tempfile.mkdtemp(prefix="arth-scenario-"))
    return Settings(**{"_env_file": None, "mode": "test", "data_dir": data_dir, **overrides})


def dig(data: Any, path: str) -> Any:
    for part in path.split(".") if path else []:
        if isinstance(data, list):
            data = data[int(part)] if part.lstrip("-").isdigit() and len(data) > int(part) else None
        elif isinstance(data, dict):
            data = data.get(part)
        else:
            return None
    return data


def substitute(value: Any, saved: dict[str, Any]) -> Any:
    if isinstance(value, str):
        whole = re.fullmatch(r"\$\{([\w.]+)\}", value)
        if whole:
            return dig(saved, whole.group(1))
        return re.sub(r"\$\{([\w.]+)\}", lambda m: str(dig(saved, m.group(1))), value)
    if isinstance(value, list):
        return [substitute(v, saved) for v in value]
    if isinstance(value, dict):
        return {k: substitute(v, saved) for k, v in value.items()}
    return value


def load(path: Path) -> dict[str, Any]:
    scenario: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = [e.message for e in validator("scenario").iter_errors(scenario)]
    if errors:
        raise ValueError(f"{path}: {errors[:3]}")
    return scenario


class ScenarioRunner:
    def __init__(self, client: TestClient) -> None:
        self.client = client
        self.state = client.app.state  # type: ignore[attr-defined]
        self.saved: dict[str, Any] = {}
        self.n = 0
        self.last: Any = None

    def call(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        return self.client.portal.call(lambda: fn(*args, **kwargs))  # type: ignore[union-attr]

    def auth(self, surface: str = "console") -> dict[str, str]:
        return {"Authorization": "Bearer " + (CONSOLE if surface == "console" else DEVICE)}

    # setup -------------------------------------------------------------------------------------------
    def setup(self, scenario: dict[str, Any]) -> None:
        from arth.domains.merchants import provision_shop
        from arth.sim.world import WorldBuilder, WorldSpec

        world = scenario.get("world", {})
        key = scenario["scenario"] + "-" + str(world.get("seed", 1))
        if world.get("cold_start"):
            shop = self.call(
                provision_shop,
                self.state.commands,
                scenario["title"][:40],
                scenario["pack"],
                "Owner",
                "4826",
                "device-" + key,
                key="world-" + key,
            )
            manifest: dict[str, Any] = {
                **shop,
                "pin": "4826",
                "items": {},
                "patrons": {},
                "suppliers": {},
                "planted": {},
            }
        else:
            spec = WorldSpec(
                pack=scenario["pack"],
                days=world.get("days", 3),
                seed=world.get("seed", 1),
                size=world.get("size", "micro"),
                patrons=world.get("patrons", 8),
                key=key,
            )
            manifest = self.call(WorldBuilder(self.state.sim, self.state.patrons, spec).build)
        mid = manifest["merchant_id"]
        self.state.commands.merchant_ids.add(mid)
        owner = manifest["owner_id"]
        self.state.sessions[CONSOLE] = Session(mid, owner, "owner", channel="console", step_up=True)
        self.state.sessions[DEVICE] = Session(mid, owner, "owner", channel="device")
        self.saved.update(merchant_id=mid, world=manifest)
        self.saved.update({sku.lower().replace("-", "_"): item for sku, item in manifest["items"].items()})
        self.pump()

    def pump(self) -> None:
        mid = self.saved["merchant_id"]
        for _ in range(2):
            self.call(self.state.commands.run_due, mid)
            self.call(self.state.events.dispatch, mid)
            self.call(self.state.runtime.tick, mid)

    def snapshot(self, name: str) -> Path:
        folder = Path(self.state.settings.data_dir) / "snapshots"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{name}.db"
        path.unlink(missing_ok=True)
        self.call(self.state.db.snapshot, path)
        path.with_suffix(".json").write_text(json.dumps({"clock": iso_utc(self.state.clock.now())}))
        return path

    # inputs ------------------------------------------------------------------------------------------------
    def command(self, spec: dict[str, Any], surface: str = "console") -> dict[str, Any]:
        self.n += 1
        # patron profiles are PII: they go through their own route, which keeps them off the command log
        response = self.client.post(
            "/v1/patrons" if spec["type"] == "patrons.add" else "/v1/commands",
            json=spec.get("payload", {})
            if spec["type"] == "patrons.add"
            else {"type": spec["type"], "payload": spec.get("payload", {})},
            headers={**self.auth(surface), "Idempotency-Key": spec.get("key") or f"scenario-{self.n}"},
        )
        if response.status_code != 200:
            return {"status": "refused", "code": response.json().get("code"), "problem": response.json()}
        result: dict[str, Any] = response.json()
        if result["status"] == "needs_approval" and spec.get("approve", True):
            result = self.approve(result["thread_id"])
        return result

    def approve(self, thread_id: str) -> dict[str, Any]:
        self.n += 1
        response = self.client.post(
            "/v1/approvals/" + thread_id,
            json={"decision": "approve"},
            headers={**self.auth(), "Idempotency-Key": f"scenario-{self.n}"},
        )
        result: dict[str, Any] = response.json()
        if result.get("status") == "queued":
            self.clock_minutes(1)
            self.pump()
        return result

    def clock_minutes(self, minutes: int) -> None:
        response = self.client.post("/v1/director/clock", json={"advance_minutes": minutes}, headers=DIRECTOR)
        assert response.status_code == 200, response.text

    def persona(self, name: str) -> dict[str, Any]:
        world = self.saved["world"]
        found = world["patrons"].get(name) or world["suppliers"].get(name)
        if found is None:
            raise BeatFailed(f"unknown persona {name}")
        return dict(found)

    def act(self, action: dict[str, Any], beat: dict[str, Any]) -> None:
        action = substitute(action, self.saved)
        sim, mid = self.state.sim, self.saved["merchant_id"]
        if "say_for_me" in action:
            self.n += 1
            surface = action.get("surface", "console")
            body: dict[str, Any] = {"text": action["say_for_me"], "surface": surface}
            if self.saved.get("bill") and surface != "whatsapp":
                body["bill_id"] = self.saved["bill"]
            response = self.client.post(
                "/v1/turns",
                json=body,
                headers={
                    **self.auth("device" if surface == "device" else "console"),
                    "Idempotency-Key": f"turn-{self.n}",
                },
            )
            assert response.status_code == 200, response.text
            self.last = response.json()
        elif "command" in action:
            self.last = self.command(action["command"])
        elif action.get("approve_all"):
            gates = self.client.get("/v1/views/notifications", headers=self.auth()).json()["needs_you"]
            self.last = [self.approve(g["thread_id"]) for g in gates]
        elif "persona_action" in action:
            spec = action["persona_action"]
            who = self.persona(spec["persona"])
            kind = spec["action"]
            if kind in {"pay_qr", "pay_pending"}:
                intent = self.command({"type": "counter.request_upi", "payload": {"bill_id": spec["bill"]}})[
                    "data"
                ]
                qr = self.call(sim.create_qr, mid, intent["order_ref"], intent["amount_paise"])
                self.last = self.call(
                    sim.pay,
                    mid,
                    token=qr["token"],
                    payer_vpa=who.get("vpa", "x@upi"),
                    outcome="pending" if kind == "pay_pending" else "success",
                )
            elif kind == "complete":
                self.last = self.call(sim.complete, mid, spec["utr"], spec.get("outcome", "success"))
            elif kind == "pay_static":
                self.last = self.call(
                    sim.pay, mid, payer_vpa=who.get("vpa", "x@upi"), amount_paise=spec["amount_paise"]
                )
            elif kind == "message":
                self.last = self.call(sim.inbound, mid, who["persona"], spec["text"])
            elif kind == "stop":
                self.n += 1
                self.last = self.call(self.state.patrons.stop, mid, who["id"], f"evt_{self.n:026d}")
            self.pump()
        elif "clock" in action:
            if action["clock"].get("advance_minutes"):
                self.clock_minutes(action["clock"]["advance_minutes"])
            for _ in range(action["clock"].get("jump_days", 0)):
                self.clock_minutes(24 * 60)
                self.pump()
            self.pump()
        elif "fault" in action:
            if action["fault"].get("rails"):
                self.call(sim.add_fault, mid, action["fault"]["rails"])
            if "providers_down" in action["fault"]:
                self.state.router.offline = bool(action["fault"]["providers_down"])
        elif "locale" in action:
            payload = {"screen_lang": action["locale"]["screen"]} if "screen" in action["locale"] else {}
            if "speech" in action["locale"]:
                payload["speech_lang"] = action["locale"]["speech"]
            self.last = self.command({"type": "merchant.update_settings", "payload": payload})
        elif "read" in action:
            response = self.client.get("/v1/views/" + action["read"], headers=self.auth())
            assert response.status_code == 200, response.text
            self.last = response.json()
        elif action.get("settle"):
            self.last = self.call(sim.settle, mid, self.state.clock.now_ist().date().isoformat())
        elif action.get("tick"):
            self.pump()
        else:
            raise BeatFailed(f"{beat['id']}: unknown input {action}")

    # expectations ---------------------------------------------------------------------------------------
    def expect_turn(self, check: dict[str, Any], beat: dict[str, Any]) -> None:
        env = self.last or {}
        turns = self.client.get("/v1/views/ask", headers=self.auth()).json()["turns"]
        intent = turns[-1]["intent"] if turns else None
        if "intent" in check and not str(intent).startswith(check["intent"]):
            raise BeatFailed(f"{beat['id']}: intent {intent} != {check['intent']}")
        if (
            "speech_contains" in check
            and check["speech_contains"].lower() not in env["speech"]["text"].lower()
        ):
            raise BeatFailed(f"{beat['id']}: speech {env['speech']['text']!r}")
        if "presence" in check and env["presence"]["state"] != check["presence"]:
            raise BeatFailed(f"{beat['id']}: presence {env['presence']}")
        if "nav" in check and (env.get("nav") or {}).get("screen") != check["nav"]:
            raise BeatFailed(f"{beat['id']}: nav {env.get('nav')}")
        if "tier" in check and env.get("tier") != check["tier"]:
            raise BeatFailed(f"{beat['id']}: tier {env.get('tier')}")

    def expect(self, check: dict[str, Any], beat: dict[str, Any]) -> None:
        check = substitute(check, self.saved)
        if check.get("invariants"):
            from arth.governance.repository import Repository
            from arth.sim.invariants import check as invariants

            async def run() -> list[str]:
                async with self.state.db.read() as conn:
                    return await invariants(Repository(conn, self.saved["merchant_id"]), self.state.clock)

            problems = self.call(run)
            if problems:
                raise BeatFailed(f"{beat['id']}: invariants {problems[:3]}")
            return
        if "sim_thread" in check:
            threads = self.call(self.state.sim.threads, self.saved["merchant_id"])
            who = self.persona(check["sim_thread"])
            thread = next((t for t in threads if t["persona_id"] == who["persona"]), None)
            templates = [
                m["body"].get("template")
                for m in (thread or {}).get("messages", [])
                if m["direction"] == "out"
            ]
            if check.get("outbound_template") and check["outbound_template"] not in templates:
                raise BeatFailed(f"{beat['id']}: {who['persona']} got {templates}")
            return
        if "result" in check:  # assert on the last input's result (e.g. a refused command's code)
            value = dig(self.last, check["result"])
            check = {**check, "view": "(last result)", "path": check["result"]}
        else:
            response = self.client.get("/v1/views/" + check["view"], headers=self.auth())
            if response.status_code != 200:
                raise BeatFailed(
                    f"{beat['id']}: view {check['view']} → {response.status_code} {response.text[:200]}"
                )
            value = dig(response.json(), check.get("path", ""))
        ok = True
        if "equals" in check:
            ok &= value == check["equals"]
        if "gte" in check:
            ok &= value is not None and value >= check["gte"]
        if "lte" in check:
            ok &= value is not None and value <= check["lte"]
        if "len" in check:
            ok &= value is not None and len(value) == check["len"]
        if "contains" in check:
            ok &= value is not None and (
                str(check["contains"]).lower() in value.lower()
                if isinstance(value, str)
                else check["contains"] in value
            )
        if check.get("absent"):
            ok &= value in (None, [], {})
        if check.get("present"):
            ok &= value not in (None, [], {}, "")
        if not ok:
            raise BeatFailed(
                f"{beat['id']}: {check['view']}:{check.get('path')} = {str(value)[:300]} vs {check}"
            )

    # run --------------------------------------------------------------------------------------------------
    def run(self, scenario: dict[str, Any], cut: str | None = None) -> dict[str, Any]:
        self.setup(scenario)
        if scenario.get("locale"):
            self.act({"locale": scenario["locale"]}, {"id": "setup"})
        wanted = set(scenario.get("cut", {}).get(cut, [])) if cut else None
        report = []
        for scene in scenario["scenes"]:
            if wanted is not None and scene["id"] not in wanted:
                continue
            self.snapshot(f"{scenario['scenario']}-scene-{scene['id']}")
            for beat in scene["beats"]:
                started = time.monotonic()
                for action in beat.get("input", []):
                    self.act(action, beat)
                for name, path in beat.get("save", {}).items():
                    self.saved[name] = dig(self.last, path)
                if beat.get("expect_turn"):
                    self.expect_turn(beat["expect_turn"], beat)
                for check in beat.get("expect", []):
                    self.expect(check, beat)
                elapsed = int((time.monotonic() - started) * 1000)
                if beat.get("within_ms") and elapsed > beat["within_ms"] * 5:  # generous headless margin
                    raise BeatFailed(f"{beat['id']}: {elapsed} ms > {beat['within_ms']} ms budget")
                report.append({"scene": scene["id"], "beat": beat["id"], "ok": True, "ms": elapsed})
        if scenario.get("invariants", "default") == "default":
            self.expect({"invariants": True}, {"id": "final"})
        return {"scenario": scenario["scenario"], "beats": report, "merchant_id": self.saved["merchant_id"]}


def run_file(path: Path, settings: Settings | None = None, cut: str | None = None) -> dict[str, Any]:
    from arth.main import create_app

    scenario = load(path)
    app = create_app(settings or isolated_settings())
    with TestClient(app) as client:
        return ScenarioRunner(client).run(scenario, cut)


def cue_cards(scenario: dict[str, Any], report: dict[str, Any] | None = None) -> str:
    """T8.7: printable cue cards (who says or does what, the screen, and the measured time per beat)."""
    timings = {r["beat"]: r["ms"] for r in (report or {}).get("beats", [])}
    lines = [f"# {scenario['title']}", "", f"Scenario `{scenario['scenario']}` · pack {scenario['pack']}", ""]
    for scene in scenario["scenes"]:
        lines.append(f"## Scene {scene['id']}: {scene['title']}")
        for beat in scene["beats"]:
            ms = f" · {timings[beat['id']]} ms" if beat["id"] in timings else ""
            focus = beat.get("focus", {})
            screen = f" · screen {focus['device_screen']}" if focus.get("device_screen") else ""
            lines.append(f"- **{beat['id']}** ({beat.get('who', 'P1')}){screen}{ms}: {beat['cue']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run scenarios headless (demo-check)")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--cut", default=None)
    parser.add_argument("--cues", action="store_true", help="also write cues.md next to each scenario")
    args = parser.parse_args()
    paths = [Path(p) for p in args.paths] or sorted(SCENARIOS_DIR.glob("*/scenario.yaml"))
    failures = 0
    for path in paths:
        passes, report = 0, None
        for _ in range(args.runs):
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    report = run_file(path, isolated_settings(data_dir=Path(tmp)), args.cut)
                    passes += 1
                except (AssertionError, ValueError) as exc:
                    print(f"  FAIL {path.parent.name}: {str(exc)[:300]}")
        print(f"{path.parent.name}: {passes}/{args.runs} green")
        failures += args.runs - passes
        if args.cues and report:
            (path.parent / "cues.md").write_text(cue_cards(load(path), report), encoding="utf-8")
    print("demo-check:", "GREEN" if not failures else f"{failures} failed run(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
