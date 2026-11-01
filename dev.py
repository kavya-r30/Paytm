#!/usr/bin/env python3
"""Arth task runner: a cross-platform replacement for make.

Usage: python dev.py <target> [<target> ...]
Targets: setup, gen, gen-check, lint, typecheck, test, check, build-web, api, web, seed, scenario, demo-check, ai-smoke,
e2e, demo
(demo = kirana stage demo: restores the saved shop in seconds; `-- --fresh` rebuilds it)
(check = gen-check, lint, typecheck, test; gen-check fails when generated contract code is stale)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"


def _exe(name: str) -> list[str]:
    path = shutil.which(name)
    if path:
        return [path]
    if name == "uv":
        return [sys.executable, "-m", "uv"]
    sys.exit(f"'{name}' was not found on PATH")


def _call(*cmd: str, cwd: Path = ROOT) -> int:
    argv = _exe(cmd[0]) + list(cmd[1:])
    print(f"\n$ {' '.join(cmd)}   [{cwd.relative_to(ROOT)}]", flush=True)
    return subprocess.run(argv, cwd=cwd).returncode


def run(*cmd: str, cwd: Path = ROOT) -> None:
    code = _call(*cmd, cwd=cwd)
    if code:
        sys.exit(code)


def setup() -> None:
    run("uv", "sync", cwd=BACKEND)
    run("pnpm", "install")


def gen() -> None:
    run("uv", "run", "python", "-m", "arth.tools.gen_contracts", cwd=BACKEND)
    run("pnpm", "--filter", "frontend", "run", "gen")
    run("pnpm", "--filter", "frontend", "run", "tokens")


def gen_check() -> None:
    """Fail if generated contract code differs from a fresh `gen` (checks both sides, then exits)."""
    codes = [
        _call(
            "uv",
            "run",
            "python",
            "-m",
            "arth.tools.gen_contracts",
            "--check",
            cwd=BACKEND,
        ),
        _call("pnpm", "--filter", "frontend", "run", "gen:check"),
    ]
    if any(codes):
        sys.exit(1)


def lint() -> None:
    run("uv", "run", "ruff", "check", "arth", "tests", cwd=BACKEND)
    run("uv", "run", "ruff", "format", "--check", "arth", "tests", cwd=BACKEND)
    run("pnpm", "--filter", "frontend", "run", "lint")


def typecheck() -> None:
    run("uv", "run", "mypy", "arth", cwd=BACKEND)
    run("pnpm", "--filter", "frontend", "run", "typecheck")


def test() -> None:
    run("uv", "run", "pytest", "-q", cwd=BACKEND)
    run("pnpm", "--filter", "frontend", "run", "test")


def check() -> None:
    gen_check()
    lint()
    typecheck()
    test()


def build_web() -> None:
    run("pnpm", "--filter", "frontend", "run", "build")


def api() -> None:
    # open SSE streams (every live surface holds one) would block a reload forever without a shutdown cap
    run(
        "uv",
        "run",
        "uvicorn",
        "arth.main:app",
        "--reload",
        "--port",
        "8000",
        "--timeout-graceful-shutdown",
        "3",
        cwd=BACKEND,
    )


def seed() -> None:
    """Generate a demo world: python dev.py seed [-- --pack cafe --days 30]."""
    extra = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    run("uv", "run", "python", "-m", "arth.sim.seed", *extra, cwd=BACKEND)


def scenario() -> None:
    """Run headless scenarios once: python dev.py scenario [-- scenarios/<id>/scenario.yaml ...]."""
    extra = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    run("uv", "run", "python", "-m", "arth.sim.scenario", *extra, cwd=BACKEND)


def demo_check() -> None:
    """T8.6: every scenario N times in a row (default 3; the demo bar is -- --runs 10), writes cues.md."""
    extra = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if "--runs" not in extra:
        extra = ["--runs", "3", *extra]
    run("uv", "run", "python", "-m", "arth.sim.scenario", "--cues", *extra, cwd=BACKEND)


def ai_smoke() -> None:
    """Live provider smoke test (needs network + backend/.env); records cassettes for offline replay."""
    run("uv", "run", "python", "-m", "arth.ai.smoke", cwd=BACKEND)


def e2e() -> None:
    """T7.18: API (fresh data dir, :8010) + web (:3010), then the Playwright matrix and live Director run.

    One-time on a new machine: pnpm --filter frontend exec playwright install chromium"""
    import os
    import tempfile
    import time
    import urllib.request

    extra = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    env = {
        **os.environ,
        "ARTH_DATA_DIR": tempfile.mkdtemp(prefix="arth-e2e-"),
        "ARTH_CORS_ORIGINS": '["http://localhost:3010"]',
        "NEXT_PUBLIC_API_URL": "http://localhost:8010",
    }
    # each server in its own process group, so stopping it also stops uvicorn / next-server under uv and pnpm
    group: dict[str, object] = (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    servers = [
        subprocess.Popen(
            _exe("uv") + ["run", "uvicorn", "arth.main:app", "--port", "8010"],
            cwd=BACKEND,
            env=env,
            **group,
        ),
        subprocess.Popen(
            _exe("pnpm") + ["exec", "next", "dev", "--port", "3010"],
            cwd=FRONTEND,
            env=env,
            **group,
        ),
    ]
    try:
        for url in ("http://localhost:8010/healthz", "http://localhost:3010/director"):
            for _ in range(120):
                try:
                    urllib.request.urlopen(url, timeout=30)
                    break
                except OSError:
                    time.sleep(2)
            else:
                sys.exit(f"e2e: {url} did not come up")
        code = _call(
            "node",
            "scripts/e2e.mjs",
            "--web",
            "http://localhost:3010",
            *extra,
            cwd=FRONTEND,
        )
    finally:
        for server in servers:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(server.pid)],
                    capture_output=True,
                )
            else:
                import signal

                os.killpg(server.pid, signal.SIGTERM)
    if code:
        sys.exit(code)


def web() -> None:
    run("pnpm", "--filter", "frontend", "run", "dev")


def demo() -> None:
    """Kirana stage demo, ready in seconds: restore the saved Gupta Diwali shop, or build and save it once.

    Needs `python dev.py api` and `python dev.py web` running. `-- --fresh` rebuilds the saved shop."""
    import json
    import time
    import urllib.error
    import urllib.request

    api, name = "http://localhost:8000", "kirana-demo"

    def post(path: str, body: dict[str, object], timeout: float = 30) -> dict[str, object]:
        request = urllib.request.Request(
            api + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer dev-director"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return dict(json.loads(response.read()))

    try:
        urllib.request.urlopen(api + "/healthz", timeout=5)
    except OSError:
        sys.exit("demo: the API is not running; start `python dev.py api` (and `python dev.py web`) first")
    started = time.monotonic()
    restored = None
    if "--fresh" not in sys.argv:
        try:
            restored = post("/v1/director/restore", {"name": name})
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
    if restored is None:
        # built in a clean throw-away database (fast, one shop), 40 days of history so forecasts work,
        # with Night Shift already run so Today opens with the owner's checklist; then restored here
        print("demo: building the Gupta Diwali kirana shop (40 days of history) in a clean database...")
        if _call("uv", "run", "python", "-m", "arth.tools.build_demo", "--name", name, cwd=BACKEND):
            sys.exit("demo: building the shop failed (see above)")
        post("/v1/director/restore", {"name": name})
    how = "restored" if restored else "built, saved and restored"
    print(f"demo: kirana shop ready in {time.monotonic() - started:.1f} s ({how})")
    print("  Stage (device + phones + logs): http://localhost:3000/stage")
    print("  Director (beats, clock, faults): http://localhost:3000/director  -> press Next beat")
    print("  Device alone:                    http://localhost:3000/device/home")


TARGETS: dict[str, Callable[[], None]] = {
    "setup": setup,
    "gen": gen,
    "gen-check": gen_check,
    "lint": lint,
    "typecheck": typecheck,
    "test": test,
    "check": check,
    "build-web": build_web,
    "api": api,
    "web": web,
    "seed": seed,
    "scenario": scenario,
    "demo-check": demo_check,
    "ai-smoke": ai_smoke,
    "e2e": e2e,
    "demo": demo,
}

if __name__ == "__main__":
    names = (
        sys.argv[1 : sys.argv.index("--")] if "--" in sys.argv else sys.argv[1:]
    ) or ["check"]
    unknown = [n for n in names if n not in TARGETS]
    if unknown:
        sys.exit(
            f"unknown target(s): {', '.join(unknown)}; choose from {', '.join(TARGETS)}"
        )
    for name in names:
        TARGETS[name]()
