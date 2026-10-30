#!/usr/bin/env python3
"""Arth task runner: a cross-platform replacement for make.

Usage: python dev.py <target> [<target> ...]
Targets: setup, gen, gen-check, lint, typecheck, test, check, build-web, api, web, seed, scenario, demo-check, ai-smoke
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
        _call("uv", "run", "python", "-m", "arth.tools.gen_contracts", "--check", cwd=BACKEND),
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
    run("uv", "run", "uvicorn", "arth.main:app", "--reload", "--port", "8000", cwd=BACKEND)


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


def web() -> None:
    run("pnpm", "--filter", "frontend", "run", "dev")


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
}

if __name__ == "__main__":
    names = (sys.argv[1 : sys.argv.index("--")] if "--" in sys.argv else sys.argv[1:]) or ["check"]
    unknown = [n for n in names if n not in TARGETS]
    if unknown:
        sys.exit(f"unknown target(s): {', '.join(unknown)}; choose from {', '.join(TARGETS)}")
    for name in names:
        TARGETS[name]()
