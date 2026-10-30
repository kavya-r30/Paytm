# Arth L0 Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **This project does not use git:** every task ends with a Checkpoint step (tests green) instead of a commit.

**Goal:** Build the foundation every later layer stands on: the repo, one cross-platform task runner, shared contracts with generated Python and TypeScript types, money and ID primitives, the Sim Clock and job scheduler, SQLite with migrations and snapshots, validated config, the vertical-pack registry, locale formatting, spans over SSE, design tokens, and booting API and web apps.

**Architecture:** A Python 3.12 FastAPI service in `backend/` and a Next.js 16 app in `frontend/`, sharing JSON Schemas and an OpenAPI document in `contracts/`. Pydantic models and TS types are generated from them. All time comes from `SimClock`; all writes go through a single-writer `Database`; all config is validated at boot. Pack manifests in `backend/packs/` can only tighten core policies.

**Tech Stack:** Python 3.12, uv, FastAPI, SQLAlchemy 2 (Core) + aiosqlite, Alembic, Pydantic v2 + pydantic-settings, python-ulid, Babel, sse-starlette, jsonschema, datamodel-code-generator, pytest + pytest-asyncio + hypothesis; Node 22, pnpm 10, Next.js 16, React 19, Tailwind CSS v4, TypeScript 5, Ajv, json-schema-to-typescript, openapi-typescript, Vitest, Prettier.

> **Repo restructure (after Task 12, 30 Oct 2026).** The repo was reorganised: `api/` → `backend/`, `web/` → `frontend/`, `packages/contracts/` → `contracts/`, `config/` → `backend/config/`, `packs/` → `backend/packs/`, `.env`/`.env.example` → `backend/`, `source/` → `design/generator/`, `previews/` → `design/previews/`, design boards → `design/boards/`, v5.1 docs → `docs/reference/`. `paths.py` now exposes `BACKEND_DIR` (was `API_DIR`), `CONTRACTS_DIR`, `CONFIG_DIR`, `PACKS_DIR`, `DATA_DIR`, `DESIGN_DIR`; `Settings` reads `backend/.env`. All paths and code blocks in this plan have been updated to the new layout; blocks for files the restructure edited now show the files as they are on disk.

**Spec:** `docs/specs/2026-10-30-arth-v6-merged-design.md`. This plan covers Part K1 (T0.1–T0.12) and contracts Part C.

**Conventions for every task:**
- Run commands from the repo root unless a step says `cd backend`. On PowerShell, `cd backend && …` works as written (PowerShell 7 supports `&&`).
- If a Checkpoint fails **only** on formatting, auto-fix and re-run: `cd backend && uv run ruff format arth tests && uv run ruff check --fix arth tests`, and `pnpm --filter frontend run format`. Formatting fixes never need a test change.
- Generated files (`backend/arth/contracts/*`, `frontend/lib/contracts/*`, `frontend/app/tokens.css`) are never edited by hand. Change `contracts/` and run `python dev.py gen`.
- If a generated Pydantic model drops the extra fields of `Card` (the round-trip test in Task 3 will fail), upgrade `datamodel-code-generator`. Current versions emit `extra='allow'` for `additionalProperties: true`.

---

## File structure (what L0 creates)

```
dev.py                                  task runner (replaces make)            [T1]
package.json, pnpm-workspace.yaml       pnpm workspace root                    [T1]
backend/pyproject.toml                      Python project, deps, ruff/mypy/pytest [T1]
backend/alembic.ini                         Alembic config                          [T6]
backend/migrations/env.py                   Alembic env (sync sqlite)               [T6]
backend/migrations/script.py.mako           Alembic revision template               [T6]
backend/migrations/versions/0001_l0_foundations.py   jobs + spans tables           [T6]
backend/arth/__init__.py
backend/arth/main.py                        create_app(), lifespan wiring           [T13]
backend/arth/api/__init__.py
backend/arth/api/problems.py                ProblemError + handler (RFC 9457)       [T13]
backend/arth/api/auth.py                    bearer-token dependencies               [T13]
backend/arth/api/health.py                  GET /healthz                            [T13]
backend/arth/api/director.py                GET /v1/director/ping                   [T13]
backend/arth/api/stream.py                  GET /v1/stream (SSE)                    [T11]
backend/arth/contracts/*.py                 GENERATED Pydantic models               [T3]
backend/arth/core/__init__.py
backend/arth/core/paths.py                  REPO_ROOT, BACKEND_DIR                      [T1]
backend/arth/core/ids.py                    prefixed ULIDs                          [T4]
backend/arth/core/money.py                  paise arithmetic                        [T4]
backend/arth/core/qty.py                    milli-unit quantities                   [T4]
backend/arth/core/clock.py                  SimClock, IST/UTC, iso helpers          [T5]
backend/arth/core/db.py                     Database (single writer), snapshot      [T6]
backend/arth/core/tables.py                 SQLAlchemy Core tables (jobs, spans)    [T6]
backend/arth/core/migrate.py                upgrade(db_path)                        [T6]
backend/arth/core/scheduler.py              Scheduler, tick_loop                    [T7]
backend/arth/core/config.py                 Settings + policies/providers          [T8]
backend/arth/core/calendar.py               India-wide calendar + CalendarIndex     [T8]
backend/arth/core/yamlconf.py               ConfigError, Strict, YAML load/validate [T8]
backend/arth/core/packs.py                  PackManifest, PackRegistry, merge       [T9]
backend/arth/core/i18n.py                   locales, money/date formatting          [T10]
backend/arth/core/spans.py                  Span, SpanBus                           [T11]
backend/arth/tools/__init__.py
backend/arth/tools/gen_contracts.py         JSON Schema → Pydantic                  [T3]
backend/tests/conftest.py                   db fixture                              [T6]
backend/tests/test_*.py                     one file per module                     [T1–T13]
contracts/envelope.schema.json response envelope v2 + Card           [T2]
contracts/events/event.schema.json  domain event base                 [T2]
contracts/problem.schema.json  problem JSON                            [T2]
contracts/openapi.yaml         HTTP API                                [T2, T13]
contracts/examples/envelope.example.json                              [T2]
contracts/fixtures/format_cases.json  shared py/web formatting cases  [T10]
contracts/tokens.json          design tokens from design/generator/c2.py         [T12]
backend/config/policies.yaml                    tiers, roles, caps, growth defaults     [T8]
backend/config/providers.yaml                   AI roles → provider chains              [T8]
backend/config/calendar/*.yaml                  India-wide festivals by state/city (written during planning) [T8]
.env.example, .env, frontend/.env.local      API keys (API only) and public web settings (written during planning) [T8]
backend/packs/kirana/manifest.yaml              reference pack                          [T9]
frontend/package.json, tsconfig.json, next.config.ts, postcss.config.mjs, vitest.config.ts, .prettierrc, .prettierignore [T1, T13]
frontend/scripts/gen-contracts.mjs           JSON Schema → TS + schema copy          [T3]
frontend/scripts/build-tokens.mjs            tokens.json → app/tokens.css            [T12]
frontend/lib/contracts/*                     GENERATED TS types + copied schemas     [T3]
frontend/lib/validate.ts                     Ajv validators                          [T3]
frontend/lib/format.ts                       money/date formatting (parity with py)  [T10]
frontend/app/globals.css, tokens.css (generated), layout.tsx, page.tsx, health-badge.tsx [T12, T13]
frontend/tests/*.test.ts                     Vitest                                  [T1, T3, T10, T12]
```

---

### Task 1: Toolchain and repo skeleton (T0.1)

**Files:**
- Create: `dev.py`, `package.json`, `pnpm-workspace.yaml`, `backend/pyproject.toml`, `backend/arth/__init__.py`, `backend/arth/core/__init__.py`, `backend/arth/core/paths.py`, `backend/tests/test_smoke.py`, `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vitest.config.ts`, `frontend/.prettierrc`, `frontend/.prettierignore`, `frontend/tests/smoke.test.ts`

- [ ] **Step 1: Install uv**

Run: `python -m pip install --upgrade uv`
Then: `python -m uv --version`
Expected: prints `uv 0.x.y`. (`dev.py` falls back to `python -m uv` when `uv` isn't on PATH.)

- [ ] **Step 2: Create the root files**

`dev.py`:
```python
#!/usr/bin/env python3
"""Arth task runner: a cross-platform replacement for make.

Usage: python dev.py <target> [<target> ...]
Targets: setup, gen, gen-check, lint, typecheck, test, check, build-web, api, web
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
}

if __name__ == "__main__":
    names = sys.argv[1:] or ["check"]
    unknown = [n for n in names if n not in TARGETS]
    if unknown:
        sys.exit(f"unknown target(s): {', '.join(unknown)}; choose from {', '.join(TARGETS)}")
    for name in names:
        TARGETS[name]()
```

`package.json`:
```json
{
  "name": "arth",
  "private": true,
  "packageManager": "pnpm@10.8.0"
}
```

`pnpm-workspace.yaml`:
```yaml
packages:
  - frontend
```

- [ ] **Step 3: Create the Python project**

`backend/pyproject.toml`:
```toml
[project]
name = "arth-api"
version = "0.1.0"
description = "Arth: AI business partner for Paytm merchants (API, simulators, agents)"
requires-python = ">=3.12,<3.13"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "pydantic>=2.8",
  "pydantic-settings>=2.4",
  "sqlalchemy[asyncio]>=2.0.30",
  "aiosqlite>=0.20",
  "alembic>=1.13",
  "pyyaml>=6.0",
  "python-ulid>=2.7",
  "babel>=2.15",
  "sse-starlette>=2.1",
  "jsonschema>=4.23",
  "tzdata>=2024.1",
  # jsonschema's format_checker skips date-time / uri-reference silently without these two
  "rfc3339-validator>=0.1.4",
  "rfc3986-validator>=0.1.1",
]

[dependency-groups]
dev = [
  "pytest>=8.3",
  "pytest-asyncio>=0.24",
  "hypothesis>=6.112",
  "httpx>=0.27",
  "ruff>=0.6",
  "mypy>=1.11",
  "types-PyYAML>=6.0",
  "datamodel-code-generator>=0.26",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["arth"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]

[tool.ruff]
line-length = 110
target-version = "py312"
extend-exclude = ["arth/contracts", "migrations/versions"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "DTZ"]

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
disallow_untyped_defs = true
exclude = ["arth/contracts/"]
```
(`tzdata` matters: Windows has no system zoneinfo database, and `Asia/Kolkata` must resolve.)

`backend/arth/__init__.py`:
```python
"""Arth API package."""
```

`backend/arth/core/__init__.py`:
```python
"""Foundations shared by every layer: clock, money, ids, db, config, packs, i18n, spans."""
```

`backend/arth/core/paths.py`:
```python
"""Well-known repository paths.

Layout: backend/ holds the Python app plus config/, packs/, data/ and .env; contracts/ and design/
sit beside it at the repo root. Per-directory overrides live in Settings (ARTH_DATA_DIR,
ARTH_CONFIG_DIR, ARTH_PACKS_DIR).
"""

from __future__ import annotations

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent
CONTRACTS_DIR = REPO_ROOT / "contracts"
CONFIG_DIR = BACKEND_DIR / "config"
PACKS_DIR = BACKEND_DIR / "packs"
DATA_DIR = BACKEND_DIR / "data"
DESIGN_DIR = REPO_ROOT / "design"
```

- [ ] **Step 4: Create the web package (tooling only; Next.js pages come in Task 13)**

`frontend/package.json`:
```json
{
  "name": "frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "next dev --port 3000",
    "build": "next build",
    "start": "next start --port 3000",
    "gen": "node scripts/gen-contracts.mjs",
    "gen:check": "node scripts/gen-contracts.mjs --check",
    "tokens": "node scripts/build-tokens.mjs",
    "lint": "prettier --check .",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  },
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "ajv": "^8.17.0",
    "ajv-formats": "^3.0.1"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.0.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "json-schema-to-typescript": "^15.0.0",
    "openapi-typescript": "^7.4.0",
    "prettier": "^3.3.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.6.0",
    "vitest": "^3.0.0"
  }
}
```

`frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "es2023"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "allowJs": false,
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts", ".next/dev/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

`frontend/vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: { environment: 'node', include: ['tests/**/*.test.ts'] },
});
```

`frontend/.prettierrc`:
```json
{ "singleQuote": true, "printWidth": 110, "trailingComma": "all" }
```

`frontend/.prettierignore`:
```
.next
node_modules
lib/contracts
app/tokens.css
next-env.d.ts
```

- [ ] **Step 5: Write the smoke tests**

`backend/tests/test_smoke.py`:
```python
from arth.core.paths import BACKEND_DIR, REPO_ROOT


def test_repo_root_contains_task_runner() -> None:
    assert (REPO_ROOT / "dev.py").is_file()
    assert BACKEND_DIR.name == "backend"
```

`frontend/tests/smoke.test.ts`:
```ts
import { describe, expect, it } from 'vitest';

describe('toolchain', () => {
  it('runs vitest', () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] **Step 6: Install and run**

Run: `python dev.py setup`
Expected: `uv sync` creates `backend/.venv` and installs; `pnpm install` installs web deps without errors.

Run: `python dev.py test`
Expected: pytest `1 passed`; vitest `1 passed`.

- [ ] **Step 7: Checkpoint**

Run: `python dev.py lint`
Expected: ruff reports no issues; prettier reports all files formatted (run `pnpm --filter frontend run format` once if not).

---

### Task 2: Contracts: envelope, card, event, problem, OpenAPI (T0.2)

**Files:**
- Create: `contracts/envelope.schema.json`, `contracts/events/event.schema.json`, `contracts/problem.schema.json`, `contracts/openapi.yaml`, `contracts/examples/envelope.example.json`
- Test: `backend/tests/test_contract_schemas.py`

Schemas use JSON Schema draft-07 with `definitions`. That's the dialect all three tools (jsonschema, datamodel-code-generator, json-schema-to-typescript/Ajv) handle identically.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_contract_schemas.py`:
```python
import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

from arth.core.paths import CONTRACTS_DIR
from arth.core.schemas import ContractError, discover_schemas, load_schemas, schema, validator

EXAMPLES = sorted((CONTRACTS_DIR / "examples").glob("*.example.json"))
SCHEMAS = discover_schemas()


def load(rel: str) -> dict[str, Any]:
    return json.loads((CONTRACTS_DIR / rel).read_text(encoding="utf-8"))


def example(name: str) -> dict[str, Any]:
    return load(f"examples/{name}.example.json")


def errors(name: str, instance: object) -> list[str]:
    return [e.message for e in validator(name).iter_errors(instance)]


def test_discovery_finds_every_contract() -> None:
    assert set(SCHEMAS) == {"common", "envelope", "event", "problem"}
    assert SCHEMAS["event"] == CONTRACTS_DIR / "events" / "event.schema.json"


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_schema_is_valid_draft7_with_title_and_id(name: str) -> None:
    Draft7Validator.check_schema(schema(name))  # load_schemas() already enforced title and $id


def test_every_example_has_a_schema() -> None:
    assert EXAMPLES, "contracts/examples/ is empty"
    for path in EXAMPLES:
        assert path.name.removesuffix(".example.json") in SCHEMAS, f"{path.name} has no matching schema"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_validates_against_its_schema(path: Path) -> None:
    name = path.name.removesuffix(".example.json")
    validator(name).validate(json.loads(path.read_text(encoding="utf-8")))


def test_format_checker_is_active() -> None:
    bad = example("envelope")
    bad["undo"]["until"] = "yesterday"
    assert errors("envelope", bad), "date-time format must be enforced"
    bad_problem = example("problem")
    bad_problem["type"] = "not a uri"
    assert errors("problem", bad_problem), "uri-reference format must be enforced"


def _set(path: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(doc: dict[str, Any]) -> None:
        *parents, last = path.split(".")
        target: Any = doc
        for key in parents:
            target = target[int(key)] if isinstance(target, list) else target[key]
        if isinstance(target, list):
            target[int(last)] = value
        else:
            target[last] = value

    return mutate


NEGATIVE: list[tuple[str, str, Callable[[dict[str, Any]], None]]] = [
    ("envelope", "bad ULID turn_id", _set("turn_id", "turn_01JBQ0Z7Y8K3M4N5P6Q7R8S9TI")),
    ("envelope", "four followups", _set("followups", [{"label_key": "chip.a_b", "turn_text": "x"}] * 4)),
    ("envelope", "unknown presence state", _set("presence.state", "dancing")),
    ("envelope", "unknown card type", _set("cards", [{"type": "banner"}])),
    ("envelope", "extra top-level property", _set("mood", "happy")),
    ("envelope", "hi-Latn as speech locale", _set("lang.speech", "hi-Latn")),
    ("envelope", "unknown audience", _set("audience", "everyone")),
    ("envelope", "empty speech text", _set("speech.text", "")),
    ("envelope", "unprefixed card id", _set("cards.0.id", "01JBQ0Z7Y8K3M4N5P6Q7R8S9T1")),
    ("envelope", "unprefixed undo command_id", _set("undo.command_id", "cmd-1")),
    ("envelope", "label_key without a dot", _set("followups.0.label_key", "chip")),
    ("problem", "status 200", _set("status", 200)),
    ("problem", "empty title", _set("title", "")),
    ("problem", "empty message_key", _set("message_key", "")),
    ("event", "event type without a dot", _set("type", "ticked")),
    ("event", "empty merchant_id", _set("merchant_id", "")),
]


@pytest.mark.parametrize(("name", "case", "mutate"), NEGATIVE, ids=[c for _, c, _ in NEGATIVE])
def test_contract_rejects(name: str, case: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    bad = copy.deepcopy(example(name))
    mutate(bad)
    assert errors(name, bad), f"{name} should reject: {case}"


@pytest.mark.parametrize("key", schema("envelope")["required"])
def test_envelope_rejects_missing_required_key(key: str) -> None:
    bad = example("envelope")
    del bad[key]
    assert errors("envelope", bad), f"envelope without {key!r} must be rejected"


def test_card_type_list_matches_spec_c4() -> None:
    card_types = schema("envelope")["definitions"]["Card"]["properties"]["type"]["enum"]
    assert set(card_types) == {
        "bill",
        "hint",
        "approval",
        "batch",
        "verdict",
        "chart",
        "forecast",
        "brief",
        "offer",
        "plan",
        "campaign",
        "patron",
        "stock",
        "po",
        "quote_compare",
        "claim",
        "memory",
        "draft",
        "capital",
        "nudge",
        "pipeline",
        "receipt",
        "health",
    }


def test_shared_definitions_live_only_in_common() -> None:
    shared = set(schema("common")["definitions"])
    for name, doc in load_schemas().items():
        if name != "common":
            assert not shared & set(doc.get("definitions", {})), f"{name} duplicates a common definition"


def test_nullable_fields_use_any_of() -> None:
    assert '"oneOf"' not in json.dumps(load_schemas()), "use anyOf [ref, {type: null}] for nullable fields"


def test_no_union_type_arrays() -> None:
    """Ajv strict mode rejects `type: [a, b]`; spell unions and nullables with anyOf."""
    text = json.dumps(load_schemas())
    assert '"type": [' not in text


def test_event_requires_causation_fields() -> None:
    assert set(schema("event")["required"]) == {
        "event_id",
        "type",
        "merchant_id",
        "occurred_at",
        "actor",
        "causation_id",
        "payload",
    }


def test_event_missing_causation_id_is_rejected() -> None:
    event = example("event")
    del event["causation_id"]
    assert errors("event", event), "causation_id is required (null for root events)"


def test_root_event_with_null_causation_id_validates() -> None:
    event = example("event")
    event["causation_id"] = None
    event["actor"] = {"kind": "system", "id": None}
    validator("event").validate(event)


def _write(root: Path, rel: str, title: str | None = "T") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    doc: dict[str, Any] = {"$id": f"https://arth.local/contracts/{rel}"}
    if title:
        doc["title"] = title
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_discovery_skips_examples_and_fixtures(tmp_path: Path) -> None:
    _write(tmp_path, "a.schema.json")
    _write(tmp_path, "events/b.schema.json")
    _write(tmp_path, "examples/c.schema.json")
    _write(tmp_path, "fixtures/d.schema.json")
    assert list(discover_schemas(tmp_path)) == ["a", "b"]


def test_discovery_rejects_duplicate_names(tmp_path: Path) -> None:
    _write(tmp_path, "thing.schema.json")
    _write(tmp_path, "events/thing.schema.json")
    with pytest.raises(ContractError, match="duplicate contract name 'thing'"):
        discover_schemas(tmp_path)


def test_loading_requires_title_and_matching_id(tmp_path: Path) -> None:
    _write(tmp_path, "untitled.schema.json", title=None)
    with pytest.raises(ContractError, match="title"):
        load_schemas(tmp_path)
    (tmp_path / "untitled.schema.json").unlink()
    (tmp_path / "moved.schema.json").write_text(
        json.dumps({"title": "M", "$id": "https://arth.local/contracts/other.schema.json"}), encoding="utf-8"
    )
    with pytest.raises(ContractError, match=r"\$id"):
        load_schemas(tmp_path)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd backend && uv run pytest tests/test_contract_schemas.py -q`
Expected: FAIL with `FileNotFoundError` for `envelope.schema.json`.

- [ ] **Step 3: Write the schemas**

`contracts/envelope.schema.json`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/envelope.schema.json",
  "title": "Envelope",
  "description": "Everything Arth says or shows arrives as one envelope (spec Part C3).",
  "type": "object",
  "required": ["turn_id", "lang", "audience", "cards", "followups", "provenance", "presence", "sensitivity"],
  "additionalProperties": false,
  "properties": {
    "turn_id": { "type": "string", "pattern": "^turn_[0-9A-HJKMNP-TV-Z]{26}$" },
    "lang": { "$ref": "#/definitions/Lang" },
    "speech": { "anyOf": [{ "$ref": "#/definitions/Speech" }, { "type": "null" }] },
    "caption": { "anyOf": [{ "$ref": "#/definitions/Caption" }, { "type": "null" }] },
    "audience": { "$ref": "common.schema.json#/definitions/Audience" },
    "cards": { "type": "array", "items": { "$ref": "#/definitions/Card" } },
    "nav": { "anyOf": [{ "$ref": "#/definitions/Nav" }, { "type": "null" }] },
    "followups": {
      "type": "array",
      "description": "v6: at most 3; UI shows 2–3 chips including screen defaults.",
      "maxItems": 3,
      "items": { "$ref": "#/definitions/Followup" }
    },
    "provenance": { "type": "array", "items": { "$ref": "#/definitions/Provenance" } },
    "presence": { "$ref": "#/definitions/Presence" },
    "led": { "anyOf": [{ "$ref": "#/definitions/Led" }, { "type": "null" }] },
    "tier": { "anyOf": [{ "$ref": "common.schema.json#/definitions/Tier" }, { "type": "null" }] },
    "undo": { "anyOf": [{ "$ref": "#/definitions/Undo" }, { "type": "null" }] },
    "sensitivity": { "type": "string", "enum": ["normal", "discreet"] },
    "fallback": { "anyOf": [{ "$ref": "#/definitions/Fallback" }, { "type": "null" }] }
  },
  "definitions": {
    "Lang": {
      "type": "object",
      "required": ["screen", "speech"],
      "additionalProperties": false,
      "properties": {
        "screen": { "$ref": "common.schema.json#/definitions/Locale" },
        "speech": { "$ref": "common.schema.json#/definitions/SpeechLocale" }
      }
    },
    "Speech": {
      "type": "object",
      "required": ["text"],
      "additionalProperties": false,
      "properties": {
        "text": { "$ref": "common.schema.json#/definitions/NonEmptyString" },
        "voice": { "type": "string" },
        "ssml_ready": { "type": "boolean" }
      }
    },
    "Caption": {
      "type": "object",
      "additionalProperties": false,
      "properties": { "heard": { "type": "string" }, "said": { "type": "string" } }
    },
    "Card": {
      "type": "object",
      "description": "Base card. Each card type adds its own fields; per-type schemas arrive with the layer that produces them (see contracts/README.md).",
      "required": ["type"],
      "additionalProperties": true,
      "properties": {
        "type": {
          "type": "string",
          "enum": [
            "bill", "hint", "approval", "batch", "verdict", "chart", "forecast", "brief", "offer", "plan",
            "campaign", "patron", "stock", "po", "quote_compare", "claim", "memory", "draft", "capital",
            "nudge", "pipeline", "receipt", "health"
          ]
        },
        "id": { "$ref": "common.schema.json#/definitions/PrefixedId" },
        "audience": { "$ref": "common.schema.json#/definitions/Audience" },
        "note": { "type": "string", "description": "Arth's annotation; grounded before it is sent" }
      }
    },
    "Nav": {
      "type": "object",
      "required": ["screen"],
      "additionalProperties": false,
      "properties": {
        "screen": { "$ref": "common.schema.json#/definitions/NonEmptyString" },
        "params": { "type": "object", "additionalProperties": { "type": "string" } }
      }
    },
    "Followup": {
      "type": "object",
      "required": ["label_key", "turn_text"],
      "additionalProperties": false,
      "properties": {
        "label_key": { "$ref": "common.schema.json#/definitions/MessageKey" },
        "turn_text": { "$ref": "common.schema.json#/definitions/NonEmptyString" }
      }
    },
    "Provenance": {
      "type": "object",
      "required": ["kind"],
      "additionalProperties": false,
      "properties": {
        "kind": { "$ref": "common.schema.json#/definitions/NonEmptyString" },
        "count": { "type": "integer", "minimum": 0 }
      }
    },
    "Presence": {
      "type": "object",
      "required": ["state"],
      "additionalProperties": false,
      "properties": {
        "state": {
          "type": "string",
          "enum": ["idle", "listening", "thinking", "speaking", "needs_you", "done", "alert"]
        },
        "gaze": { "type": "string" }
      }
    },
    "Led": {
      "type": "object",
      "required": ["pattern", "color"],
      "additionalProperties": false,
      "properties": { "pattern": { "type": "string" }, "color": { "type": "string" } }
    },
    "Undo": {
      "type": "object",
      "required": ["command_id", "until"],
      "additionalProperties": false,
      "properties": {
        "command_id": { "$ref": "common.schema.json#/definitions/PrefixedId" },
        "until": { "type": "string", "format": "date-time" }
      }
    },
    "Fallback": {
      "type": "object",
      "required": ["channel"],
      "additionalProperties": false,
      "properties": { "channel": { "type": "string" }, "thread": { "type": "string" } }
    }
  }
}
```

`contracts/events/event.schema.json`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/event.schema.json",
  "title": "DomainEvent",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": ["event_id", "type", "merchant_id", "occurred_at", "actor", "causation_id", "payload"],
  "additionalProperties": false,
  "properties": {
    "event_id": { "type": "string", "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$" },
    "type": { "$ref": "../common.schema.json#/definitions/DottedCode" },
    "merchant_id": { "$ref": "../common.schema.json#/definitions/NonEmptyString" },
    "occurred_at": { "type": "string", "format": "date-time" },
    "actor": { "$ref": "#/definitions/Actor" },
    "causation_id": {
      "anyOf": [{ "$ref": "../common.schema.json#/definitions/PrefixedId" }, { "type": "null" }],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": { "type": "object" }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": ["kind"],
      "additionalProperties": false,
      "properties": {
        "kind": { "type": "string", "enum": ["owner", "staff", "customer", "supplier", "agent", "system", "simulator"] },
        "id": { "anyOf": [{ "$ref": "../common.schema.json#/definitions/NonEmptyString" }, { "type": "null" }] }
      }
    }
  }
}
```

`contracts/problem.schema.json`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/problem.schema.json",
  "title": "Problem",
  "description": "RFC 9457 problem details with a stable code and an i18n message key (spec Part C1).",
  "type": "object",
  "required": ["type", "title", "status", "code", "message_key"],
  "additionalProperties": false,
  "properties": {
    "type": { "type": "string", "format": "uri-reference" },
    "title": { "$ref": "common.schema.json#/definitions/NonEmptyString" },
    "status": { "type": "integer", "minimum": 400, "maximum": 599 },
    "code": { "$ref": "common.schema.json#/definitions/DottedCode" },
    "message_key": { "$ref": "common.schema.json#/definitions/MessageKey" },
    "detail": { "type": "string" },
    "params": {
      "type": "object",
      "description": "Values interpolated into the message_key text.",
      "additionalProperties": {
        "description": "integer is listed before number so whole numbers (e.g. paise) stay integers through Pydantic.",
        "anyOf": [{ "type": "string" }, { "type": "integer" }, { "type": "number" }, { "type": "boolean" }]
      }
    }
  }
}
```

`contracts/openapi.yaml`:
```yaml
openapi: 3.1.0
info:
  title: Arth API
  version: 0.1.0
  description: Spec Part C2. L0 exposes health, the SSE stream and a director ping; later layers add their families.
paths:
  /healthz:
    get:
      operationId: getHealth
      security: []
      responses:
        '200':
          description: Service health
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Health' }
  /v1/stream:
    get:
      operationId: getStream
      description: >-
        Server-sent events. L0 streams spans; L1 adds domain events, envelopes and view invalidations.
        Unauthenticated in L0: auth arrives with L1 sessions (STF-2), which use the reserved `device`
        and `console` security schemes.
      responses:
        '200':
          description: SSE stream
          content:
            text/event-stream:
              schema: { type: string }
  /v1/director/ping:
    get:
      operationId: directorPing
      security:
        - director: []
      responses:
        '200':
          description: Director token accepted
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Ok' }
        '401':
          $ref: '#/components/responses/Problem'
components:
  securitySchemes:
    director:
      type: http
      scheme: bearer
      description: Presenter token for /v1/director/* (L0).
    device:
      type: http
      scheme: bearer
      description: Reserved for L1 device sessions (STF-2); no L0 route uses it yet.
    console:
      type: http
      scheme: bearer
      description: Reserved for L1 Console sessions (STF-2); no L0 route uses it yet.
  responses:
    Problem:
      description: RFC 9457 problem details (spec Part C1)
      content:
        application/problem+json:
          schema: { $ref: '#/components/schemas/Problem' }
  schemas:
    Problem:
      $ref: './problem.schema.json'
    Health:
      type: object
      required: [status, mode, clock, packs, providers]
      properties:
        status: { type: string, enum: [ok] }
        mode: { type: string, enum: [dev, test, demo, prod] }
        clock: { type: string, format: date-time }
        packs: { type: array, items: { type: string } }
        providers:
          type: object
          description: Whether each AI provider has an API key configured (booleans only, never the key)
          additionalProperties: { type: boolean }
    Ok:
      type: object
      required: [ok]
      properties:
        ok: { type: boolean }
```

`contracts/examples/envelope.example.json` (the spec C3 example with valid IDs):
```json
{
  "turn_id": "turn_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "lang": { "screen": "hi-Latn", "speech": "hi-IN" },
  "speech": { "text": "Parle-G joda. Kul ₹62.", "voice": "sarvam:bulbul", "ssml_ready": true },
  "caption": { "heard": "aur ek Parle-G", "said": "Parle-G joda. Kul ₹62." },
  "audience": "all",
  "cards": [
    { "type": "bill", "id": "bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1", "audience": "all" },
    {
      "type": "hint",
      "audience": "owner",
      "patron_ref": "pat_01JBQ0Z7Y8K3M4N5P6Q7R8S9T2",
      "item_ref": "item_01JBQ0Z7Y8K3M4N5P6Q7R8S9T3",
      "reason_key": "hint.weekday_habit"
    }
  ],
  "nav": { "screen": "bill", "params": { "bill_id": "bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1" } },
  "followups": [{ "label_key": "chip.aaj_kitna_aaya", "turn_text": "Aaj kitna aaya?" }],
  "provenance": [{ "kind": "bills", "count": 214 }, { "kind": "upi_ledger" }],
  "presence": { "state": "speaking", "gaze": "card" },
  "led": { "pattern": "solid", "color": "signal" },
  "tier": null,
  "undo": { "command_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T4", "until": "2026-10-29T03:43:30Z" },
  "sensitivity": "normal",
  "fallback": { "channel": "messages", "thread": "owner" }
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd backend && uv run pytest tests/test_contract_schemas.py -q`
Expected: `7 passed` (3 parametrised schema checks + 4 tests).

- [ ] **Step 5: Checkpoint**

Run: `python dev.py test`
Expected: all green.

---

### Task 3: Codegen for Python and TypeScript, plus round-trip tests (T0.3)

**Files:**
- Create: `backend/arth/tools/__init__.py`, `backend/arth/tools/gen_contracts.py`, `frontend/scripts/gen-contracts.mjs`, `frontend/lib/validate.ts`
- Generated: `backend/arth/contracts/{__init__,envelope,event,problem}.py`, `frontend/lib/contracts/{envelope,event,problem,api}.ts`, `frontend/lib/contracts/schemas/*.schema.json`
- Test: `backend/tests/test_contract_roundtrip.py`, `frontend/tests/contracts.test.ts`

- [ ] **Step 1: Write the failing Python test**

`backend/tests/test_contract_roundtrip.py`:
```python
import importlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from arth.core.paths import BACKEND_DIR, CONTRACTS_DIR
from arth.core.schemas import discover_schemas, schema

EXAMPLES = sorted((CONTRACTS_DIR / "examples").glob("*.example.json"))
GENERATED = BACKEND_DIR / "arth" / "contracts"
HEADER = "# Generated from contracts. Do not edit; run `python dev.py gen`."


def model_for(name: str) -> type[BaseModel]:
    """The generated model for a contract: module = contract name, class = schema title."""
    model = getattr(importlib.import_module(f"arth.contracts.{name}"), schema(name)["title"])
    assert issubclass(model, BaseModel)
    return model


def round_trip(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    # exclude_unset keeps explicit nulls (a dropped null would fail the exact comparison below)
    dumped: dict[str, Any] = model_for(name).model_validate(raw).model_dump(mode="json", exclude_unset=True)
    return dumped


def canonical(value: Any) -> str:
    # JSON text, not Python equality: 200000 == 200000.0 in Python, but they are different JSON.
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_round_trips_exactly(path: Path) -> None:
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert canonical(round_trip(path.name.removesuffix(".example.json"), raw)) == canonical(raw)


def test_explicit_nulls_survive_the_round_trip() -> None:
    raw = json.loads((CONTRACTS_DIR / "examples" / "envelope.example.json").read_text(encoding="utf-8"))
    raw |= {"speech": None, "nav": None, "tier": None, "led": None}
    assert round_trip("envelope", raw) == raw

    event = json.loads((CONTRACTS_DIR / "examples" / "event.example.json").read_text(encoding="utf-8"))
    event |= {"causation_id": None, "actor": {"kind": "system", "id": None}}
    assert round_trip("event", event) == event


def test_documented_imports_work() -> None:
    from arth.contracts.envelope import Envelope
    from arth.contracts.event import DomainEvent
    from arth.contracts.problem import Problem

    names = {Envelope.__name__, DomainEvent.__name__, Problem.__name__}
    assert names == {"Envelope", "DomainEvent", "Problem"}


def test_one_generated_module_per_contract() -> None:
    modules = {p.stem for p in GENERATED.glob("*.py")} - {"__init__"}
    assert modules == set(discover_schemas())


def test_generated_files_carry_do_not_edit_header() -> None:
    for path in GENERATED.glob("*.py"):
        assert path.read_text(encoding="utf-8").startswith(HEADER), path.name
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd backend && uv run pytest tests/test_contract_roundtrip.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.contracts'`.

- [ ] **Step 3: Write the Python generator**

`backend/arth/tools/__init__.py`:
```python
"""Developer tools (code generation, maintenance scripts)."""
```

`backend/arth/tools/gen_contracts.py`:
```python
"""Generate Pydantic v2 models from the contracts JSON Schemas.

Run: python dev.py gen          (or: cd backend && uv run python -m arth.tools.gen_contracts)
     python dev.py gen-check    (--check: exit 1 if the committed models differ from a fresh run)

Every contract (see arth.core.schemas) becomes `arth/contracts/<name>.py` with a class named by the
schema's `title`. The schemas are staged flat as `<name>.json`, with cross-file `$ref`s rewritten to
those names, and generated in one datamodel-codegen run: shared definitions are emitted once in
`common.py` and imported by the other modules instead of being copied into each of them.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from arth.core.paths import BACKEND_DIR, CONTRACTS_DIR
from arth.core.schemas import ContractError, discover_schemas, load_schemas

OUT = BACKEND_DIR / "arth" / "contracts"
HEADER = "# Generated from contracts. Do not edit; run `python dev.py gen`."
STALE = "contracts are stale: run `python dev.py gen`"
CODEGEN = [sys.executable, "-m", "datamodel_code_generator"]
OPTIONS = [
    "--input-file-type",
    "jsonschema",
    "--output-model-type",
    "pydantic_v2.BaseModel",
    "--target-python-version",
    "3.12",
    "--use-standard-collections",
    "--use-union-operator",
    "--use-title-as-name",
    "--collapse-root-models",
    "--disable-timestamp",
    "--formatters",
    "black",
    "isort",
    "--custom-file-header",
    HEADER,
]


class GenError(RuntimeError):
    """Code generation failed; the message names the contracts involved."""


def _rewrite_refs(node: Any, source: Path, names: dict[Path, str]) -> Any:
    if isinstance(node, dict):
        out = {k: _rewrite_refs(v, source, names) for k, v in node.items()}
        ref = node.get("$ref")
        if isinstance(ref, str) and not ref.startswith("#"):
            file_part, _, fragment = ref.partition("#")
            target = (source.parent / file_part).resolve()
            if target not in names:
                raise GenError(f"{source.name}: $ref {ref!r} points at {file_part}, which is not a contract")
            out["$ref"] = f"{names[target]}.json#{fragment}"
        return out
    if isinstance(node, list):
        return [_rewrite_refs(v, source, names) for v in node]
    return node


def stage(contracts: Path, dest: Path) -> list[str]:
    """Copy every contract to dest/<name>.json with cross-file refs rewritten; return the names."""
    try:
        paths = discover_schemas(contracts)
        schemas = load_schemas(contracts)
    except ContractError as exc:
        raise GenError(str(exc)) from exc
    names = {path.resolve(): name for name, path in paths.items()}
    dest.mkdir(parents=True, exist_ok=True)
    for name, path in paths.items():
        staged = _rewrite_refs(schemas[name], path.resolve(), names)
        staged.pop("$id", None)  # resolve refs by staged file name, never by URL
        (dest / f"{name}.json").write_text(json.dumps(staged, ensure_ascii=False, indent=2), encoding="utf-8")
    return list(paths)


def _check_titles(generated: dict[str, bytes], titles: dict[str, str]) -> None:
    for name, title in titles.items():
        source = generated.get(f"{name}.py", b"").decode("utf-8")
        if not re.search(rf"^class {re.escape(title)}\(", source, re.MULTILINE):
            raise GenError(f"{name}: generated module has no class {title!r} (the schema title)")


def render(contracts: Path = CONTRACTS_DIR) -> dict[str, bytes]:
    """Generate every model in a temporary directory; return {file name: LF-normalised bytes}."""
    with tempfile.TemporaryDirectory(prefix="arth-gen-") as tmp:
        staged, out = Path(tmp) / "schemas", Path(tmp) / "models"
        names = stage(contracts, staged)
        argv = [*CODEGEN, "--input", str(staged), "--output", str(out), *OPTIONS]
        result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            raise GenError(
                f"datamodel-codegen failed for contracts {', '.join(names)} "
                f"(exit {result.returncode}):\n{result.stderr.strip() or result.stdout.strip()}"
            )
        generated = {
            p.name: p.read_bytes().replace(b"\r\n", b"\n")
            for p in sorted(out.glob("*.py"))
            if p.name != "__init__.py"
        }
    generated["__init__.py"] = (HEADER + "\n").encode("utf-8")
    _check_titles(generated, {name: s["title"] for name, s in load_schemas(contracts).items()})
    return dict(sorted(generated.items()))


def stale(expected: dict[str, bytes], out: Path) -> list[str]:
    """Files in out that differ from, are missing from, or are not in expected (sorted)."""
    present = {p.name for p in out.glob("*.py")}
    changed = [n for n in expected if n not in present or (out / n).read_bytes() != expected[n]]
    return sorted(changed + sorted(present - set(expected)))


def write(expected: dict[str, bytes], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, data in expected.items():
        (out / name).write_bytes(data)
        print(f"generated arth/contracts/{name}")
    for path in out.glob("*.py"):
        if path.name not in expected:
            path.unlink()
            print(f"removed stale arth/contracts/{path.name}")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        expected = render()
    except GenError as exc:
        print(f"gen_contracts: {exc}", file=sys.stderr)
        return 1
    if "--check" in args:
        files = stale(expected, OUT)
        if files:
            print(f"{STALE}\n" + "\n".join(f"  backend/arth/contracts/{f}" for f in files), file=sys.stderr)
            return 1
        print(f"contracts: {len(expected)} Python files are up to date")
        return 0
    write(expected, OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write the web generator and validators**

`frontend/scripts/gen-contracts.mjs`:
```js
// Generates TS types from the contracts, copies the schemas for Ajv, and writes the registry.
// Run via: python dev.py gen        (or: pnpm --filter frontend run gen)
//          python dev.py gen-check  (or: pnpm --filter frontend run gen:check) exits 1 when stale
//
// Every contracts/**/*.schema.json outside examples/ and fixtures/ is a contract named by its file
// stem (events/event.schema.json -> "event"); its `title` names the TS type. Outputs, all under
// lib/contracts/: <name>.ts, schemas/<name>.schema.json, api.ts (openapi.yaml) and index.ts.
// Nothing is written unless every contract compiles.
import { compileFromFile } from 'json-schema-to-typescript';
import openapiTS, { astToString } from 'openapi-typescript';
import { mkdir, readdir, readFile, unlink, writeFile } from 'node:fs/promises';
import { dirname, join, relative, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const FRONTEND = join(dirname(fileURLToPath(import.meta.url)), '..');
const CONTRACTS = join(FRONTEND, '..', 'contracts');
const OUT = join(FRONTEND, 'lib', 'contracts');
const BANNER = '/* Generated from contracts. Do not edit; run `python dev.py gen`. */';
const SUFFIX = '.schema.json';
const EXCLUDED = new Set(['examples', 'fixtures']);
const STALE = 'contracts are stale: run `python dev.py gen`';

class GenError extends Error {}

async function discover(dir = CONTRACTS) {
  const found = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!(dir === CONTRACTS && EXCLUDED.has(entry.name))) found.push(...(await discover(path)));
    } else if (entry.name.endsWith(SUFFIX)) {
      found.push({ name: entry.name.slice(0, -SUFFIX.length), path });
    }
  }
  return found;
}

async function contracts() {
  const byName = new Map();
  for (const c of (await discover()).sort((a, b) => a.name.localeCompare(b.name))) {
    const rel = relative(CONTRACTS, c.path).split(sep).join('/');
    if (byName.has(c.name)) {
      throw new GenError(`duplicate contract name "${c.name}": ${byName.get(c.name).rel} and ${rel}`);
    }
    const text = await readFile(c.path, 'utf-8');
    const schema = JSON.parse(text);
    if (typeof schema.title !== 'string' || !schema.title) {
      throw new GenError(`${rel}: a contract schema needs a non-empty "title" (the generated type name)`);
    }
    byName.set(c.name, { ...c, rel, text, schema, title: schema.title });
  }
  return [...byName.values()];
}

const toLf = (s) => s.replace(/\r\n/g, '\n');

function indexTs(all) {
  const lines = [BANNER, ''];
  for (const c of all) lines.push(`import type { ${c.title} } from './${c.name}';`);
  for (const c of all) lines.push(`import ${c.name}Schema from './schemas/${c.name}${SUFFIX}';`);
  lines.push('');
  for (const c of all) lines.push(`export type { ${c.title} } from './${c.name}';`);
  lines.push(
    "export type * from './common'; // shared definitions: Locale, SpeechLocale, Audience, Tier, ...",
  );
  lines.push(
    '',
    '/** Every contract: name (file stem), JSON Schema $id and the schema itself, for Ajv. */',
    'export const SCHEMAS = [',
    ...all.map((c) => `  { name: '${c.name}', id: '${c.schema.$id}', schema: ${c.name}Schema },`),
    '] as const;',
    '',
    "export type SchemaName = (typeof SCHEMAS)[number]['name'];",
    '',
    '/** The generated type for each contract name. */',
    'export interface ContractTypes {',
    ...all.map((c) => `  ${c.name}: ${c.title};`),
    '}',
    '',
  );
  return lines.join('\n');
}

async function render() {
  const all = await contracts();
  const files = new Map();
  const failures = [];
  for (const c of all) {
    try {
      // unreachableDefinitions: a definitions-only schema (common) still exports each definition as a type.
      const ts = await compileFromFile(c.path, {
        bannerComment: BANNER,
        cwd: dirname(c.path),
        unreachableDefinitions: true,
      });
      if (!new RegExp(`^export (interface|type) ${c.title}\\b`, 'm').test(ts)) {
        throw new GenError(`no exported type named "${c.title}" (the schema title)`);
      }
      files.set(`${c.name}.ts`, toLf(ts));
      files.set(`schemas/${c.name}${SUFFIX}`, toLf(c.text));
    } catch (err) {
      failures.push(`${c.rel}: ${err instanceof Error ? err.message : String(err)}`);
    }
  }
  try {
    const ast = await openapiTS(pathToFileURL(join(CONTRACTS, 'openapi.yaml')));
    files.set('api.ts', `${BANNER}\n\n${toLf(astToString(ast))}`);
  } catch (err) {
    failures.push(`openapi.yaml: ${err instanceof Error ? err.message : String(err)}`);
  }
  if (failures.length) throw new GenError(`code generation failed:\n  ${failures.join('\n  ')}`);
  files.set('index.ts', indexTs(all));
  return new Map([...files].sort(([a], [b]) => a.localeCompare(b)));
}

/** Generated files on disk: top-level *.ts and schemas/*.json under lib/contracts. */
async function existing() {
  const list = async (sub, ext) => {
    try {
      const entries = await readdir(join(OUT, sub), { withFileTypes: true });
      return entries
        .filter((e) => e.isFile() && e.name.endsWith(ext))
        .map((e) => (sub ? `${sub}/${e.name}` : e.name));
    } catch {
      return [];
    }
  };
  return [...(await list('', '.ts')), ...(await list('schemas', '.json'))];
}

async function stale(files) {
  const out = [];
  for (const [rel, content] of files) {
    const current = await readFile(join(OUT, rel), 'utf-8').catch(() => null);
    if (current !== content) out.push(rel);
  }
  for (const rel of await existing()) if (!files.has(rel)) out.push(rel);
  return out.sort();
}

async function main() {
  const check = process.argv.includes('--check');
  const files = await render();
  if (check) {
    const changed = await stale(files);
    if (changed.length) {
      console.error(`${STALE}\n${changed.map((f) => `  frontend/lib/contracts/${f}`).join('\n')}`);
      process.exitCode = 1;
      return;
    }
    console.log(`contracts: ${files.size} frontend files are up to date`);
    return;
  }
  await mkdir(join(OUT, 'schemas'), { recursive: true });
  for (const [rel, content] of files) await writeFile(join(OUT, rel), content);
  for (const rel of await existing()) {
    if (!files.has(rel)) {
      await unlink(join(OUT, rel));
      console.log(`contracts: removed stale lib/contracts/${rel}`);
    }
  }
  console.log(`contracts: wrote ${files.size} files to lib/contracts`);
}

try {
  await main();
} catch (err) {
  console.error(`gen-contracts: ${err instanceof Error ? err.message : String(err)}`);
  process.exitCode = 1;
}
```

`frontend/lib/validate.ts`:
```ts
// Runtime validation against the contract JSON Schemas (hand-written; the registry is generated).
// Every schema is added up front so cross-file $refs (common.schema.json) resolve by $id; each
// validator is compiled on first use and memoised by Ajv.
import Ajv, { type ValidateFunction } from 'ajv';
import addFormats from 'ajv-formats';
import { SCHEMAS, type ContractTypes, type Envelope, type SchemaName } from './contracts';

// strict: true with no exemptions. The contracts avoid union `type` arrays (see contracts/README.md),
// so neither strictTypes nor allowUnionTypes needs relaxing.
const ajv = new Ajv({ allErrors: true, strict: true });
addFormats(ajv);
for (const { schema } of SCHEMAS) ajv.addSchema(schema);

const ID_BY_NAME: Record<string, string> = Object.fromEntries(SCHEMAS.map((s) => [s.name, s.id]));

export function validator<N extends SchemaName>(name: N): ValidateFunction<ContractTypes[N]> {
  const id = ID_BY_NAME[name];
  if (!id) throw new Error(`no contract named "${name}"; known: ${Object.keys(ID_BY_NAME).join(', ')}`);
  const fn = ajv.getSchema<ContractTypes[N]>(id);
  if (!fn) throw new Error(`contract "${name}" (${id}) is not registered with Ajv`);
  return fn;
}

/** Validate data against a contract by name; on failure, `validator(name).errors` holds the reasons. */
export function validate<N extends SchemaName>(name: N, data: unknown): data is ContractTypes[N] {
  return validator(name)(data);
}

type NamedValidator<T> = ((data: unknown) => data is T) & { readonly errors: ValidateFunction['errors'] };

/** A validator bound to one contract, compiled on first call; `.errors` mirrors Ajv's last result. */
function lazy<N extends SchemaName>(name: N): NamedValidator<ContractTypes[N]> {
  const fn = (data: unknown): data is ContractTypes[N] => validate(name, data);
  return Object.defineProperty(fn, 'errors', { get: () => validator(name).errors }) as NamedValidator<
    ContractTypes[N]
  >;
}

export const validateEnvelope = lazy('envelope');
export const validateEvent = lazy('event');
export const validateProblem = lazy('problem');

/** Return data typed as an Envelope, or throw with Ajv's error text. */
export function parseEnvelope(data: unknown): Envelope {
  const fn = validator('envelope');
  if (!fn(data)) throw new Error(`invalid envelope: ${ajv.errorsText(fn.errors)}`);
  return data;
}
```

`frontend/tests/contracts.test.ts`:
```ts
import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { SCHEMAS, type SchemaName } from '../lib/contracts';
import { parseEnvelope, validate, validateEnvelope, validateEvent, validateProblem } from '../lib/validate';

const EXAMPLES_DIR = fileURLToPath(new URL('../../contracts/examples/', import.meta.url));
const examples = readdirSync(EXAMPLES_DIR)
  .filter((f) => f.endsWith('.example.json'))
  .sort()
  .map(
    (f) => [f.replace(/\.example\.json$/, ''), JSON.parse(readFileSync(EXAMPLES_DIR + f, 'utf-8'))] as const,
  );
const example = (name: string) => structuredClone(examples.find(([n]) => n === name)![1]);

describe('contract registry', () => {
  it('lists every contract', () => {
    expect(SCHEMAS.map((s) => s.name).sort()).toEqual(['common', 'envelope', 'event', 'problem']);
  });

  it('has an example for each top-level contract', () => {
    expect(examples.map(([n]) => n)).toEqual(['envelope', 'event', 'problem']);
  });
});

describe.each(examples)('%s example', (name, data) => {
  it('validates against its schema', () => {
    expect(validate(name as SchemaName, data)).toBe(true);
  });
});

describe('envelope contract', () => {
  it('accepts the spec example via the named validator', () => {
    expect(validateEnvelope(example('envelope'))).toBe(true);
  });

  it('rejects an unknown audience', () => {
    expect(validateEnvelope({ ...example('envelope'), audience: 'everyone' })).toBe(false);
  });

  it('rejects an unknown card type', () => {
    expect(validateEnvelope({ ...example('envelope'), cards: [{ type: 'banner' }] })).toBe(false);
  });

  it('rejects hi-Latn as a speech locale (resolved through common.schema.json)', () => {
    expect(validateEnvelope({ ...example('envelope'), lang: { screen: 'hi-Latn', speech: 'hi-Latn' } })).toBe(
      false,
    );
  });

  it('rejects a bad undo date-time (formats are on)', () => {
    const bad = example('envelope');
    bad.undo.until = 'yesterday';
    expect(validateEnvelope(bad)).toBe(false);
  });

  it('parseEnvelope returns the typed envelope or throws with the errors', () => {
    expect(parseEnvelope(example('envelope')).turn_id).toMatch(/^turn_/);
    expect(() => parseEnvelope({ ...example('envelope'), presence: { state: 'dancing' } })).toThrow(
      /invalid envelope: .*presence\/state/,
    );
  });
});

describe('event and problem contracts', () => {
  it('rejects an event type without a dot', () => {
    expect(validateEvent({ ...example('event'), type: 'ticked' })).toBe(false);
  });

  it('accepts a root event with a null causation_id', () => {
    expect(validateEvent({ ...example('event'), causation_id: null })).toBe(true);
  });

  it('rejects a problem with a 2xx status', () => {
    expect(validateProblem({ ...example('problem'), status: 200 })).toBe(false);
  });

  it('throws for an unknown contract name', () => {
    expect(() => validate('nope' as SchemaName, {})).toThrow(/no contract named "nope"/);
  });
});
```

- [ ] **Step 5: Generate and run the tests**

Run: `python dev.py gen`
Expected: `generated arth/contracts/envelope.py` (and event.py, problem.py); `contracts: wrote 3 type files …`; `openapi-typescript` writes `lib/contracts/api.ts`. (`gen` also calls the `tokens` script, which doesn't exist until Task 12. Until then, run the first two commands of `gen()` by hand: `cd backend && uv run python -m arth.tools.gen_contracts`, then `pnpm --filter frontend run gen`.)

Run: `cd backend && uv run pytest tests/test_contract_roundtrip.py -q`
Expected: `2 passed`.

Run: `pnpm --filter frontend run test`
Expected: `contracts.test.ts` 3 passed, `smoke.test.ts` 1 passed.

If the round-trip test fails because a generated field dumps differently (e.g. a datetime with `+00:00` instead of `Z`), change the **example**, not the generated code: use the dumped form. The contract is the schema; the example only illustrates it.

- [ ] **Step 6: Checkpoint**

Run: `python dev.py test`
Expected: all green.


**Post-review additions (contracts, Tasks 2–3).** After code review the contracts layer gained: `contracts/common.schema.json` (shared `Locale`, `SpeechLocale`, `Audience`, `Tier`, `Ulid`, `PrefixedId`, `DottedCode`, `MessageKey`, `NonEmptyString`); `anyOf` nullables; `contracts/examples/{event,problem}.example.json`; `contracts/README.md` (rules + the per-card/per-topic extension pattern); `backend/arth/core/schemas.py` (schema discovery by `*.schema.json`, a `referencing` registry, validators); generator discovery on both sides (`backend/arth/tools/gen_contracts.py`, `frontend/scripts/gen-contracts.mjs`, which also emits `frontend/lib/contracts/index.ts`); a `--check` mode wired into `python dev.py gen-check` and run first by `python dev.py check`; Ajv `strict: true` with all schemas added up front (`frontend/lib/validate.ts`: `validate(name, data)`, `parseEnvelope`, `validateProblem`); tests parametrised over `contracts/examples/*` with canonical-JSON round-trips (integers must stay integers), negative schema cases, an OpenAPI ref/operationId test (`backend/tests/test_gen_contracts.py`, `test_contract_schemas.py`, `test_contract_roundtrip.py`). Code blocks above reflect the files on disk.

---

### Task 4: IDs, money and quantities (T0.5)

**Files:**
- Create: `backend/arth/core/ids.py`, `backend/arth/core/money.py`, `backend/arth/core/qty.py`
- Test: `backend/tests/test_ids.py`, `backend/tests/test_money_qty.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_ids.py`:
```python
import pytest

from arth.core.ids import IdError, kind_of, new_id, parse_id


def test_new_id_has_kind_prefix_and_ulid() -> None:
    value = new_id("bill")
    kind, ulid = parse_id(value)
    assert kind == "bill"
    assert len(ulid) == 26
    assert kind_of(value) == "bill"


def test_ids_are_unique() -> None:
    assert len({new_id("pat") for _ in range(1000)}) == 1000


@pytest.mark.parametrize("kind", ["", "B", "bill-x", "x", "averyverylongkind", "bill\n"])
def test_rejects_bad_kind(kind: str) -> None:
    with pytest.raises(IdError):
        new_id(kind)


@pytest.mark.parametrize(
    "value",
    [
        "bill",
        "bill_123",
        "Bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1",
        "bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9TU",
        "bill\n_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1",
        "bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1\n",
        "bill_81JBQ0Z7Y8K3M4N5P6Q7R8S9T1",
    ],
)
def test_rejects_bad_id(value: str) -> None:
    with pytest.raises(IdError):
        parse_id(value)
    with pytest.raises(IdError):
        kind_of(value)


def test_first_ulid_char_up_to_7_is_accepted() -> None:
    assert parse_id("bill_71JBQ0Z7Y8K3M4N5P6Q7R8S9T1")[0] == "bill"


def test_ids_generated_in_a_loop_have_non_decreasing_timestamps() -> None:
    # Millisecond-level monotonicity only: within one ms the random part is unordered.
    stamps = [new_id("pat").split("_")[1][:10] for _ in range(2000)]
    assert stamps == sorted(stamps)
```

`backend/tests/test_money_qty.py`:
```python
from decimal import Decimal, Inexact, Rounded, localcontext
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from arth.core.money import MoneyError, div_round_half_even, to_paise
from arth.core.qty import QtyError, line_amount, to_milli

BIG = 10**40


def _ref_half_even(n: int, d: int) -> int:
    return round(Fraction(n, d))  # Fraction.__round__ rounds half-to-even


def test_to_paise_exact() -> None:
    assert to_paise("62") == 6200
    assert to_paise("62.5") == 6250
    assert to_paise(Decimal("0.01")) == 1
    assert to_paise(1600) == 160000


def test_to_paise_negative() -> None:
    assert to_paise("-62.5") == -6250
    assert to_paise(-3) == -300
    assert to_paise("-0") == 0


def test_to_paise_rejects_sub_paise() -> None:
    with pytest.raises(MoneyError):
        to_paise("1.005")


def test_half_even_rounding() -> None:
    assert div_round_half_even(5, 2) == 2
    assert div_round_half_even(7, 2) == 4
    assert div_round_half_even(-5, 2) == -2


def test_div_round_half_even_ties_and_signs() -> None:
    assert div_round_half_even(1, 2) == 0
    assert div_round_half_even(3, 2) == 2
    assert div_round_half_even(-3, 2) == -2
    assert div_round_half_even(5, -2) == -2
    assert div_round_half_even(-5, -2) == 2
    assert div_round_half_even(10**40 + 1, 2) == 5 * 10**39  # beyond default Decimal precision


def test_div_round_half_even_zero_denominator() -> None:
    with pytest.raises(ZeroDivisionError):
        div_round_half_even(1, 0)


@given(st.integers(-BIG, BIG), st.integers(-BIG, BIG).filter(lambda d: d != 0))
def test_div_round_half_even_matches_fraction_reference(n: int, d: int) -> None:
    assert div_round_half_even(n, d) == _ref_half_even(n, d)


@given(st.integers(-BIG, BIG), st.integers(1, 10**20))
def test_div_round_half_even_exact_ties(k: int, d: int) -> None:
    # (2k+1)*d / (2d) is exactly k + 1/2
    assert div_round_half_even((2 * k + 1) * d, 2 * d) == _ref_half_even((2 * k + 1) * d, 2 * d)


def test_sugar_half_kilo_at_48_per_kg_is_24_rupees() -> None:
    # Billing screen: "Sugar, loose 0.5 kg · ₹24" at ₹48/kg
    assert line_amount(unit_price_paise=4800, qty_milli=to_milli("0.5")) == 2400


def test_line_amount_half_even_ties() -> None:
    assert line_amount(1, 500) == 0
    assert line_amount(1, 1500) == 2
    assert line_amount(1, 2500) == 2
    assert line_amount(-1, 1500) == -2


def test_to_milli_exact_and_negative() -> None:
    assert to_milli("0.5") == 500
    assert to_milli("-1.250") == -1250
    assert to_milli(3) == 3000
    assert to_milli(Decimal("0.001")) == 1
    assert to_milli("-0") == 0


def test_to_milli_rejects_more_than_three_decimals() -> None:
    with pytest.raises(QtyError):
        to_milli("0.0005")


@given(st.integers(0, 10_000_000))
def test_one_unit_costs_unit_price(price: int) -> None:
    assert line_amount(price, 1000) == price


@given(st.integers(0, 1_000_000), st.integers(0, 100_000))
def test_line_amount_is_monotonic_in_quantity(price: int, qty: int) -> None:
    assert line_amount(price, qty + 1) >= line_amount(price, qty)


@given(st.integers(-(10**12), 10**12))
def test_paise_round_trip_through_rupee_string(paise: int) -> None:
    rupees = Decimal(paise) / 100
    assert to_paise(str(rupees)) == paise


@given(st.integers(-BIG, BIG))
def test_paise_round_trip_large(paise: int) -> None:
    sign = "-" if paise < 0 else ""
    whole, frac = divmod(abs(paise), 100)
    assert to_paise(f"{sign}{whole}.{frac:02d}") == paise


@given(st.integers(-BIG, BIG))
def test_milli_round_trip_large(milli: int) -> None:
    sign = "-" if milli < 0 else ""
    whole, frac = divmod(abs(milli), 1000)
    assert to_milli(f"{sign}{whole}.{frac:03d}") == milli


@given(st.integers(-(10**30), 10**30), st.integers(-(10**30), 10**30))
def test_line_amount_large_ints_match_reference(price: int, qty: int) -> None:
    assert line_amount(price, qty) == _ref_half_even(price * qty, 1000)


@pytest.mark.parametrize("bad", [1.5, 0.0, True, False, float("nan"), float("inf")])
def test_float_and_bool_rejected(bad: object) -> None:
    with pytest.raises(MoneyError):
        to_paise(bad)  # type: ignore[arg-type]
    with pytest.raises(QtyError):
        to_milli(bad)  # type: ignore[arg-type]


def test_float_message() -> None:
    with pytest.raises(MoneyError, match="pass str, int or Decimal, not float"):
        to_paise(1.5)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "bad",
    [
        "1e2",
        "1E2",
        "inf",
        "-inf",
        "Infinity",
        "nan",
        "NaN",
        "sNaN",
        "",
        " 1",
        "1 ",
        "+1",
        ".5",
        "1.",
        "1_0",
        "--1",
        "1\n",
        "١٢",
    ],
)
def test_non_plain_strings_rejected(bad: str) -> None:
    with pytest.raises(MoneyError):
        to_paise(bad)
    with pytest.raises(QtyError):
        to_milli(bad)


@pytest.mark.parametrize("bad", [Decimal("Infinity"), Decimal("-Infinity"), Decimal("NaN"), Decimal("sNaN")])
def test_non_finite_decimals_rejected(bad: Decimal) -> None:
    with pytest.raises(MoneyError):
        to_paise(bad)
    with pytest.raises(QtyError):
        to_milli(bad)


def test_other_types_rejected() -> None:
    with pytest.raises(MoneyError):
        to_paise(None)  # type: ignore[arg-type]


def test_parsing_ignores_ambient_decimal_context() -> None:
    with localcontext() as ctx:
        ctx.prec = 3
        ctx.traps[Inexact] = True
        ctx.traps[Rounded] = True
        assert to_paise("123456789012345678901234567890.12") == 12345678901234567890123456789012
        assert to_paise(Decimal("1.50")) == 150
        with pytest.raises(MoneyError):
            to_paise("1.005")
        assert to_milli("123456789012345678901234567890.123") == 123456789012345678901234567890123


def test_decimal_objects_with_exponent() -> None:
    assert to_paise(Decimal("1E+2")) == 10000
    assert to_paise(Decimal("1E-2")) == 1
    with pytest.raises(MoneyError):
        to_paise(Decimal("1E-3"))
    with pytest.raises(MoneyError):
        to_paise(Decimal("1E+99999999"))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_ids.py tests/test_money_qty.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.core.ids'`.

- [ ] **Step 3: Implement**

`backend/arth/core/ids.py`:
```python
"""Prefixed ULIDs: `bill_01JBQ…`. The prefix makes logs readable; the ULID sorts by creation time.

Ordering is millisecond-level: IDs created in different milliseconds sort chronologically,
but IDs created within the same millisecond have a random (unordered) suffix.
"""

from __future__ import annotations

import re

from ulid import ULID

_KIND_PATTERN = r"[a-z][a-z0-9]{1,9}"
# 26 Crockford base32 chars = 130 bits; a 128-bit ULID's first char is therefore 0-7.
_ULID_PATTERN = r"[0-7][0-9A-HJKMNP-TV-Z]{25}"
_KIND = re.compile(_KIND_PATTERN)
_ID = re.compile(rf"({_KIND_PATTERN})_({_ULID_PATTERN})")


class IdError(ValueError):
    """An ID or ID kind is malformed."""


def new_id(kind: str) -> str:
    """Return a fresh ID `<kind>_<ULID>`.

    `kind` must be 2-10 chars of lowercase letters/digits starting with a letter.
    Raises IdError otherwise (including trailing newlines). Sorting is ms-level monotonic.
    """
    if not _KIND.fullmatch(kind):
        raise IdError(f"bad id kind {kind!r}: use 2–10 lowercase letters/digits starting with a letter")
    return f"{kind}_{ULID()}"


def parse_id(value: str) -> tuple[str, str]:
    """Split an ID into `(kind, ulid)`. Raises IdError unless it is exactly `<kind>_<26-char ULID>`."""
    match = _ID.fullmatch(value)
    if not match:
        raise IdError(f"bad id {value!r}")
    return match.group(1), match.group(2)


def kind_of(value: str) -> str:
    """Return the kind prefix of a valid ID. Raises IdError if the ID is malformed."""
    return parse_id(value)[0]
```

`backend/arth/core/money.py`:
```python
"""Money is integer paise everywhere. Formatting lives in arth.core.i18n."""

from __future__ import annotations

import re
from decimal import Decimal

_PLAIN_DECIMAL = re.compile(r"-?[0-9]+(\.[0-9]+)?")
_MAX_EXPONENT = 1000  # refuse absurd Decimal exponents instead of building gigantic ints


class MoneyError(ValueError):
    """A money value cannot be represented exactly in paise."""


def scale_exact(value: object, places: int, error: type[ValueError]) -> int:
    """Return `value * 10**places` as an int, or raise `error` if it is not exactly an integer.

    Pure integer arithmetic on the Decimal's digit tuple, so the result never depends on the
    ambient decimal context (precision, traps, rounding).
    Accepts: plain decimal strings (`-?[0-9]+(\\.[0-9]+)?`), ints, finite Decimals.
    Rejects: float, bool, other types, exponent/whitespace/`+`/inf/nan strings, non-finite Decimals.
    """
    if isinstance(value, float):
        raise error("pass str, int or Decimal, not float")
    if isinstance(value, bool):
        raise error("pass str, int or Decimal, not bool")
    try:
        if isinstance(value, str):
            if not _PLAIN_DECIMAL.fullmatch(value):
                raise error(f"not a plain decimal number: {value!r}")
            dec = Decimal(value)
        elif isinstance(value, int):
            dec = Decimal(value)
        elif isinstance(value, Decimal):
            dec = value
        else:
            raise error(f"pass str, int or Decimal, not {type(value).__name__}")
        if not dec.is_finite():
            raise error(f"not a finite number: {value!r}")
        sign, digits, exponent = dec.as_tuple()
        assert isinstance(exponent, int)
        if abs(exponent) > _MAX_EXPONENT:
            raise error(f"exponent too large: {value!r}")
        magnitude = int("".join(map(str, digits)) or "0")
        shift = exponent + places
        if shift >= 0:
            result = magnitude * 10**shift
        else:
            result, remainder = divmod(magnitude, 10**-shift)
            if remainder:
                raise error(f"{value!r} has more than {places} decimal places")
        return -result if sign else result
    except ArithmeticError as exc:
        raise error(f"not a number: {value!r}") from exc


def to_paise(rupees: str | int | Decimal) -> int:
    """Convert rupees to integer paise, exactly.

    Accepts a plain decimal string like "62" or "-62.50" (no exponent, `+` sign, spaces,
    underscores, "inf"/"nan"), an int, or a finite Decimal. Raises MoneyError for float/bool
    (pass a str instead), non-finite or malformed input, and values with more than 2 decimal places.
    """
    return scale_exact(rupees, 2, MoneyError)


def div_round_half_even(numerator: int, denominator: int) -> int:
    """Integer division rounded half-to-even (banker's rounding), used for tax and pro-rata lines.

    Pure integer arithmetic, exact for arbitrarily large ints. Raises ZeroDivisionError on 0.
    """
    if denominator == 0:
        raise ZeroDivisionError("denominator is zero")
    negative = (numerator < 0) != (denominator < 0)
    divisor = abs(denominator)
    quotient, remainder = divmod(abs(numerator), divisor)
    twice = 2 * remainder
    if twice > divisor or (twice == divisor and quotient % 2 == 1):
        quotient += 1
    return -quotient if negative else quotient
```

`backend/arth/core/qty.py`:
```python
"""Quantities are integer milli-units (0.5 kg = 500)."""

from __future__ import annotations

from decimal import Decimal

from arth.core.money import div_round_half_even, scale_exact

MILLI = 1000


class QtyError(ValueError):
    """A quantity cannot be represented exactly in milli-units."""


def to_milli(qty: str | int | Decimal) -> int:
    """Convert a quantity in units to integer milli-units, exactly.

    Accepts a plain decimal string like "0.5" or "-1.250" (no exponent, `+` sign, spaces,
    "inf"/"nan"), an int, or a finite Decimal. Raises QtyError for float/bool, non-finite or
    malformed input, and values with more than 3 decimal places.
    """
    return scale_exact(qty, 3, QtyError)


def line_amount(unit_price_paise: int, qty_milli: int) -> int:
    """Price of `qty_milli` units at `unit_price_paise` per unit, rounded half-even to the paisa."""
    return div_round_half_even(unit_price_paise * qty_milli, MILLI)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_ids.py tests/test_money_qty.py -q`
Expected: all pass (hypothesis runs 100 examples per property).

- [ ] **Step 5: Checkpoint**

Run: `python dev.py lint test`
Expected: all green.

---

### Task 5: Sim Clock (T0.4, part 1)

**Files:**
- Create: `backend/arth/core/clock.py`
- Test: `backend/tests/test_clock.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_clock.py`:
```python
import ast
import math
from datetime import datetime, timedelta

import pytest

from arth.core.clock import IST, UTC, ClockError, SimClock, iso_utc, next_daily, parse_iso
from arth.core.paths import BACKEND_DIR

START = datetime(2026, 10, 29, 7, 45, tzinfo=IST)
NAIVE = datetime(2026, 10, 29, 7, 45)  # noqa: DTZ001


class FakeMonotonic:
    """A hand-driven stand-in for time.monotonic, so clock tests never sleep."""

    def __init__(self) -> None:
        self.value = 1000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


@pytest.fixture
def mono() -> FakeMonotonic:
    return FakeMonotonic()


def test_frozen_clock_does_not_move(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    mono.advance(3600)
    assert clock.now() == START.astimezone(UTC)
    assert clock.running is False


def test_now_is_utc_aware_and_ist_view_matches() -> None:
    clock = SimClock(START)
    assert clock.now().tzinfo is UTC
    assert clock.now_ist().hour == 7 and clock.now_ist().minute == 45


def test_set_forward_and_refuse_backwards() -> None:
    clock = SimClock(START)
    clock.set(START + timedelta(hours=2))
    assert clock.now_ist().hour == 9
    with pytest.raises(ClockError):
        clock.set(START)


def test_set_backwards_message_names_both_times() -> None:
    clock = SimClock(START + timedelta(hours=2))
    with pytest.raises(ClockError) as info:
        clock.set(START)
    message = str(info.value)
    assert START.astimezone(UTC).isoformat() in message
    assert (START + timedelta(hours=2)).astimezone(UTC).isoformat() in message


def test_set_to_exactly_now_is_allowed(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.set(clock.now())
    assert clock.now() == START.astimezone(UTC)
    clock.run(rate=60.0)
    mono.advance(1)
    clock.set(clock.now())
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=60)


def test_reset_may_go_backwards_for_snapshot_restore() -> None:
    clock = SimClock(START + timedelta(days=1))
    clock.reset(START)
    assert clock.now() == START.astimezone(UTC)


def test_reset_while_running_continues_at_same_rate(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=60.0)
    mono.advance(1)
    target = START - timedelta(days=3)
    clock.reset(target)
    assert clock.now() == target.astimezone(UTC)
    mono.advance(2)
    assert clock.now() == target.astimezone(UTC) + timedelta(seconds=120)
    assert clock.running is True
    assert clock.rate == 60.0


def test_running_clock_advances_at_rate(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=3600.0)  # one real second = one sim hour
    mono.advance(0.5)
    assert clock.now() == START.astimezone(UTC) + timedelta(minutes=30)
    clock.freeze()
    frozen = clock.now()
    mono.advance(10)
    assert clock.now() == frozen == START.astimezone(UTC) + timedelta(minutes=30)
    assert clock.running is False


def test_rate_continuity_across_run_freeze_run(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=10.0)
    mono.advance(1)
    clock.freeze()
    mono.advance(5)
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=10)
    clock.run(rate=10.0)
    mono.advance(1)
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=20)


def test_multi_day_running_jump(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=86400.0)  # one real second = one sim day
    mono.advance(8)
    assert clock.now() == START.astimezone(UTC) + timedelta(days=8)


def test_rate_property_defaults_and_follows_run(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    assert clock.rate == 1.0
    clock.run(rate=5.0)
    assert clock.rate == 5.0


@pytest.mark.parametrize("bad", [0, -1, -0.5, math.nan, math.inf, -math.inf])
def test_constructor_rejects_bad_rate(bad: float) -> None:
    with pytest.raises(ClockError, match="rate must be a positive finite number"):
        SimClock(START, rate=bad)


@pytest.mark.parametrize("bad", [0, -1, -0.5, math.nan, math.inf, -math.inf])
def test_run_rejects_bad_rate_and_leaves_state_unchanged(bad: float, mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    clock.run(rate=10.0)
    mono.advance(1)
    with pytest.raises(ClockError, match="rate must be a positive finite number"):
        clock.run(rate=bad)
    assert clock.running is True
    assert clock.rate == 10.0
    mono.advance(1)
    assert clock.now() == START.astimezone(UTC) + timedelta(seconds=20)


def test_rejected_run_leaves_frozen_clock_frozen(mono: FakeMonotonic) -> None:
    clock = SimClock(START, monotonic=mono)
    with pytest.raises(ClockError):
        clock.run(rate=0)
    assert clock.running is False
    mono.advance(100)
    assert clock.now() == START.astimezone(UTC)


def test_rejects_naive_datetimes() -> None:
    with pytest.raises(ClockError):
        SimClock(NAIVE)


def test_set_and_reset_reject_naive_datetimes() -> None:
    clock = SimClock(START)
    with pytest.raises(ClockError):
        clock.set(NAIVE)
    with pytest.raises(ClockError):
        clock.reset(NAIVE)


def test_iso_round_trip_and_fixed_width() -> None:
    value = iso_utc(START)
    assert value == "2026-10-29T02:15:00.000000Z"
    assert parse_iso(value) == START


def test_parse_iso_rejects_naive_strings() -> None:
    with pytest.raises(ClockError):
        parse_iso("2026-10-29T02:15:00")


def test_next_daily_is_strictly_after() -> None:
    at_2200 = next_daily(START, "22:00")
    assert at_2200.astimezone(IST) == datetime(2026, 10, 29, 22, 0, tzinfo=IST)
    assert next_daily(at_2200, "22:00").astimezone(IST) == datetime(2026, 10, 30, 22, 0, tzinfo=IST)


def test_next_daily_from_exact_boundary_goes_to_next_day() -> None:
    boundary = datetime(2026, 10, 29, 8, 0, tzinfo=IST)
    assert next_daily(boundary, "08:00").astimezone(IST) == datetime(2026, 10, 30, 8, 0, tzinfo=IST)


@pytest.mark.parametrize("bad", ["8", "25:00", "08:00:00", "ab", "08:60", "8:00", ""])
def test_next_daily_rejects_bad_time(bad: str) -> None:
    with pytest.raises(ClockError, match="expected HH:MM"):
        next_daily(START, bad)


# --- wall-clock ban (AST based, so comments and docstrings never trigger it) ---

_BANNED_CALLS = (
    ("datetime", "now"),
    ("datetime", "utcnow"),
    ("date", "today"),
    ("time", "time"),
    ("time", "time_ns"),
)


def _attribute_chain(node: ast.expr) -> tuple[str, ...]:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return tuple(reversed(parts))


def wall_clock_violations(source: str) -> list[str]:
    """Describe every wall-clock read in `source` (empty list when clean)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            chain = _attribute_chain(node.func)
            if any(chain[-2:] == banned for banned in _BANNED_CALLS):
                found.append(f"line {node.lineno}: {'.'.join(chain)}()")
        elif isinstance(node, ast.ImportFrom) and node.module == "time":
            found.extend(
                f"line {node.lineno}: from time import {alias.name}"
                for alias in node.names
                if alias.name in {"time", "time_ns"}
            )
    return found


def test_wall_clock_scanner_flags_violations_only() -> None:
    dirty = (
        "import time\n"
        "from datetime import datetime\n"
        "from time import time_ns\n"
        "a = datetime.now()\n"
        "b = time.time()\n"
    )
    assert len(wall_clock_violations(dirty)) == 3
    clean = (
        '"""Mentions datetime.now() and time.time() in a docstring only."""\n'
        "# datetime.utcnow() in a comment\n"
        "import time\n"
        "x = time.monotonic()\n"
        "y = clock.now()\n"
    )
    assert wall_clock_violations(clean) == []


def test_no_wall_clock_outside_clock_module() -> None:
    clock_module = (BACKEND_DIR / "arth" / "core" / "clock.py").resolve()
    offenders = {
        str(path.relative_to(BACKEND_DIR)): hits
        for path in (BACKEND_DIR / "arth").rglob("*.py")
        if path.resolve() != clock_module
        and (hits := wall_clock_violations(path.read_text(encoding="utf-8")))
    }
    assert offenders == {}, f"use SimClock instead of the wall clock in: {offenders}"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_clock.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.core.clock'`.

- [ ] **Step 3: Implement**

`backend/arth/core/clock.py`:
```python
"""The Sim Clock: the only source of "now" in Arth (spec v5.1 D6).

Stored times are UTC; the shop sees IST. A frozen clock never moves; a running clock advances at
`rate` x real time. `set` only moves forward; `reset` (used by snapshot restore) may go back.
"""

from __future__ import annotations

import math
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
__all__ = ["IST", "UTC", "ClockError", "SimClock", "iso_utc", "parse_iso", "next_daily"]

_HH_MM = re.compile(r"([01][0-9]|2[0-3]):([0-5][0-9])")


class ClockError(ValueError):
    """Invalid clock input: naive datetime, backwards `set`, bad `rate`, or malformed "HH:MM"."""


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ClockError("datetimes must be timezone-aware")


def _require_rate(rate: float) -> None:
    valid = isinstance(rate, int | float) and not isinstance(rate, bool) and math.isfinite(rate) and rate > 0
    if not valid:
        raise ClockError("rate must be a positive finite number")


def iso_utc(value: datetime) -> str:
    """Fixed-width UTC ISO string; sorts lexically in time order (used in SQLite columns)."""
    _require_aware(value)
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    _require_aware(parsed)
    return parsed.astimezone(UTC)


def next_daily(after: datetime, at_ist: str) -> datetime:
    """The first moment strictly after `after` whose IST wall time is `at_ist` ("HH:MM")."""
    _require_aware(after)
    match = _HH_MM.fullmatch(at_ist)
    if match is None:
        raise ClockError(f"bad time {at_ist!r}; expected HH:MM")
    hour, minute = int(match.group(1)), int(match.group(2))
    local = after.astimezone(IST)
    candidate = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= local:
        candidate += timedelta(days=1)
    return candidate.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class _State:
    anchor_sim: datetime
    anchor_real: float
    running: bool
    rate: float


class SimClock:
    """The simulated clock.

    Safe to read (`now`, `now_ist`, `running`, `rate`) from any thread: all state lives in one
    immutable snapshot that is swapped in a single assignment. Mutate (`set`, `reset`, `freeze`,
    `run`) only from the event-loop thread.
    """

    def __init__(
        self,
        start: datetime,
        *,
        running: bool = False,
        rate: float = 1.0,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        _require_aware(start)
        _require_rate(rate)
        self._monotonic = monotonic
        self._state = _State(start.astimezone(UTC), monotonic(), running, rate)

    @property
    def running(self) -> bool:
        return self._state.running

    @property
    def rate(self) -> float:
        return self._state.rate

    def now(self) -> datetime:
        return self._at(self._state, self._monotonic())

    def now_ist(self) -> datetime:
        return self.now().astimezone(IST)

    def set(self, value: datetime) -> None:
        _require_aware(value)
        current = self.now()
        if value < current:
            raise ClockError(
                "sim time cannot go backwards; restore a snapshot instead "
                f"(requested {value.astimezone(UTC).isoformat()}, "
                f"current {current.isoformat()})"
            )
        self._rebase(value, self._state.running, self._state.rate)

    def reset(self, value: datetime) -> None:
        """Move to any time. Only snapshot restore may call this."""
        _require_aware(value)
        self._rebase(value, self._state.running, self._state.rate)

    def freeze(self) -> None:
        self._rebase(self.now(), False, self._state.rate)

    def run(self, rate: float = 1.0) -> None:
        _require_rate(rate)
        self._rebase(self.now(), True, rate)

    @staticmethod
    def _at(state: _State, real: float) -> datetime:
        if not state.running:
            return state.anchor_sim
        return state.anchor_sim + timedelta(seconds=(real - state.anchor_real) * state.rate)

    def _rebase(self, value: datetime, running: bool, rate: float) -> None:
        self._state = _State(value.astimezone(UTC), self._monotonic(), running, rate)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_clock.py -q`
Expected: `39 passed`.

- [ ] **Step 5: Checkpoint**

Run: `python dev.py lint test`
Expected: all green.

---

### Task 6: Database, migrations and snapshots (T0.6)

**Files:**
- Create: `backend/arth/core/db.py`, `backend/arth/core/tables.py`, `backend/arth/core/migrate.py`, `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/script.py.mako`, `backend/migrations/versions/0001_l0_foundations.py`, `backend/tests/conftest.py`
- Test: `backend/tests/test_db.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/conftest.py`:
```python
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from arth.core.db import Database
from arth.core.migrate import upgrade


@pytest.fixture
async def db(tmp_path: Path) -> AsyncIterator[Database]:
    path = tmp_path / "arth.db"
    upgrade(path)
    database = Database(path)
    await database.open()
    yield database
    await database.close()
```

`backend/tests/test_db.py`:
```python
import asyncio
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import func, insert, select, text

from arth.core.db import Database
from arth.core.tables import jobs


def job_row(job_id: str) -> dict:
    return {"id": job_id, "name": "t", "due_at": "2026-10-29T16:30:00.000000Z", "payload": "{}"}


async def test_pragmas_are_applied(db: Database) -> None:
    async with db.read() as conn:
        assert (await conn.execute(text("PRAGMA journal_mode"))).scalar() == "wal"
        assert (await conn.execute(text("PRAGMA foreign_keys"))).scalar() == 1
        assert (await conn.execute(text("PRAGMA synchronous"))).scalar() == 1
        assert (await conn.execute(text("PRAGMA busy_timeout"))).scalar() == 5000


async def test_migration_creates_l0_tables(db: Database) -> None:
    async with db.read() as conn:
        names = {
            row[0] for row in await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        }
    assert {"jobs", "spans", "alembic_version"} <= names


async def test_write_then_read(db: Database) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    async with db.read() as conn:
        assert (await conn.execute(select(func.count()).select_from(jobs))).scalar() == 1


async def test_snapshot_and_restore_round_trip(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "snapshots" / "scene-1.db"
    await db.snapshot(snap)
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))
    await db.restore(snap)
    async with db.read() as conn:
        assert (await conn.execute(select(func.count()).select_from(jobs))).scalar() == 1


async def count_jobs(db: Database) -> int:
    async with db.read() as conn:
        return (await conn.execute(select(func.count()).select_from(jobs))).scalar_one()


async def test_write_rolls_back_on_exception(db: Database) -> None:
    with pytest.raises(RuntimeError):
        async with db.write() as conn:
            await conn.execute(insert(jobs).values(**job_row("job_1")))
            raise RuntimeError("boom")
    assert await count_jobs(db) == 0


async def test_snapshot_includes_data_still_in_wal(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "wal.db"
    await db.snapshot(snap)
    check = sqlite3.connect(snap)
    try:
        assert check.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
    finally:
        check.close()


async def test_restore_waits_for_in_flight_reader(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "s.db"
    await db.snapshot(snap)
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))

    restore_task: asyncio.Task[None]
    async with db.read() as conn:
        assert (await conn.execute(select(func.count()).select_from(jobs))).scalar() == 2
        restore_task = asyncio.create_task(db.restore(snap))
        await asyncio.sleep(0.2)
        assert not restore_task.done()  # blocked on our open reader
        late_reader = asyncio.create_task(count_jobs(db))
        await asyncio.sleep(0.1)
        assert not late_reader.done()  # new readers are gated during restore
    await restore_task
    assert await late_reader == 1


async def test_restore_then_write_works_and_matches_snapshot(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "s.db"
    await db.snapshot(snap)
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))
    await db.restore(snap)
    async with db.read() as conn:
        ids = {r[0] for r in await conn.execute(select(jobs.c.id))}
        assert ids == {"job_1"}
        assert (await conn.execute(text("PRAGMA journal_mode"))).scalar() == "wal"
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_3")))
    assert await count_jobs(db) == 2


async def test_restore_times_out_with_stuck_reader(
    db: Database, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import arth.core.db as db_mod

    monkeypatch.setattr(db_mod, "RESTORE_READER_TIMEOUT", 0.2)
    snap = tmp_path / "s.db"
    await db.snapshot(snap)
    async with db.read():
        with pytest.raises(RuntimeError, match="reader"):
            await db.restore(snap)
    assert await count_jobs(db) == 0  # gate released; reads work again


async def test_restore_missing_file_leaves_db_untouched(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    with pytest.raises(FileNotFoundError, match="nope.db"):
        await db.restore(tmp_path / "nope.db")
    assert await count_jobs(db) == 1


async def test_restore_bad_file_leaves_db_untouched(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    bad = tmp_path / "bad.db"
    bad.write_bytes(b"this is not a sqlite database" * 100)
    with pytest.raises(RuntimeError, match="live database unchanged"):
        await db.restore(bad)
    assert await count_jobs(db) == 1
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))
    assert await count_jobs(db) == 2
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_db.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.core.db'`.

- [ ] **Step 3: Implement the database module and tables**

`backend/arth/core/db.py`:
```python
"""SQLite access: WAL, one writer at a time, many readers, snapshot and restore (spec v5.1 D2)."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

RESTORE_READER_TIMEOUT = 5.0

# busy_timeout first so the remaining pragmas (journal_mode needs a lock) already wait on contention.
PRAGMAS = (
    "PRAGMA busy_timeout=5000",
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA foreign_keys=ON",
)


def _apply_pragmas(dbapi_connection: Any, _record: Any) -> None:
    cursor = dbapi_connection.cursor()
    for pragma in PRAGMAS:
        cursor.execute(pragma)
    cursor.close()


def _vacuum_into(src: Path, dest: Path) -> None:
    conn = sqlite3.connect(src)
    try:
        escaped = dest.as_posix().replace("'", "''")
        conn.execute(f"VACUUM INTO '{escaped}'")
    finally:
        conn.close()


def _backup_into(src: Path, dest: Path) -> None:
    """Copy src over dest in place with SQLite's online backup API (transactional: all or nothing)."""
    src_conn = sqlite3.connect(f"{src.resolve().as_uri()}?mode=ro", uri=True)
    try:
        src_conn.execute("SELECT count(*) FROM sqlite_master").fetchone()  # raises if not a SQLite DB
        dest_conn = sqlite3.connect(dest, timeout=5.0)
        try:
            src_conn.backup(dest_conn)
        finally:
            dest_conn.close()
    finally:
        src_conn.close()


class Database:
    """Async SQLite wrapper: one writer at a time, many readers, snapshot and in-place restore.

    The write lock and reader gate are per-process (per event loop) asyncio primitives. Contention
    from another process is not coordinated here; it relies on SQLite's busy_timeout.

    Rules: always go through `read()`/`write()` (using `engine.connect()` directly bypasses the
    restore gate); don't nest `read()` inside `read()` (a restore starting in between waits for the
    outer reader and aborts after the timeout); never call `restore()`/`snapshot()` inside `write()`
    (the write lock is not reentrant).
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._engine: AsyncEngine | None = None
        self._write_lock = asyncio.Lock()
        self._gate = asyncio.Condition()
        self._readers = 0
        self._restoring = False

    async def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_async_engine(f"sqlite+aiosqlite:///{self.path.as_posix()}")
        event.listen(engine.sync_engine, "connect", _apply_pragmas)
        self._engine = engine

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Database.open() has not been called")
        return self._engine

    @asynccontextmanager
    async def read(self) -> AsyncIterator[AsyncConnection]:
        """Reader connection; waits while a restore is in progress and is counted so restore can drain."""
        async with self._gate:
            await self._gate.wait_for(lambda: not self._restoring)
            self._readers += 1
        try:
            async with self.engine.connect() as conn:
                yield conn
        finally:
            async with self._gate:
                self._readers -= 1
                self._gate.notify_all()

    @asynccontextmanager
    async def write(self) -> AsyncIterator[AsyncConnection]:
        """One writer at a time; the block commits on success and rolls back on error."""
        async with self._write_lock, self.engine.begin() as conn:
            yield conn

    async def snapshot(self, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with self._write_lock:
            dest.unlink(missing_ok=True)
            await asyncio.to_thread(_vacuum_into, self.path, dest)

    async def restore(self, src: Path) -> None:
        """Replace the live DB contents with a snapshot, in place (no file swap under open handles)."""
        if not src.is_file():
            raise FileNotFoundError(f"snapshot not found: {src}")
        async with self._write_lock:
            async with self._gate:
                self._restoring = True
            try:
                async with self._gate:
                    try:
                        await asyncio.wait_for(
                            self._gate.wait_for(lambda: self._readers == 0), RESTORE_READER_TIMEOUT
                        )
                    except TimeoutError as exc:
                        raise RuntimeError(
                            f"restore aborted: {self._readers} reader(s) still active after "
                            f"{RESTORE_READER_TIMEOUT}s"
                        ) from exc
                try:
                    await asyncio.to_thread(_backup_into, src, self.path)
                except sqlite3.Error as exc:
                    raise RuntimeError(f"restore failed, live database unchanged: {exc}") from exc
                await self.engine.dispose()
            finally:
                async with self._gate:
                    self._restoring = False
                    self._gate.notify_all()
```

`backend/arth/core/tables.py`:
```python
"""SQLAlchemy Core tables owned by L0. Later layers add their own table modules."""

from __future__ import annotations

from sqlalchemy import Column, Float, Integer, String, Table, Text

from arth.core.db import metadata

jobs = Table(
    "jobs",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("due_at", String, nullable=False, index=True),
    Column("every_seconds", Integer, nullable=True),
    Column("daily_at", String, nullable=True),
    Column("payload", Text, nullable=False, server_default="{}"),
    Column("status", String, nullable=False, server_default="pending"),
    Column("attempts", Integer, nullable=False, server_default="0"),
    Column("last_error", Text, nullable=True),
    Column("ran_at", String, nullable=True),
)

spans = Table(
    "spans",
    metadata,
    Column("id", String, primary_key=True),
    Column("trace_id", String, nullable=False, index=True),
    Column("parent_id", String, nullable=True),
    Column("kind", String, nullable=False),
    Column("name", String, nullable=False),
    Column("start_at", String, nullable=False),
    Column("dur_ms", Float, nullable=False),
    Column("mode", String, nullable=False, server_default="none"),
    Column("cost_paise", Integer, nullable=False, server_default="0"),
    Column("attrs", Text, nullable=False, server_default="{}"),
)
```

`backend/arth/core/migrate.py`:
```python
"""Run Alembic migrations programmatically (app boot, tests, scenario snapshots)."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from alembic import command
from alembic.config import Config

from arth.core.paths import BACKEND_DIR


def upgrade(db_path: Path, revision: str = "head") -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    # URL-quote (SQLAlchemy unquotes the path), then escape % for configparser interpolation.
    cfg.set_main_option(
        "sqlalchemy.url", f"sqlite:///{quote(db_path.as_posix(), safe='/:')}".replace("%", "%%")
    )
    command.upgrade(cfg, revision)
```

- [ ] **Step 4: Create the Alembic files**

`backend/alembic.ini`:
```ini
# The app runs migrations via arth.core.migrate.upgrade(), which overrides both values below
# with absolute paths. This file is for the Alembic CLI only.
[alembic]
script_location = %(here)s/migrations
sqlalchemy.url = sqlite:///%(here)s/data/arth.db
```

`backend/migrations/env.py`:
```python
from alembic import context
from sqlalchemy import engine_from_config, pool

# Every new table module must be imported here so its tables register on metadata;
# otherwise autogenerate and the schema-drift test will not see them.
import arth.core.tables  # noqa: F401  (registers L0 tables on metadata)
from arth.core.db import metadata

config = context.config
target_metadata = metadata


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
```

`backend/migrations/script.py.mako`:
```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

`backend/migrations/versions/0001_l0_foundations.py`:
```python
"""L0 foundations: jobs and spans.

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("due_at", sa.String(), nullable=False),
        sa.Column("every_seconds", sa.Integer(), nullable=True),
        sa.Column("daily_at", sa.String(), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("ran_at", sa.String(), nullable=True),
    )
    op.create_index("ix_jobs_due_at", "jobs", ["due_at"])
    op.create_table(
        "spans",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("trace_id", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), nullable=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("start_at", sa.String(), nullable=False),
        sa.Column("dur_ms", sa.Float(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False, server_default="none"),
        sa.Column("cost_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attrs", sa.Text(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_spans_trace_id", "spans", ["trace_id"])


def downgrade() -> None:
    op.drop_table("spans")
    op.drop_table("jobs")
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_db.py -q`
Expected: `4 passed`.

- [ ] **Step 6: Checkpoint**

Run: `python dev.py lint typecheck test`
Expected: all green.

---

**Post-review additions (database)**

`backend/tests/test_migrations.py`:
```python
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

import arth.core.tables  # noqa: F401  (registers tables on metadata)
from arth.core.db import metadata
from arth.core.migrate import upgrade


def test_migrations_match_models(tmp_path: Path) -> None:
    path = tmp_path / "drift.db"
    upgrade(path)
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    try:
        with engine.connect() as conn:
            ctx = MigrationContext.configure(conn, opts={"compare_type": True})
            assert compare_metadata(ctx, metadata) == []
    finally:
        engine.dispose()


def test_upgrade_handles_percent_in_path(tmp_path: Path) -> None:
    path = tmp_path / "a%20b" / "arth.db"
    upgrade(path)
    assert path.is_file()
```

### Task 7: Job scheduler and tick loop (T0.4, part 2)

**Files:**
- Create: `backend/arth/core/scheduler.py`
- Test: `backend/tests/test_scheduler.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_scheduler.py`:
```python
import asyncio
import logging
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select, update

from arth.core.clock import IST, ClockError, SimClock, parse_iso
from arth.core.db import Database
from arth.core.scheduler import Job, Scheduler, tick_loop
from arth.core.tables import jobs

START = datetime(2026, 10, 29, 7, 45, tzinfo=IST)


async def test_jumping_eight_days_runs_eight_nightly_jobs_in_order(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    seen: list[datetime] = []

    async def night_shift(job: Job) -> None:
        seen.append(clock.now_ist())

    scheduler.on("night_shift", night_shift)
    await scheduler.schedule_daily("night_shift", "22:00")
    ran = await scheduler.advance_to(START + timedelta(days=8))

    assert ran == 8
    assert [(d.day, d.hour, d.minute) for d in seen] == [
        (29, 22, 0),
        (30, 22, 0),
        (31, 22, 0),
        (1, 22, 0),
        (2, 22, 0),
        (3, 22, 0),
        (4, 22, 0),
        (5, 22, 0),
    ]
    assert clock.now() == (START + timedelta(days=8)).astimezone(clock.now().tzinfo)


async def test_jobs_run_in_due_order_across_names(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    order: list[str] = []

    async def record(job: Job) -> None:
        order.append(job.payload["tag"])

    scheduler.on("a", record)
    scheduler.on("b", record)
    await scheduler.schedule("b", START + timedelta(hours=2), {"tag": "second"})
    await scheduler.schedule("a", START + timedelta(hours=1), {"tag": "first"})
    await scheduler.advance_to(START + timedelta(hours=3))
    assert order == ["first", "second"]


async def test_failed_job_is_marked_and_does_not_stop_others(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    done: list[str] = []

    async def boom(job: Job) -> None:
        raise RuntimeError("boom")

    async def ok(job: Job) -> None:
        done.append("ok")

    scheduler.on("boom", boom)
    scheduler.on("ok", ok)
    await scheduler.schedule("boom", START + timedelta(minutes=1))
    await scheduler.schedule("ok", START + timedelta(minutes=2))
    await scheduler.advance_to(START + timedelta(minutes=5))
    assert done == ["ok"]
    assert await scheduler.count(status="failed") == 1


async def test_tick_loop_runs_due_jobs_while_clock_runs(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    fired = asyncio.Event()

    async def handler(job: Job) -> None:
        fired.set()

    scheduler.on("soon", handler)
    await scheduler.schedule("soon", START + timedelta(minutes=1))
    clock.run(rate=3600.0)
    stop = asyncio.Event()
    task = asyncio.create_task(tick_loop(scheduler, stop, interval_s=0.01))
    await asyncio.wait_for(fired.wait(), timeout=2)
    stop.set()
    await task


async def test_eight_nights_record_each_ran_at(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)

    async def noop(job: Job) -> None:
        return None

    scheduler.on("night_shift", noop)
    await scheduler.schedule_daily("night_shift", "22:00")
    await scheduler.advance_to(START + timedelta(days=8))
    async with db.read() as conn:
        rows = (
            await conn.execute(select(jobs.c.ran_at).where(jobs.c.status == "done").order_by(jobs.c.ran_at))
        ).all()
    ran_at = [parse_iso(r[0]).astimezone(IST) for r in rows]
    assert [(d.day, d.hour, d.minute) for d in ran_at] == [(d, 22, 0) for d in (29, 30, 31, 1, 2, 3, 4, 5)]


async def test_concurrent_run_due_and_advance_run_job_once(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    calls: list[str] = []

    async def slow(job: Job) -> None:
        calls.append(job.id)
        await asyncio.sleep(0.05)

    scheduler.on("night_shift", slow)
    await scheduler.schedule_daily("night_shift", "22:00")
    due = START.replace(hour=22, minute=0)
    clock.set(due)
    await asyncio.gather(scheduler.run_due(), scheduler.advance_to(due + timedelta(hours=1)))
    assert len(calls) == 1
    assert await scheduler.count(status="done") == 1
    assert await scheduler.count(status="pending") == 1


async def test_recover_resets_running_jobs_to_pending(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    job_id = await scheduler.schedule("x", START)
    async with db.write() as conn:
        await conn.execute(update(jobs).where(jobs.c.id == job_id).values(status="running"))
    assert await scheduler.recover() == 1
    assert await scheduler.count(status="pending") == 1
    assert await scheduler.count(status="running") == 0


async def test_done_and_successor_commit_together(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)

    async def noop(job: Job) -> None:
        return None

    scheduler.on("n", noop)
    await scheduler.schedule_daily("n", "22:00")
    await scheduler.advance_to(START + timedelta(hours=15))
    assert await scheduler.count(status="done") == 1
    assert await scheduler.count(status="pending") == 1


async def test_advance_to_on_running_clock_does_not_go_backwards(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)

    async def slow(job: Job) -> None:
        await asyncio.sleep(0.05)

    scheduler.on("j", slow)
    await scheduler.schedule("j", START + timedelta(seconds=1))
    clock.run(rate=10_000.0)
    assert clock.running
    assert await scheduler.advance_to(START + timedelta(seconds=2)) == 1
    assert clock.now() >= START + timedelta(seconds=2)


async def test_tick_loop_survives_run_due_error(db: Database, monkeypatch: pytest.MonkeyPatch) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    fired = asyncio.Event()

    async def handler(job: Job) -> None:
        fired.set()

    scheduler.on("soon", handler)
    await scheduler.schedule("soon", START)
    real = scheduler._claim_next
    state = {"calls": 0}

    async def flaky(until: datetime) -> Job | None:
        state["calls"] += 1
        if state["calls"] == 1:
            raise RuntimeError("db hiccup")
        return await real(until)

    monkeypatch.setattr(scheduler, "_claim_next", flaky)
    stop = asyncio.Event()
    task = asyncio.create_task(tick_loop(scheduler, stop, interval_s=0.01))
    await asyncio.wait_for(fired.wait(), timeout=2)
    stop.set()
    await task


def test_every_seconds_must_be_positive(db: Database) -> None:
    scheduler = Scheduler(db, SimClock(START))
    for bad in (0, -5):
        with pytest.raises(ValueError):
            asyncio.run(scheduler.schedule("x", START, every_seconds=bad))


async def test_same_instant_jobs_run_in_insertion_order(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    order: list[str] = []

    async def record(job: Job) -> None:
        order.append(job.payload["tag"])

    scheduler.on("t", record)
    tags = [f"t{i}" for i in range(10)]
    for tag in tags:
        await scheduler.schedule("t", START + timedelta(minutes=1), {"tag": tag})
    await scheduler.advance_to(START + timedelta(minutes=2))
    assert order == tags


async def test_unhandled_job_stays_pending_and_warns_once(
    db: Database, caplog: pytest.LogCaptureFixture
) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    await scheduler.schedule("ghost", START + timedelta(minutes=1))
    with caplog.at_level(logging.WARNING, logger="arth.core.scheduler"):
        await scheduler.advance_to(START + timedelta(minutes=5))
        await scheduler.run_due()
    assert await scheduler.count(status="pending") == 1
    assert await scheduler.count(status="failed") == 0
    assert len([r for r in caplog.records if "ghost" in r.getMessage()]) == 1


async def test_interval_job_reschedules_from_due_time(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    runs: list[datetime] = []

    async def tick(job: Job) -> None:
        runs.append(job.due_at)

    scheduler.on("poll", tick)
    await scheduler.schedule("poll", START + timedelta(hours=1), every_seconds=3600)
    assert await scheduler.advance_to(START + timedelta(hours=3, minutes=30)) == 3
    assert runs == [(START + timedelta(hours=h)).astimezone(runs[0].tzinfo) for h in (1, 2, 3)]
    assert await scheduler.count(status="pending") == 1


async def test_job_scheduled_by_handler_inside_window_runs_in_same_advance(db: Database) -> None:
    clock = SimClock(START)
    scheduler = Scheduler(db, clock)
    order: list[str] = []

    async def first(job: Job) -> None:
        order.append("first")
        await scheduler.schedule("second", clock.now() + timedelta(minutes=10))

    async def second(job: Job) -> None:
        order.append("second")

    scheduler.on("first", first)
    scheduler.on("second", second)
    await scheduler.schedule("first", START + timedelta(minutes=5))
    assert await scheduler.advance_to(START + timedelta(hours=1)) == 2
    assert order == ["first", "second"]


async def test_advance_backwards_raises(db: Database) -> None:
    scheduler = Scheduler(db, SimClock(START))
    with pytest.raises(ClockError):
        await scheduler.advance_to(START - timedelta(minutes=1))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_scheduler.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.core.scheduler'`.

- [ ] **Step 3: Implement**

`backend/arth/core/scheduler.py`:
```python
"""Jobs on sim time. Jumping the clock runs every due job in order (spec v5.1 D6)."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import Insert, func, insert, select, text, update

from arth.core.clock import ClockError, SimClock, iso_utc, next_daily, parse_iso
from arth.core.db import Database
from arth.core.ids import new_id
from arth.core.tables import jobs

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Job:
    id: str
    name: str
    due_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)
    every_seconds: int | None = None
    daily_at: str | None = None


Handler = Callable[[Job], Awaitable[None]]


class Scheduler:
    """Persistent job scheduler on sim time.

    Execution is serialised by an internal lock and each job is claimed atomically
    (pending -> running), so concurrent `run_due`/`advance_to` calls never run a job twice.
    Call `await recover()` once at startup (API lifespan) before `tick_loop` starts.
    Handlers must not call `run_due()`/`advance_to()` (the run lock is not reentrant: deadlock);
    scheduling new jobs from a handler is fine.
    """

    def __init__(self, db: Database, clock: SimClock) -> None:
        self.db = db
        self.clock = clock
        self._handlers: dict[str, Handler] = {}
        self._run_lock = asyncio.Lock()
        self._warned_unhandled: set[str] = set()

    def on(self, name: str, handler: Handler) -> None:
        """Register `handler` for jobs called `name`.

        Delivery is at-least-once: handlers MUST be idempotent. If the process dies while a
        handler runs, the job stays `running` and is re-run after `recover()`.
        """
        self._handlers[name] = handler

    async def recover(self) -> int:
        """Startup recovery: jobs left `running` by a crash go back to `pending`."""
        async with self.db.write() as conn:
            result = await conn.execute(
                update(jobs).where(jobs.c.status == "running").values(status="pending")
            )
            return int(result.rowcount)  # type: ignore[attr-defined]

    async def schedule(
        self,
        name: str,
        due_at: datetime,
        payload: dict[str, Any] | None = None,
        *,
        every_seconds: int | None = None,
        daily_at: str | None = None,
    ) -> str:
        if every_seconds is not None and every_seconds <= 0:
            raise ValueError("every_seconds must be > 0")
        job_id = new_id("job")
        async with self.db.write() as conn:
            await conn.execute(self._insert(job_id, name, due_at, payload or {}, every_seconds, daily_at))
        return job_id

    @staticmethod
    def _insert(
        job_id: str,
        name: str,
        due_at: datetime,
        payload: dict[str, Any],
        every_seconds: int | None,
        daily_at: str | None,
    ) -> Insert:
        return insert(jobs).values(
            id=job_id,
            name=name,
            due_at=iso_utc(due_at),
            payload=json.dumps(payload, sort_keys=True),
            every_seconds=every_seconds,
            daily_at=daily_at,
        )

    async def schedule_daily(self, name: str, at_ist: str, payload: dict[str, Any] | None = None) -> str:
        return await self.schedule(name, next_daily(self.clock.now(), at_ist), payload, daily_at=at_ist)

    async def count(self, *, status: str) -> int:
        async with self.db.read() as conn:
            result = await conn.execute(select(func.count()).select_from(jobs).where(jobs.c.status == status))
            return int(result.scalar_one())

    async def run_due(self) -> int:
        async with self._run_lock:
            ran = 0
            while (job := await self._claim_next(self.clock.now())) is not None:
                await self._run(job)
                ran += 1
            return ran

    async def advance_to(self, target: datetime) -> int:
        if target < self.clock.now():
            raise ClockError("advance_to cannot go backwards")
        async with self._run_lock:
            ran = 0
            while (job := await self._claim_next(target)) is not None:
                if job.due_at > self.clock.now():
                    self.clock.set(job.due_at)
                await self._run(job)
                ran += 1
            if target > self.clock.now():  # a running clock may already be past target
                self.clock.set(target)
            return ran

    async def _claim_next(self, until: datetime) -> Job | None:
        """Atomically move the earliest due, handled job pending -> running; None if there is none."""
        names = list(self._handlers)
        await self._warn_unhandled(until, names)
        while True:
            async with self.db.write() as conn:
                row = (
                    (
                        await conn.execute(
                            select(jobs)
                            .where(
                                jobs.c.status == "pending",
                                jobs.c.due_at <= iso_utc(until),
                                jobs.c.name.in_(names),
                            )
                            .order_by(jobs.c.due_at, text("rowid"))
                            .limit(1)
                        )
                    )
                    .mappings()
                    .first()
                )
                if row is None:
                    return None
                claimed = await conn.execute(
                    update(jobs)
                    .where(jobs.c.id == row["id"], jobs.c.status == "pending")
                    .values(status="running")
                )
                if claimed.rowcount != 1:  # type: ignore[attr-defined]
                    continue
            return Job(
                id=row["id"],
                name=row["name"],
                due_at=parse_iso(row["due_at"]),
                payload=json.loads(row["payload"]),
                every_seconds=row["every_seconds"],
                daily_at=row["daily_at"],
            )

    async def _warn_unhandled(self, until: datetime, names: list[str]) -> None:
        async with self.db.read() as conn:
            result = await conn.execute(
                select(jobs.c.name)
                .where(jobs.c.status == "pending", jobs.c.due_at <= iso_utc(until), jobs.c.name.not_in(names))
                .distinct()
            )
            missing = {r[0] for r in result} - self._warned_unhandled
        for name in sorted(missing):
            self._warned_unhandled.add(name)
            log.warning("no handler registered for job %r; leaving it pending", name)

    async def _run(self, job: Job) -> None:
        handler = self._handlers[job.name]
        log.debug("running job %s (%s) due %s", job.id, job.name, job.due_at.isoformat())
        status, error = "done", None
        try:
            await handler(job)
        except Exception as exc:  # a failing job must not stop the night
            log.exception("job %s (%s) failed", job.id, job.name)
            status, error = "failed", repr(exc)
        # One transaction: mark finished and enqueue the successor together.
        async with self.db.write() as conn:
            await conn.execute(
                update(jobs)
                .where(jobs.c.id == job.id)
                .values(
                    status=status,
                    last_error=error,
                    attempts=jobs.c.attempts + 1,
                    ran_at=iso_utc(self.clock.now()),
                )
            )
            successor = self._successor(job)
            if successor is not None:
                await conn.execute(successor)

    def _successor(self, job: Job) -> Insert | None:
        if job.every_seconds:
            due = job.due_at + timedelta(seconds=job.every_seconds)
        elif job.daily_at:
            due = next_daily(job.due_at, job.daily_at)
        else:
            return None
        return self._insert(new_id("job"), job.name, due, job.payload, job.every_seconds, job.daily_at)


async def tick_loop(scheduler: Scheduler, stop: asyncio.Event, interval_s: float = 1.0) -> None:
    """Run due jobs every `interval_s` real seconds until `stop` is set."""
    while not stop.is_set():
        try:
            await scheduler.run_due()
        except Exception:  # keep the night shift alive; CancelledError still propagates
            log.exception("scheduler tick failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_s)
        except TimeoutError:
            pass
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_scheduler.py -q`
Expected: `4 passed`.

- [ ] **Step 5: Checkpoint**

Run: `python dev.py lint typecheck test`
Expected: all green.

---

### Task 8: Settings and secrets, policies, providers, and the India-wide calendar (T0.7)

**Files:**
- Create: `backend/arth/core/config.py`, `backend/arth/core/calendar.py`, `backend/arth/core/yamlconf.py`, `backend/config/policies.yaml`, `backend/config/providers.yaml`
- Already present (written during planning; this task validates them): `backend/.env.example`, `backend/.env`, `frontend/.env.local`, `backend/config/calendar/regions.yaml`, `backend/config/calendar/events-2025.yaml`, `backend/config/calendar/events-2026.yaml`, `backend/config/calendar/events-2027.yaml`, `backend/config/calendar/seasons-2026-27.yaml`
- Test: `backend/tests/test_config.py`, `backend/tests/test_calendar.py`

The calendar is spec Part D3: events are scoped national, by state (ISO 3166-2:IN) or by city, with per-state date overrides, a confidence label and a source. `CalendarIndex` answers "what applies to this shop's city between these dates", for example Karva Chauth in Lucknow but Pongal in Chennai.

- [ ] **Step 1: Confirm the planning-time files exist**

Run: `python -c "import pathlib; [print(p, pathlib.Path(p).is_file()) for p in ['backend/.env', 'backend/.env.example', 'backend/config/calendar/regions.yaml', 'backend/config/calendar/events-2026.yaml', 'backend/config/calendar/events-2025.yaml', 'backend/config/calendar/events-2027.yaml', 'backend/config/calendar/seasons-2026-27.yaml']]"`
Expected: every line ends with `True`. Put your keys into `backend/.env` (`MISTRAL_API_KEY`, `GROQ_API_KEY`, `SARVAM_API_KEY`) whenever you have them. Nothing in L0 calls a provider, and every test ignores `.env`.

- [ ] **Step 2: Write the policy and provider configs**

`backend/config/policies.yaml` (spec Part F1):
```yaml
tiers:
  counter.add_lines: R1
  ledger.add_entry: R2
  supply.place_po: R3
  outreach.send_campaign: R3
  offers.create_program: R3
  treasury.refund: R4
  capital.apply: R4
  privacy.erase_patron: R4
roles:
  owner: { max_tier: R4, approve: [R2, R3] }
  manager: { max_tier: R2, approve: [R2] }
  cashier: { max_tier: R1, allow: [treasury.cash_payment] }
  helper: { max_tier: R1 }
quiet_hours: { start: '21:30', end: '08:00' }
contact_caps: { marketing_per_patron_per_week: 1 }
reminders: { per_patron_per_week: 1, cadence_days: [0, 7, 14] }
growth: { holdout_share: 0.2, holdout_min: 1, margin_floor: 0.15, monthly_incentive_budget_paise: 0 }
expiry_alert_days: { default: 30 }
discreet_mode: { busy_hours: ['09:00-11:00', '17:30-21:00'] }
attention: { proactive_per_day: 1, urgent_interrupts_per_day: 3 }
forbid_offers_on_flags: []
```

`backend/config/providers.yaml` (spec Part G0–G1; aliases current on 30 Oct 2026, pinned to dated versions in T4.2):
```yaml
roles:
  llm.fast:
    chain:
      - { provider: mistral, model: mistral-small-latest, timeout_ms: 2500, json: true }
      - { provider: groq, model: openai/gpt-oss-20b, timeout_ms: 2500, json: true }
      - { provider: cassette }
  llm.large:
    chain:
      - { provider: mistral, model: mistral-large-latest, timeout_ms: 4000, json: true }
      - { provider: groq, model: openai/gpt-oss-120b, timeout_ms: 4000, json: true }
      - { provider: cassette }
  vision:
    chain:
      - { provider: mistral, model: mistral-medium-latest, timeout_ms: 4000 }
      - { provider: mistral, model: mistral-small-latest, timeout_ms: 4000 }
      - { provider: cassette }
  ocr:
    chain:
      - { provider: mistral, model: mistral-ocr-latest, timeout_ms: 20000 }
      - { provider: sarvam, model: sarvam-vision, timeout_ms: 20000 }
      - { provider: cassette }
  stt:
    chain:
      - { provider: sarvam, model: 'saaras:v4', timeout_ms: 2500, langs: [hi, en, mr, ta, bn, gu, te] }
      - { provider: groq, model: whisper-large-v3, timeout_ms: 3000 }
  tts:
    chain:
      - { provider: sarvam, model: 'bulbul:v4-flash', timeout_ms: 2000, langs: [hi, en, mr, ta, bn, gu, te] }
      - { provider: sarvam, model: 'bulbul:v3', timeout_ms: 2000 }
      - { provider: cassette }
  translate:
    chain:
      - { provider: sarvam, model: sarvam-translate, timeout_ms: 2000 }
  guard:
    chain:
      - { provider: mistral, model: mistral-small-latest, timeout_ms: 1000, json: true }
      - { provider: groq, model: openai/gpt-oss-20b, timeout_ms: 1000, json: true }
  persona:
    chain:
      - { provider: groq, model: openai/gpt-oss-20b, timeout_ms: 3000 }
      - { provider: cassette }
providers:
  mistral: { api_key_env: MISTRAL_API_KEY, data_tag: merchant_ok_if_paid_plan }
  groq: { api_key_env: GROQ_API_KEY, data_tag: synthetic_only_on_free_tier }
  sarvam: { api_key_env: SARVAM_API_KEY, data_tag: merchant_ok_if_paid_plan, rate: { rpm: 60 } }
```

- [ ] **Step 3: Write the failing tests**

`backend/tests/test_config.py`:
```python
from pathlib import Path

import pytest

from arth.core.config import (
    ConfigError,
    Settings,
    check_auth_tokens,
    check_provider_keys,
    load_policies,
    load_providers,
    provider_status,
)
from arth.core.paths import CONFIG_DIR, DATA_DIR

CONFIG = CONFIG_DIR
KEY_VARS = ("MISTRAL_API_KEY", "GROQ_API_KEY", "SARVAM_API_KEY")
TOKEN_VARS = ("ARTH_DIRECTOR_TOKEN", "ARTH_DEVICE_TOKEN", "ARTH_CONSOLE_TOKEN")


@pytest.fixture
def no_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (*KEY_VARS, *TOKEN_VARS, "ARTH_MODE"):
        monkeypatch.delenv(name, raising=False)


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_repo_policies_load() -> None:
    policies = load_policies(CONFIG / "policies.yaml")
    assert policies.roles["owner"].max_tier == "R4"
    assert policies.tiers, "every action has a tier"
    assert 0 <= policies.growth.margin_floor <= 1


def test_bad_tier_fails_with_file_name(tmp_path: Path) -> None:
    text = (
        (CONFIG / "policies.yaml")
        .read_text(encoding="utf-8")
        .replace("ledger.add_entry: R2", "ledger.add_entry: R9")
    )
    with pytest.raises(ConfigError, match="policies.yaml"):
        load_policies(write(tmp_path, "policies.yaml", text))


def test_policies_require_owner_role(tmp_path: Path) -> None:
    text = (CONFIG / "policies.yaml").read_text(encoding="utf-8").replace("  owner:", "  boss:")
    with pytest.raises(ConfigError, match="owner"):
        load_policies(write(tmp_path, "policies.yaml", text))


@pytest.mark.parametrize("bad", ["9:5", "25:00", "21:60", "abc", "21.30", "2130"])
def test_quiet_hours_must_be_hh_mm(tmp_path: Path, bad: str) -> None:
    text = (CONFIG / "policies.yaml").read_text(encoding="utf-8").replace("start: '21:30'", f"start: '{bad}'")
    with pytest.raises(ConfigError, match="HH:MM"):
        load_policies(write(tmp_path, "policies.yaml", text))


def test_repo_providers_structure() -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    assert providers.used() <= providers.providers.keys()
    for env in (p.api_key_env for p in providers.providers.values()):
        assert env.endswith("_API_KEY")


def test_repo_providers_use_the_decided_stack() -> None:
    # Team decisions, pinned on purpose: Mistral primary LLM, Groq backup, Sarvam STT/TTS models.
    providers = load_providers(CONFIG / "providers.yaml")
    assert providers.roles["llm.fast"].chain[0].provider == "mistral"
    assert providers.roles["llm.fast"].chain[1].provider == "groq"
    assert providers.roles["stt"].chain[0].model == "saaras:v4"
    assert providers.roles["tts"].chain[0].model == "bulbul:v4-flash"
    assert providers.providers["sarvam"].api_key_env == "SARVAM_API_KEY"


def test_unknown_provider_in_chain_fails(tmp_path: Path) -> None:
    text = (
        (CONFIG / "providers.yaml")
        .read_text(encoding="utf-8")
        .replace(
            "provider: groq, model: openai/gpt-oss-20b, timeout_ms: 3000",
            "provider: openx, model: x, timeout_ms: 3000",
        )
    )
    with pytest.raises(ConfigError, match="openx"):
        load_providers(write(tmp_path, "providers.yaml", text))


def test_unknown_key_env_fails(tmp_path: Path) -> None:
    text = (
        (CONFIG / "providers.yaml")
        .read_text(encoding="utf-8")
        .replace("api_key_env: GROQ_API_KEY", "api_key_env: GROQ_KEY")
    )
    with pytest.raises(ConfigError, match="GROQ_KEY"):
        load_providers(write(tmp_path, "providers.yaml", text))


def test_settings_defaults_point_inside_repo(no_key_env: None) -> None:
    settings = Settings(_env_file=None)
    assert settings.mode == "dev"
    assert settings.db_path == DATA_DIR / "arth.db"
    assert settings.clock_start.isoformat() == "2026-10-29T07:45:00+05:30"
    assert settings.mistral_api_key is None


def test_keys_come_from_the_env_file_as_secrets(tmp_path: Path, no_key_env: None) -> None:
    env = write(tmp_path, ".env", "MISTRAL_API_KEY=sk-test-123\nGROQ_API_KEY=\nARTH_MODE=demo\n")
    settings = Settings(_env_file=env)
    assert settings.mode == "demo"
    assert settings.mistral_api_key is not None
    assert settings.mistral_api_key.get_secret_value() == "sk-test-123"
    assert settings.groq_api_key is None, "a blank value means 'not set'"
    assert "sk-test-123" not in repr(settings)
    assert "sk-test-123" not in settings.model_dump_json()


def test_auth_tokens_are_secrets(tmp_path: Path, no_key_env: None) -> None:
    env = write(tmp_path, ".env", "ARTH_DIRECTOR_TOKEN=tok-director-xyz\nARTH_DEVICE_TOKEN=tok-device-xyz\n")
    settings = Settings(_env_file=env)
    assert settings.director_token.get_secret_value() == "tok-director-xyz"
    dumped = repr(settings) + settings.model_dump_json()
    for text in ("tok-director-xyz", "tok-device-xyz", "dev-console"):
        assert text not in dumped


def test_prod_refuses_default_dev_tokens(no_key_env: None) -> None:
    with pytest.raises(ConfigError) as err:
        check_auth_tokens(Settings(_env_file=None, mode="prod"))
    message = str(err.value)
    for env in TOKEN_VARS:
        assert env in message
    assert "dev-director" not in message


def test_prod_accepts_real_tokens_and_dev_accepts_defaults(tmp_path: Path, no_key_env: None) -> None:
    check_auth_tokens(Settings(_env_file=None, mode="dev"))
    env = write(
        tmp_path,
        ".env",
        "ARTH_MODE=prod\nARTH_DIRECTOR_TOKEN=a-long-random-1\nARTH_DEVICE_TOKEN=a-long-random-2\n"
        "ARTH_CONSOLE_TOKEN=a-long-random-3\n",
    )
    check_auth_tokens(Settings(_env_file=env))


def test_prod_refuses_to_boot_without_keys(no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    with pytest.raises(ConfigError, match="MISTRAL_API_KEY.*SARVAM_API_KEY"):
        check_provider_keys(Settings(_env_file=None, mode="prod"), providers)


def test_prod_boots_when_all_keys_are_present(tmp_path: Path, no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    env = write(
        tmp_path,
        ".env",
        "ARTH_MODE=prod\nMISTRAL_API_KEY=fake-m\nGROQ_API_KEY=fake-g\nSARVAM_API_KEY=fake-s\n",
    )
    settings = Settings(_env_file=env)
    check_provider_keys(settings, providers)
    assert provider_status(settings, providers) == {"mistral": True, "groq": True, "sarvam": True}


def test_config_errors_never_contain_key_text(tmp_path: Path, no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    env = write(
        tmp_path, ".env", "ARTH_MODE=prod\nMISTRAL_API_KEY=sk-secret-aaa\nGROQ_API_KEY=sk-secret-bbb\n"
    )
    with pytest.raises(ConfigError) as err:
        check_provider_keys(Settings(_env_file=env), providers)
    assert "SARVAM_API_KEY" in str(err.value)
    assert "sk-secret" not in str(err.value)


def test_dev_boots_without_keys_and_reports_status(no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    settings = Settings(_env_file=None, mode="dev")
    check_provider_keys(settings, providers)
    status = provider_status(settings, providers)
    assert set(status) == set(providers.providers)
    assert not any(status.values())
```

`backend/tests/test_calendar.py`:
```python
from datetime import date
from pathlib import Path

import pytest

from arth.core.calendar import CalendarIndex, Occurrence, load_calendar
from arth.core.config import ConfigError
from arth.core.paths import CONFIG_DIR

DEMO_DAY = date(2026, 10, 29)


@pytest.fixture(scope="module")
def repo() -> CalendarIndex:
    return CalendarIndex(load_calendar(CONFIG_DIR / "calendar"))


def kinds(index: CalendarIndex, city: str, start: date, end: date) -> set[str]:
    return {o.kind for o in index.between(city, start, end)}


# ---- Demo-scenario invariants (gupta_diwali, Lucknow) -----------------------------------------
# These pin real repo data used by the demo; if one fails, fix the calendar YAML row (cite its source).


def test_lucknow_sees_karva_chauth_on_demo_day_and_chennai_does_not(repo: CalendarIndex) -> None:
    assert "karva_chauth" in kinds(repo, "lucknow", DEMO_DAY, DEMO_DAY)
    assert "karva_chauth" not in kinds(repo, "chennai", DEMO_DAY, DEMO_DAY)


def test_chennai_sees_pongal_and_lucknow_does_not(repo: CalendarIndex) -> None:
    jan = (date(2026, 1, 13), date(2026, 1, 17))
    assert "pongal" in kinds(repo, "chennai", *jan)
    assert "pongal" not in kinds(repo, "lucknow", *jan)


def test_kolkata_durga_puja_and_varanasi_dev_deepawali(repo: CalendarIndex) -> None:
    assert "durga_puja" in kinds(repo, "kolkata", date(2026, 10, 17), date(2026, 10, 20))
    assert "dev_deepawali" in kinds(repo, "varanasi", date(2026, 11, 24), date(2026, 11, 24))
    assert "dev_deepawali" not in kinds(repo, "lucknow", date(2026, 11, 24), date(2026, 11, 24))


def test_diwali_is_ten_days_from_demo_start_in_lucknow(repo: CalendarIndex) -> None:
    assert repo.days_until("diwali", DEMO_DAY, city="lucknow") == 10


def test_lucknow_demo_window_has_the_whole_festive_run(repo: CalendarIndex) -> None:
    window = kinds(repo, "lucknow", DEMO_DAY, date(2026, 11, 30))
    assert {
        "karva_chauth",
        "dhanteras",
        "diwali",
        "govardhan_puja",
        "bhai_dooj",
        "chhath",
        "guru_nanak_jayanti",
    } <= window


def test_last_years_diwali_is_available_for_comparison(repo: CalendarIndex) -> None:
    assert "diwali" in kinds(repo, "lucknow", date(2025, 10, 20), date(2025, 10, 20))


def test_salary_week_recurs_monthly(repo: CalendarIndex) -> None:
    salary = [
        o for o in repo.between("lucknow", date(2026, 11, 1), date(2026, 11, 30)) if o.kind == "salary_days"
    ]
    assert [o.start.day for o in salary] == [1, 2, 3, 4, 5, 6, 7]


# ---- Repo-wide invariants ----------------------------------------------------------------------


def test_every_event_has_source_and_confidence(repo: CalendarIndex) -> None:
    for occurrence in repo.between("lucknow", date(2025, 8, 1), date(2027, 12, 31)):
        assert occurrence.confidence and occurrence.source


def test_unknown_city_is_a_clear_error(repo: CalendarIndex) -> None:
    with pytest.raises(ConfigError, match="regions.yaml"):
        repo.between("atlantis", DEMO_DAY, DEMO_DAY)


# ---- Fixture calendars -------------------------------------------------------------------------

REGIONS = (
    "states:\n"
    "  - { code: IN-UP, name: Uttar Pradesh, ui_locale: hi, cities: [lucknow] }\n"
    "  - { code: IN-TN, name: Tamil Nadu, ui_locale: ta, cities: [chennai] }\n"
)


def fixture_calendar(tmp_path: Path, events_yaml: str, regions: str = REGIONS) -> Path:
    folder = tmp_path / "calendar"
    folder.mkdir()
    (folder / "regions.yaml").write_text(regions, encoding="utf-8")
    (folder / "events-test.yaml").write_text(events_yaml, encoding="utf-8")
    return folder


EVENT = """events:
  - id: fest_2026
    kind: fest
    type: festival
    names: {{ en: Fest }}
    start: 2026-11-08
    {extra}
    confidence: regional_variant
    source: test
"""

RECURRING = """recurring:
  - id: rec
    kind: rec
    names: {{ en: Rec }}
    rule: monthly_days
    days: {days}
    scope: {{ national: true }}
    source: test
"""


def build(tmp_path: Path, yaml_text: str) -> CalendarIndex:
    return CalendarIndex(load_calendar(fixture_calendar(tmp_path, yaml_text)))


def test_state_override_moves_the_date_for_that_state_only(tmp_path: Path) -> None:
    index = build(
        tmp_path, EVENT.format(extra="scope: { national: true }\n    date_overrides: { IN-TN: 2026-11-07 }")
    )
    assert index.days_until("fest", DEMO_DAY, city="lucknow") == 10
    assert index.days_until("fest", DEMO_DAY, city="chennai") == 9


def test_multi_day_event_counts_while_ongoing(tmp_path: Path) -> None:
    index = build(tmp_path, EVENT.format(extra="end: 2026-11-12\n    scope: { national: true }"))
    assert [o.kind for o in index.upcoming("lucknow", date(2026, 11, 10), within_days=0)] == ["fest"]


def test_unknown_place_fails_at_boot_and_names_the_file(tmp_path: Path) -> None:
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: { states: [IN-XX] }"))
    with pytest.raises(ConfigError, match=r"events-test\.yaml.*IN-XX"):
        CalendarIndex(load_calendar(folder))


def test_empty_scope_is_rejected(tmp_path: Path) -> None:
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: {}"))
    with pytest.raises(ConfigError, match="scope"):
        load_calendar(folder)


def test_occurrence_carries_event_fields(tmp_path: Path) -> None:
    index = build(
        tmp_path,
        EVENT.format(
            extra="scope: { national: true }\n    closure: partial\n    note: n1\n    lead_days: 5\n"
            "    tail_days: 2\n    priors: { sweets: { lift: 2.0 } }"
        ),
    )
    (occ,) = index.between("lucknow", date(2026, 11, 8), date(2026, 11, 8))
    assert (occ.type, occ.names, occ.closure, occ.note) == ("festival", {"en": "Fest"}, "partial", "n1")
    assert (occ.lead_days, occ.tail_days) == (5, 2)
    occ.priors["sweets"]["lift"] = 99.0  # must not leak back into the loaded calendar
    (again,) = index.between("lucknow", date(2026, 11, 8), date(2026, 11, 8))
    assert again.priors["sweets"]["lift"] == 2.0


def test_lead_and_tail_windows_are_not_applied_by_between(tmp_path: Path) -> None:
    index = build(
        tmp_path, EVENT.format(extra="scope: { national: true }\n    lead_days: 5\n    tail_days: 3")
    )
    assert index.between("lucknow", date(2026, 11, 1), date(2026, 11, 7)) == []
    assert index.between("lucknow", date(2026, 11, 9), date(2026, 11, 12)) == []


def test_recurring_defaults(tmp_path: Path) -> None:
    index = build(tmp_path, RECURRING.format(days="[5]"))
    (occ,) = index.between("lucknow", date(2026, 11, 1), date(2026, 11, 30))
    assert isinstance(occ, Occurrence)
    assert (occ.type, occ.confidence, occ.closure, occ.names) == (
        "observance",
        "published",
        "none",
        {"en": "Rec"},
    )


def test_day_31_is_skipped_in_a_30_day_month(tmp_path: Path) -> None:
    index = build(tmp_path, RECURRING.format(days="[30, 31]"))
    nov = [o.start for o in index.between("lucknow", date(2026, 11, 1), date(2026, 11, 30))]
    assert nov == [date(2026, 11, 30)]
    dec = [o.start for o in index.between("lucknow", date(2026, 12, 1), date(2026, 12, 31))]
    assert dec == [date(2026, 12, 30), date(2026, 12, 31)]


def test_range_spanning_december_into_january(tmp_path: Path) -> None:
    index = build(tmp_path, RECURRING.format(days="[1, 28]"))
    found = [o.start for o in index.between("lucknow", date(2026, 12, 15), date(2027, 1, 15))]
    assert found == [date(2026, 12, 28), date(2027, 1, 1)]


@pytest.mark.parametrize("days", ["[]", "[0]", "[32]", "[-1]", "[3, 3]"])
def test_recurring_days_are_validated(tmp_path: Path, days: str) -> None:
    folder = fixture_calendar(tmp_path, RECURRING.format(days=days))
    with pytest.raises(ConfigError, match="days"):
        load_calendar(folder)


def test_days_until_raises_key_error_when_nothing_upcoming(tmp_path: Path) -> None:
    index = build(tmp_path, EVENT.format(extra="scope: { national: true }"))
    with pytest.raises(KeyError, match="nothing"):
        index.days_until("nothing", DEMO_DAY, city="lucknow")


def test_duplicate_ids_across_files_name_both_files(tmp_path: Path) -> None:
    body = EVENT.format(extra="scope: { national: true }")
    folder = fixture_calendar(tmp_path, body)
    (folder / "events-other.yaml").write_text(body, encoding="utf-8")
    with pytest.raises(ConfigError, match=r"events-test\.yaml.*fest_2026|fest_2026.*events-test\.yaml"):
        load_calendar(folder)


def test_duplicate_city_across_states_is_rejected(tmp_path: Path) -> None:
    regions = REGIONS + "  - { code: IN-MH, name: Maharashtra, ui_locale: mr, cities: [lucknow] }\n"
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: { national: true }"), regions=regions)
    with pytest.raises(ConfigError, match=r"(?s)regions\.yaml.*lucknow"):
        load_calendar(folder)


def test_stray_yaml_in_calendar_dir_is_rejected(tmp_path: Path) -> None:
    folder = fixture_calendar(tmp_path, EVENT.format(extra="scope: { national: true }"))
    (folder / "event-2028.yaml").write_text("events: []\n", encoding="utf-8")
    with pytest.raises(ConfigError, match=r"event-2028\.yaml"):
        load_calendar(folder)


@pytest.mark.parametrize("field", ["source: ''", "names: { en: '' }"])
def test_blank_source_or_name_is_rejected(tmp_path: Path, field: str) -> None:
    text = EVENT.format(extra="scope: { national: true }")
    key = field.split(":")[0]
    text = "\n".join(line for line in text.splitlines() if not line.strip().startswith(key + ":"))
    text += f"    {field}\n"
    with pytest.raises(ConfigError, match="events-test.yaml"):
        load_calendar(fixture_calendar(tmp_path, text))
```

- [ ] **Step 4: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_config.py tests/test_calendar.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.core.config'`.

- [ ] **Step 5: Implement**

`backend/arth/core/config.py`:
```python
"""Settings and secrets from the environment, plus validated YAML config: policies, providers, calendar.

An invalid config file stops the app at boot with the file name in the error. API keys are read only here,
as SecretStr, from backend/.env; they never reach the web app, logs, spans or prompts (spec Part G0).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from arth.core.clock import IST
from arth.core.paths import BACKEND_DIR, CONFIG_DIR, DATA_DIR, PACKS_DIR
from arth.core.yamlconf import ConfigError, Strict, validate

Tier = Literal["R0", "R1", "R2", "R3", "R4"]
Mode = Literal["dev", "test", "demo", "prod"]
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
TOKEN_ENVS = {
    "ARTH_DIRECTOR_TOKEN": "director_token",
    "ARTH_DEVICE_TOKEN": "device_token",
    "ARTH_CONSOLE_TOKEN": "console_token",
}
KEY_ENVS = ("MISTRAL_API_KEY", "GROQ_API_KEY", "SARVAM_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY")


# ---- settings and secrets ------------------------------------------------------------------


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ARTH_", env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    mode: Mode = "dev"
    data_dir: Path = DATA_DIR
    config_dir: Path = CONFIG_DIR
    packs_dir: Path = PACKS_DIR
    clock_start: datetime = datetime(2026, 10, 29, 7, 45, tzinfo=IST)
    director_token: SecretStr = SecretStr("dev-director")
    device_token: SecretStr = SecretStr("dev-device")
    console_token: SecretStr = SecretStr("dev-console")
    cors_origins: list[str] = ["http://localhost:3000"]
    tick_interval_s: float = 1.0

    mistral_api_key: SecretStr | None = Field(default=None, validation_alias="MISTRAL_API_KEY")
    groq_api_key: SecretStr | None = Field(default=None, validation_alias="GROQ_API_KEY")
    sarvam_api_key: SecretStr | None = Field(default=None, validation_alias="SARVAM_API_KEY")
    langfuse_public_key: SecretStr | None = Field(default=None, validation_alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: SecretStr | None = Field(default=None, validation_alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", validation_alias="LANGFUSE_HOST")

    @field_validator(
        "mistral_api_key",
        "groq_api_key",
        "sarvam_api_key",
        "langfuse_public_key",
        "langfuse_secret_key",
        mode="before",
    )
    @classmethod
    def _blank_is_unset(cls, value: object) -> object:
        return None if isinstance(value, str) and not value.strip() else value

    @property
    def db_path(self) -> Path:
        return self.data_dir / "arth.db"

    def secret(self, env_name: str) -> SecretStr | None:
        secrets = {
            "MISTRAL_API_KEY": self.mistral_api_key,
            "GROQ_API_KEY": self.groq_api_key,
            "SARVAM_API_KEY": self.sarvam_api_key,
            "LANGFUSE_PUBLIC_KEY": self.langfuse_public_key,
            "LANGFUSE_SECRET_KEY": self.langfuse_secret_key,
        }
        if env_name not in secrets:
            raise ConfigError(f"unknown secret {env_name!r}")
        return secrets[env_name]


def check_auth_tokens(settings: Settings) -> None:
    """In prod the dev-* default surface tokens are refused. Messages name env vars, never values."""
    weak = sorted(
        env
        for env, attr in TOKEN_ENVS.items()
        if getattr(settings, attr).get_secret_value().startswith("dev-")
    )
    if weak and settings.mode == "prod":
        raise ConfigError(f"prod refuses the default dev-* auth tokens; set {', '.join(weak)}")


# ---- policies.yaml -------------------------------------------------------------------------


class Role(Strict):
    max_tier: Tier
    approve: list[Tier] = []
    allow: list[str] = []


class QuietHours(Strict):
    start: str
    end: str

    @field_validator("start", "end")
    @classmethod
    def _hhmm(cls, value: str) -> str:
        if not HHMM.match(value):
            raise ValueError(f"time {value!r} must be HH:MM, 24-hour (e.g. '21:30')")
        return value


class ContactCaps(Strict):
    marketing_per_patron_per_week: int = Field(ge=0)


class Reminders(Strict):
    per_patron_per_week: int = Field(ge=0)
    cadence_days: list[int]


class Growth(Strict):
    holdout_share: float = Field(ge=0, le=1)
    holdout_min: int = Field(ge=0)
    margin_floor: float = Field(ge=0, le=1)
    monthly_incentive_budget_paise: int = Field(ge=0)


class DiscreetMode(Strict):
    busy_hours: list[str]


class Attention(Strict):
    proactive_per_day: int = Field(ge=0)
    urgent_interrupts_per_day: int = Field(ge=0)


class Policies(Strict):
    tiers: dict[str, Tier]
    roles: dict[str, Role]
    quiet_hours: QuietHours
    contact_caps: ContactCaps
    reminders: Reminders
    growth: Growth
    expiry_alert_days: dict[str, int]
    discreet_mode: DiscreetMode
    attention: Attention
    forbid_offers_on_flags: list[str] = []

    @model_validator(mode="after")
    def _owner_is_top(self) -> Policies:
        owner = self.roles.get("owner")
        if owner is None or owner.max_tier != "R4":
            raise ValueError("an 'owner' role with max_tier R4 is required")
        return self


# ---- providers.yaml ------------------------------------------------------------------------

DataTag = Literal["merchant_ok_if_paid_plan", "synthetic_only", "synthetic_only_on_free_tier"]
REQUIRED_ROLES = {"llm.fast", "llm.large", "vision", "ocr", "stt", "tts", "translate", "guard", "persona"}


class Hop(Strict):
    provider: str
    model: str | None = None
    timeout_ms: int | None = Field(default=None, gt=0)
    json_mode: bool = Field(default=False, alias="json")
    langs: list[str] | None = None


class RoleChain(Strict):
    chain: list[Hop] = Field(min_length=1)


class Provider(Strict):
    api_key_env: str
    data_tag: DataTag
    rate: dict[str, int] = {}

    @field_validator("api_key_env")
    @classmethod
    def _known_env(cls, value: str) -> str:
        if value not in KEY_ENVS:
            raise ValueError(f"api_key_env {value!r} is not one of {', '.join(KEY_ENVS)}")
        return value


class Providers(Strict):
    roles: dict[str, RoleChain]
    providers: dict[str, Provider]

    @model_validator(mode="after")
    def _chains_are_resolvable(self) -> Providers:
        missing = REQUIRED_ROLES - self.roles.keys()
        if missing:
            raise ValueError(f"missing roles: {sorted(missing)}")
        for role, chain in self.roles.items():
            for hop in chain.chain:
                if hop.provider != "cassette" and hop.provider not in self.providers:
                    raise ValueError(f"role {role!r} uses unknown provider {hop.provider!r}")
                if hop.provider != "cassette" and not hop.model:
                    raise ValueError(f"role {role!r}: provider {hop.provider!r} needs a model id")
        return self

    def used(self) -> set[str]:
        return {
            hop.provider for chain in self.roles.values() for hop in chain.chain if hop.provider != "cassette"
        }


def provider_status(settings: Settings, providers: Providers) -> dict[str, bool]:
    """Which providers have a key configured. Values are booleans only, never the key."""
    return {
        name: settings.secret(p.api_key_env) is not None for name, p in sorted(providers.providers.items())
    }


def check_provider_keys(settings: Settings, providers: Providers) -> None:
    missing = sorted(
        providers.providers[name].api_key_env
        for name in providers.used()
        if settings.secret(providers.providers[name].api_key_env) is None
    )
    if missing and settings.mode == "prod":
        raise ConfigError(f"missing API keys in .env for prod: {', '.join(missing)}")


# ---- loaders -------------------------------------------------------------------------------


def load_policies(path: Path) -> Policies:
    return validate(Policies, path)


def load_providers(path: Path) -> Providers:
    return validate(Providers, path)
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_config.py tests/test_calendar.py -q`
Expected: all pass.

**Post-review additions (config/calendar).** After code review, Task 8 ships three modules instead of one. `backend/arth/core/yamlconf.py` holds `ConfigError`, `Strict` and `load_yaml`/`validate` (every loader uses `validate(model, path)`, so every failure names the file). `backend/arth/core/calendar.py` holds the calendar models, `Occurrence`, `CalendarIndex` and `load_calendar`. `backend/arth/core/config.py` keeps settings, policies and providers, and re-exports `ConfigError`, so `from arth.core.config import ConfigError, Settings, load_policies, load_providers, check_provider_keys, provider_status, Policies` still works. The three surface tokens (`ARTH_DIRECTOR_TOKEN`, `ARTH_DEVICE_TOKEN`, `ARTH_CONSOLE_TOKEN`) are `SecretStr`; `check_auth_tokens(settings)` makes `mode == "prod"` refuse the `dev-*` defaults, and the Task 13 auth dependency compares with `secrets.compare_digest` on `get_secret_value()`. `between()` does not apply `lead_days`/`tail_days`; `Occurrence` carries them so consumers widen their own windows. The code blocks above already reflect these changes; the test counts in Step 6 are now higher than listed.
If a repo-data test fails (e.g. Karva Chauth in Lucknow), the **calendar file** is wrong, not the code. Fix the YAML row and cite its source in the row's `source` field.

- [ ] **Step 7: Checkpoint**

Run: `python dev.py lint typecheck test`
Expected: all green.

---

### Task 9: Vertical-pack registry with tighten-only policies (T0.8)

**Files:**
- Create: `backend/arth/core/packs.py`, `backend/packs/kirana/manifest.yaml`
- Test: `backend/tests/test_packs.py`

- [ ] **Step 1: Write the kirana manifest**

`backend/packs/kirana/manifest.yaml` (spec Part D1):
```yaml
pack: kirana
version: 1
names: { en: Kirana / general store, hi: किराना / जनरल स्टोर, hi-Latn: Kirana / general store }
catalog:
  schema: sku
  fields: [mrp, price, cost, pack_size, unit, hsn, gst_rate, barcodes, category]
  units: [pcs, g, kg, ml, l, pack]
  loose_sale: true
  starter_catalog: catalog_starter.csv
stock: { batches: optional, expiry: optional, bom: false }
counter: { modes: [scan, tap, voice, search], tickets: false, appointments: false }
khata: { enabled: true }
levers:
  counter_hint: { min_habit_share: 0.6 }
  winback: { lapsing_rule: default }
  replenish: { categories: [atta, rice, oil, sugar, dal, milk, tea, detergent], cv_max: 0.4 }
  repeat_order: {}
  demand_capture: {}
  bundle_preorder: { margin_floor: 0.15 }
  credit_advisor: {}
  welcome: { coupon_paise: 2000, min_bill_paise: 20000, valid_days: 14 }
  offers: { types: [next_txn_cashback, instant_cashback, first_time_coupon, payment_count, item_coupon] }
  storefront: {}
  feedback: {}
calendar: [diwali, holi, eid_ul_fitr, raksha_bandhan, chhath, pongal, onam, durga_puja, christmas, wedding_season, salary_days]
charts: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
policies: { margin_floor: 0.15 }
templates: templates/
generator: generator.yaml
peer_cohort: kirana_by_city_tier_and_size
scenarios: [gupta_diwali, kirana_cold_start, kirana_monsoon_week, kirana_month_end]
```

- [ ] **Step 2: Write the failing tests**

`backend/tests/test_packs.py`:
```python
from pathlib import Path

import pytest

from arth.core.config import load_policies
from arth.core.packs import PackPolicyError, PackRegistry, UnknownPack, merge_policies
from arth.core.paths import CONFIG_DIR, PACKS_DIR

POLICIES = load_policies(CONFIG_DIR / "policies.yaml")
KIRANA = (PACKS_DIR / "kirana" / "manifest.yaml").read_text(encoding="utf-8")


def make_pack(root: Path, name: str, policies_line: str) -> None:
    folder = root / name
    folder.mkdir(parents=True)
    text = KIRANA.replace("pack: kirana", f"pack: {name}").replace(
        "policies: { margin_floor: 0.15 }", policies_line
    )
    (folder / "manifest.yaml").write_text(text, encoding="utf-8")


def test_repo_packs_load_and_expose_levers() -> None:
    registry = PackRegistry.load(PACKS_DIR, POLICIES)
    kirana = registry.get("kirana")
    assert kirana.catalog.schema_ == "sku"
    assert registry.lever("kirana", "replenish") == {
        "categories": ["atta", "rice", "oil", "sugar", "dal", "milk", "tea", "detergent"],
        "cv_max": 0.4,
    }
    assert registry.lever("kirana", "slot_fill") is None


def test_unknown_pack_raises() -> None:
    registry = PackRegistry.load(PACKS_DIR, POLICIES)
    with pytest.raises(UnknownPack):
        registry.get("bakery")


def test_tightening_is_merged() -> None:
    registry = PackRegistry.load(PACKS_DIR, POLICIES)
    tighter = registry.get("kirana").model_copy(update={"policies": {"margin_floor": 0.25}})
    merged = merge_policies(POLICIES, tighter)
    assert merged.growth.margin_floor == 0.25
    assert POLICIES.growth.margin_floor == 0.15, "core policies must not be mutated"


def test_loosening_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "loose", "policies: { margin_floor: 0.10 }")
    with pytest.raises(PackPolicyError, match="margin_floor"):
        PackRegistry.load(tmp_path, POLICIES)


def test_raising_contact_cap_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "spammy", "policies: { marketing_per_patron_per_week: 3 }")
    with pytest.raises(PackPolicyError, match="marketing_per_patron_per_week"):
        PackRegistry.load(tmp_path, POLICIES)


def test_unknown_policy_key_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "odd", "policies: { allow_r4_by_voice: true }")
    with pytest.raises(PackPolicyError, match="allow_r4_by_voice"):
        PackRegistry.load(tmp_path, POLICIES)


def test_forbid_offers_flags_are_added(tmp_path: Path) -> None:
    make_pack(tmp_path, "chemist", "policies: { forbid_offers_on_flags: [rx_required] }")
    registry = PackRegistry.load(tmp_path, POLICIES)
    assert registry.policies_for("chemist").forbid_offers_on_flags == ["rx_required"]


def test_merged_policies_out_of_bounds_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "wild", "policies: { margin_floor: 5 }")
    with pytest.raises(PackPolicyError, match=r"wild.*merged policies invalid"):
        PackRegistry.load(tmp_path, POLICIES)


@pytest.mark.parametrize("bad", ["abc", "true", ".nan", ".inf"])
def test_non_numeric_scalar_fails_boot(tmp_path: Path, bad: str) -> None:
    make_pack(tmp_path, "junk", f"policies: {{ margin_floor: {bad} }}")
    with pytest.raises(PackPolicyError, match=r"junk.*margin_floor must be a number"):
        PackRegistry.load(tmp_path, POLICIES)


@pytest.mark.parametrize("bad", ["rx_required", "[1, 2]", "['']", "{a: b}"])
def test_forbid_offers_must_be_list_of_strings(tmp_path: Path, bad: str) -> None:
    make_pack(tmp_path, "badlist", f"policies: {{ forbid_offers_on_flags: {bad} }}")
    with pytest.raises(PackPolicyError, match=r"badlist.*forbid_offers_on_flags"):
        PackRegistry.load(tmp_path, POLICIES)


def test_malformed_yaml_fails_boot(tmp_path: Path) -> None:
    folder = tmp_path / "broken"
    folder.mkdir()
    (folder / "manifest.yaml").write_text("pack: [unclosed\n  : :", encoding="utf-8")
    with pytest.raises(PackPolicyError, match=r"broken.*manifest.yaml"):
        PackRegistry.load(tmp_path, POLICIES)


def test_folder_name_must_match_pack(tmp_path: Path) -> None:
    make_pack(tmp_path, "alpha", "policies: { margin_floor: 0.2 }")
    (tmp_path / "alpha").rename(tmp_path / "beta")
    with pytest.raises(PackPolicyError, match="must match its folder name"):
        PackRegistry.load(tmp_path, POLICIES)


def test_schema_violation_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "extra", "policies: { margin_floor: 0.2 }\nsurprise: 1")
    with pytest.raises(PackPolicyError, match=r"extra/manifest.yaml"):
        PackRegistry.load(tmp_path, POLICIES)


def test_expiry_alert_days_is_a_floor(tmp_path: Path) -> None:
    core = POLICIES.expiry_alert_days["default"]
    make_pack(tmp_path / "low", "low", f"policies: {{ expiry_alert_days: {core - 1} }}")
    with pytest.raises(PackPolicyError, match="expiry_alert_days"):
        PackRegistry.load(tmp_path / "low", POLICIES)
    make_pack(tmp_path / "high", "high", f"policies: {{ expiry_alert_days: {core + 5} }}")
    registry = PackRegistry.load(tmp_path / "high", POLICIES)
    assert registry.policies_for("high").expiry_alert_days["default"] == core + 5
```

- [ ] **Step 3: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_packs.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.core.packs'`.

- [ ] **Step 4: Implement**

`backend/arth/core/packs.py`:
```python
"""Vertical packs (spec Part D). The core never branches on vertical; it asks this registry.

A pack can only TIGHTEN core policies. A pack that loosens one fails at boot.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Literal, NamedTuple

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from arth.core.config import Policies


class PackPolicyError(ValueError):
    """Any invalid pack (bad manifest, YAML, or a policy that loosens/is malformed)."""


class UnknownPack(KeyError):
    """No pack with that name is installed."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CatalogSpec(_Strict):
    schema_: Literal["sku", "menu", "medicine", "service"] = Field(alias="schema")
    fields: list[str]
    units: list[str]
    loose_sale: bool = False
    starter_catalog: str | None = None


class StockSpec(_Strict):
    batches: Literal["required", "optional", "off"]
    expiry: Literal["required", "optional", "off"]
    bom: bool = False


class CounterSpec(_Strict):
    modes: list[str]
    tickets: bool = False
    appointments: bool = False


class KhataSpec(_Strict):
    enabled: bool


class PackManifest(_Strict):
    pack: str
    version: int
    names: dict[str, str]
    catalog: CatalogSpec
    stock: StockSpec
    counter: CounterSpec
    khata: KhataSpec
    levers: dict[str, dict[str, Any]]
    calendar: list[str]
    charts: list[int]
    policies: dict[str, Any] = Field(default_factory=dict)
    templates: str
    generator: str
    peer_cohort: str
    scenarios: list[str]


class Rule(NamedTuple):
    path: tuple[str, ...]  # location inside Policies
    kind: Literal["floor", "cap"]  # floor: pack value must be >= core; cap: must be <= core


_SCALAR_RULES: dict[str, Rule] = {
    # Higher margin floor = fewer thin-margin offers.
    "margin_floor": Rule(("growth", "margin_floor"), "floor"),
    # Larger holdout share = more control group, i.e. more measurement and less exposure.
    "holdout_share": Rule(("growth", "holdout_share"), "floor"),
    # Lower contact cap = fewer marketing messages per patron.
    "marketing_per_patron_per_week": Rule(("contact_caps", "marketing_per_patron_per_week"), "cap"),
    # Higher expiry window = earlier alerts before stock expires.
    "expiry_alert_days": Rule(("expiry_alert_days", "default"), "floor"),
}
_LIST_ADD_ONLY = {"forbid_offers_on_flags"}


def _get(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    node: Any = data
    for key in path:
        node = node[key]
    return node


def _set(data: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    node: Any = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value


def merge_policies(core: Policies, manifest: PackManifest) -> Policies:
    name = manifest.pack
    merged = core.model_dump()
    for key, value in manifest.policies.items():
        if key in _SCALAR_RULES:
            rule = _SCALAR_RULES[key]
            if not (isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)):
                raise PackPolicyError(f"pack {name!r}: {key} must be a number, got {value!r}")
            current = _get(merged, rule.path)
            loosens = value < current if rule.kind == "floor" else value > current
            if loosens:
                raise PackPolicyError(
                    f"pack {name!r} loosens {key}: {value} vs core {current} "
                    f"(packs may only tighten policies)"
                )
            _set(merged, rule.path, value)
        elif key in _LIST_ADD_ONLY:
            if not (isinstance(value, list) and all(isinstance(v, str) and v for v in value)):
                raise PackPolicyError(
                    f"pack {name!r}: {key} must be a list of non-empty strings, got {value!r}"
                )
            merged[key] = sorted(set(merged[key]) | set(value))
        else:
            raise PackPolicyError(f"pack {name!r} sets unknown policy key {key!r}")
    try:
        return Policies.model_validate(merged)
    except ValidationError as exc:
        raise PackPolicyError(f"pack {name!r}: merged policies invalid: {exc}") from exc


class PackRegistry:
    def __init__(self, manifests: dict[str, PackManifest], policies: dict[str, Policies]) -> None:
        self._manifests = manifests
        self._policies = policies

    @classmethod
    def load(cls, packs_dir: Path, core: Policies) -> PackRegistry:
        manifests: dict[str, PackManifest] = {}
        policies: dict[str, Policies] = {}
        for path in sorted(packs_dir.glob("*/manifest.yaml")):
            try:
                manifest = PackManifest.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
            except yaml.YAMLError as exc:
                raise PackPolicyError(f"{path.parent.name}/manifest.yaml: invalid YAML: {exc}") from exc
            except ValidationError as exc:
                raise PackPolicyError(f"{path.parent.name}/manifest.yaml: {exc}") from exc
            if manifest.pack != path.parent.name:
                raise PackPolicyError(f"{path}: 'pack: {manifest.pack}' must match its folder name")
            manifests[manifest.pack] = manifest
            policies[manifest.pack] = merge_policies(core, manifest)
        return cls(manifests, policies)

    @property
    def names(self) -> list[str]:
        return sorted(self._manifests)

    def get(self, pack: str) -> PackManifest:
        try:
            return self._manifests[pack]
        except KeyError:
            raise UnknownPack(pack) from None

    def lever(self, pack: str, name: str) -> dict[str, Any] | None:
        return self.get(pack).levers.get(name)

    def policies_for(self, pack: str) -> Policies:
        self.get(pack)
        return self._policies[pack]
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_packs.py -q`
Expected: `7 passed`.

- [ ] **Step 6: Checkpoint**

Run: `python dev.py lint typecheck test`
Expected: all green.

---

### Task 10: Locales and formatting, with Python and web in lockstep (T0.9)

**Files:**
- Create: `backend/arth/core/i18n.py`, `contracts/fixtures/format_cases.json`, `frontend/lib/format.ts`
- Test: `backend/tests/test_i18n.py`, `frontend/tests/format.test.ts`

Both sides format money by hand (Indian grouping in every locale, digits optionally native), so they match exactly. Neither relies on CLDR versions that differ between Babel and Node's ICU. Dates use Babel or Intl only for the localised day and month names. One shared fixture file keeps the two in lockstep.

- [ ] **Step 1: Write the shared fixture**

`contracts/fixtures/format_cases.json`:
```json
{
  "_comment": "Money is byte-identical on both sides (Python backend/arth/core/i18n.py, TS frontend/lib/format.ts). Dates are formatted by whichever side renders them (frontend for screens, backend for messages/PDFs); Babel and Node ICU ship different CLDR versions, so non-Latin month/weekday names may differ. Dates are therefore only required to be byte-identical for en and hi-Latn; each side separately tests that the other locales contain the day number and a non-empty weekday and month.",
  "locales": {
    "hi": { "lakh": "लाख", "crore": "करोड़", "nativeZero": 2406, "babel": "hi_IN", "intl": "hi-IN" },
    "en": { "lakh": "lakh", "crore": "crore", "nativeZero": null, "babel": "en_IN", "intl": "en-IN" },
    "hi-Latn": { "lakh": "lakh", "crore": "crore", "nativeZero": null, "babel": "en_IN", "intl": "en-IN" },
    "mr": { "lakh": "लाख", "crore": "कोटी", "nativeZero": 2406, "babel": "mr_IN", "intl": "mr-IN" },
    "ta": { "lakh": "லட்சம்", "crore": "கோடி", "nativeZero": 3046, "babel": "ta_IN", "intl": "ta-IN" },
    "bn": { "lakh": "লাখ", "crore": "কোটি", "nativeZero": 2534, "babel": "bn_IN", "intl": "bn-IN" },
    "gu": { "lakh": "લાખ", "crore": "કરોડ", "nativeZero": 2790, "babel": "gu_IN", "intl": "gu-IN" },
    "te": { "lakh": "లక్ష", "crore": "కోటి", "nativeZero": 3174, "babel": "te_IN", "intl": "te-IN" }
  },
  "money": [
    { "paise": 11240000, "locale": "en", "expected": "₹1,12,400" },
    { "paise": 11240000, "locale": "hi", "expected": "₹1,12,400" },
    { "paise": 11240000, "locale": "hi-Latn", "expected": "₹1,12,400" },
    { "paise": 11240000, "locale": "mr", "expected": "₹1,12,400" },
    { "paise": 11240000, "locale": "ta", "expected": "₹1,12,400" },
    { "paise": 11240000, "locale": "bn", "expected": "₹1,12,400" },
    { "paise": 11240000, "locale": "gu", "expected": "₹1,12,400" },
    { "paise": 11240000, "locale": "te", "expected": "₹1,12,400" },
    { "paise": 6200, "locale": "hi-Latn", "expected": "₹62" },
    { "paise": 6250, "locale": "en", "expected": "₹62.50" },
    { "paise": 9000, "locale": "ta", "expected": "₹90" },
    { "paise": 5, "locale": "en", "expected": "₹0.05" },
    { "paise": 10005, "locale": "hi", "expected": "₹100.05" },
    { "paise": 0, "locale": "en", "expected": "₹0" },
    { "paise": 0, "locale": "te", "compact": true, "expected": "₹0" },
    { "paise": 845000, "locale": "en", "compact": true, "expected": "₹8,450" },
    { "paise": 9999900, "locale": "en", "compact": true, "expected": "₹99,999" },
    { "paise": 11000000, "locale": "en", "compact": true, "expected": "₹1.1 lakh" },
    { "paise": 11000000, "locale": "hi-Latn", "compact": true, "expected": "₹1.1 lakh" },
    { "paise": 11000000, "locale": "hi", "compact": true, "expected": "₹1.1 लाख" },
    { "paise": 11000000, "locale": "mr", "compact": true, "expected": "₹1.1 लाख" },
    { "paise": 11000000, "locale": "ta", "compact": true, "expected": "₹1.1 லட்சம்" },
    { "paise": 11000000, "locale": "bn", "compact": true, "expected": "₹1.1 লাখ" },
    { "paise": 11000000, "locale": "gu", "compact": true, "expected": "₹1.1 લાખ" },
    { "paise": 11000000, "locale": "te", "compact": true, "expected": "₹1.1 లక్ష" },
    { "paise": 20000000, "locale": "ta", "compact": true, "expected": "₹2 லட்சம்" },
    { "paise": 2500000000, "locale": "en", "compact": true, "expected": "₹2.5 crore" },
    { "paise": 2500000000, "locale": "hi-Latn", "compact": true, "expected": "₹2.5 crore" },
    { "paise": 2500000000, "locale": "hi", "compact": true, "expected": "₹2.5 करोड़" },
    { "paise": 2500000000, "locale": "mr", "compact": true, "expected": "₹2.5 कोटी" },
    { "paise": 2500000000, "locale": "ta", "compact": true, "expected": "₹2.5 கோடி" },
    { "paise": 2500000000, "locale": "bn", "compact": true, "expected": "₹2.5 কোটি" },
    { "paise": 2500000000, "locale": "gu", "compact": true, "expected": "₹2.5 કરોડ" },
    { "paise": 2500000000, "locale": "te", "compact": true, "expected": "₹2.5 కోటి" },
    { "paise": 999499900, "locale": "en", "compact": true, "expected": "₹99.9 lakh" },
    { "paise": 999500000, "locale": "en", "compact": true, "expected": "₹1 crore" },
    { "paise": 999999900, "locale": "en", "compact": true, "expected": "₹1 crore" },
    { "paise": 999999900, "locale": "hi", "compact": true, "expected": "₹1 करोड़" },
    { "paise": 12345678900, "locale": "en", "compact": true, "expected": "₹12.3 crore" },
    { "paise": 1234500000000, "locale": "en", "compact": true, "expected": "₹1,234.5 crore" },
    { "paise": 1234500000000, "locale": "hi", "compact": true, "native": true, "expected": "₹१,२३४.५ करोड़" },
    { "paise": -11000000, "locale": "en", "compact": true, "expected": "-₹1.1 lakh" },
    { "paise": -2500000000, "locale": "hi", "compact": true, "expected": "-₹2.5 करोड़" },
    { "paise": 11240000, "locale": "hi", "native": true, "expected": "₹१,१२,४००" },
    { "paise": 11240000, "locale": "mr", "native": true, "expected": "₹१,१२,४००" },
    { "paise": 11240000, "locale": "bn", "native": true, "expected": "₹১,১২,৪০০" },
    { "paise": 11240000, "locale": "ta", "native": true, "expected": "₹௧,௧௨,௪௦௦" },
    { "paise": 11240000, "locale": "gu", "native": true, "expected": "₹૧,૧૨,૪૦૦" },
    { "paise": 11240000, "locale": "te", "native": true, "expected": "₹౧,౧౨,౪౦౦" },
    { "paise": 11240000, "locale": "en", "native": true, "expected": "₹1,12,400" },
    { "paise": 11000000, "locale": "hi", "compact": true, "native": true, "expected": "₹१.१ लाख" },
    { "paise": -500000, "locale": "en", "expected": "-₹5,000" },
    { "paise": 999400000, "locale": "en", "compact": true, "expected": "₹99.9 lakh" },
    { "paise": 12499900, "locale": "en", "compact": true, "expected": "₹1.2 lakh" },
    { "paise": 12500000, "locale": "en", "compact": true, "expected": "₹1.3 lakh" },
    { "paise": -12500000, "locale": "en", "compact": true, "expected": "-₹1.3 lakh" },
    { "paise": 2500000000, "locale": "ta", "compact": true, "native": true, "expected": "₹௨.௫ கோடி" },
    { "paise": 12345, "locale": "en", "compact": true, "expected": "₹123.45" }
  ],
  "dates": [
    { "date": "2026-10-29", "locale": "en", "expected": "Thu, 29 Oct" },
    { "date": "2026-10-29", "locale": "hi-Latn", "expected": "Thu, 29 Oct" },
    { "date": "2026-11-05", "locale": "en", "expected": "Thu, 5 Nov" },
    { "date": "2026-11-05", "locale": "hi-Latn", "expected": "Thu, 5 Nov" }
  ]
}
```

- [ ] **Step 2: Write the failing tests**

`backend/tests/test_i18n.py`:
```python
import json
from datetime import date

import pytest

from arth.core.i18n import (
    BABEL_LOCALE,
    LAKH_CRORE,
    LOCALES,
    NATIVE_ZERO,
    LocaleError,
    format_date,
    format_money,
    group_indian,
    to_native_digits,
)
from arth.core.paths import CONTRACTS_DIR

CASES = json.loads((CONTRACTS_DIR / "fixtures" / "format_cases.json").read_text(encoding="utf-8"))

SPEC = CASES["locales"]
NON_LATIN = tuple(loc for loc, row in SPEC.items() if row["nativeZero"] is not None)


def _case_id(c: dict) -> str:
    compact = "-compact" if c.get("compact") else ""
    native = "-native" if c.get("native") else ""
    return f"{c['locale']}-{c['paise']}{compact}{native}"


@pytest.mark.parametrize("case", CASES["money"], ids=_case_id)
def test_money_matches_shared_fixture(case: dict) -> None:
    got = format_money(
        case["paise"], case["locale"], compact=case.get("compact", False), native=case.get("native", False)
    )
    assert got == case["expected"]


@pytest.mark.parametrize("case", CASES["dates"], ids=lambda c: c["locale"])
def test_dates_match_shared_fixture(case: dict) -> None:
    assert format_date(date.fromisoformat(case["date"]), case["locale"]) == case["expected"]


def test_code_tables_equal_fixture_locales_section() -> None:
    assert list(LOCALES) == list(SPEC)
    assert set(LAKH_CRORE) == set(BABEL_LOCALE) == set(SPEC)
    for locale, row in SPEC.items():
        assert LAKH_CRORE[locale] == (row["lakh"], row["crore"])
        assert BABEL_LOCALE[locale] == row["babel"]
        assert NATIVE_ZERO.get(locale) == row["nativeZero"]
    assert set(NATIVE_ZERO) == set(NON_LATIN)


@pytest.mark.parametrize("locale", LOCALES)
def test_fixture_covers_every_locale(locale: str) -> None:
    mine = [c for c in CASES["money"] if c["locale"] == locale]
    lakh, crore = SPEC[locale]["lakh"], SPEC[locale]["crore"]
    assert any(not c.get("compact") and not c.get("native") for c in mine)
    assert any(c.get("compact") and c["expected"].endswith(f" {lakh}") for c in mine)
    assert any(c.get("compact") and c["expected"].endswith(f" {crore}") for c in mine)
    if locale in NON_LATIN:
        assert any(c.get("native") for c in mine)


@pytest.mark.parametrize("locale", LOCALES)
def test_date_has_weekday_day_and_month(locale: str) -> None:
    # Non-Latin names may differ from the web build (CLDR drift); only structure is asserted.
    weekday, rest = format_date(date(2026, 10, 29), locale).split(", ", 1)
    assert weekday
    assert rest.startswith("29 ")
    assert rest[3:].strip()


@pytest.mark.parametrize("locale", NON_LATIN)
def test_native_date_uses_native_digits(locale: str) -> None:
    assert to_native_digits("29", locale) in format_date(date(2026, 10, 29), locale, native=True)


def test_date_single_digit_day_has_no_padding() -> None:
    assert format_date(date(2026, 11, 5), "en").split(", ", 1)[1].startswith("5 ")


def test_unknown_locale_is_rejected() -> None:
    with pytest.raises(LocaleError, match="unsupported locale 'fr'"):
        format_money(100, "fr")
    with pytest.raises(LocaleError):
        format_money(100_000_00, "fr", compact=True)
    with pytest.raises(LocaleError):
        format_date(date(2026, 10, 29), "fr")
    with pytest.raises(LocaleError):
        to_native_digits("29", "fr")


@pytest.mark.parametrize("bad", [True, 1.5, 100.0, "100", None])
def test_money_requires_int(bad: object) -> None:
    with pytest.raises(TypeError, match="paise must be an int"):
        format_money(bad, "en")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("n", "expected"),
    [(0, "0"), (999, "999"), (1000, "1,000"), (100000, "1,00,000"), (12345678, "1,23,45,678")],
)
def test_group_indian(n: int, expected: str) -> None:
    assert group_indian(n) == expected
```

`frontend/tests/format.test.ts`:
```ts
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import {
  formatDate,
  formatMoney,
  INTL_LOCALE,
  isLocale,
  LAKH_CRORE,
  LOCALES,
  LocaleError,
  NATIVE_ZERO,
  toNativeDigits,
  type Locale,
} from '../lib/format';

type MoneyCase = { paise: number; locale: Locale; compact?: boolean; native?: boolean; expected: string };
type DateCase = { date: string; locale: Locale; expected: string };
type LocaleSpec = {
  lakh: string;
  crore: string;
  nativeZero: number | null;
  babel: string;
  intl: string;
};
const cases = JSON.parse(
  readFileSync(
    fileURLToPath(new URL('../../contracts/fixtures/format_cases.json', import.meta.url)),
    'utf-8',
  ),
) as { locales: Record<Locale, LocaleSpec>; money: MoneyCase[]; dates: DateCase[] };

const SPEC = cases.locales;
const NON_LATIN = LOCALES.filter((l) => SPEC[l].nativeZero !== null);
const day = new Date('2026-10-29T12:00:00+05:30');

describe('formatMoney matches the shared fixture', () => {
  it.each(cases.money)('$locale $paise compact=$compact native=$native → $expected', (c) => {
    expect(formatMoney(c.paise, c.locale, { compact: c.compact, native: c.native })).toBe(c.expected);
  });
});

describe('formatDate matches the shared fixture', () => {
  it.each(cases.dates)('$locale $date → $expected', (c) => {
    expect(formatDate(new Date(`${c.date}T12:00:00+05:30`), c.locale)).toBe(c.expected);
  });
});

describe('dates in every locale (structure only; names may differ from Babel)', () => {
  it.each([...LOCALES])('%s has weekday, day 29 and month', (locale) => {
    const [weekday, rest] = formatDate(day, locale).split(/, (.*)/s);
    expect(weekday).toBeTruthy();
    expect(rest.startsWith('29 ')).toBe(true);
    expect(rest.slice(3).trim()).not.toBe('');
  });
  it.each(NON_LATIN)('%s native date uses native digits', (locale) => {
    expect(formatDate(day, locale, { native: true })).toContain(toNativeDigits('29', locale));
  });
});

describe('fixture coverage', () => {
  it.each([...LOCALES])('%s has plain, lakh, crore (and native) cases', (locale) => {
    const mine = cases.money.filter((c) => c.locale === locale);
    const { lakh, crore } = SPEC[locale];
    expect(mine.some((c) => !c.compact && !c.native)).toBe(true);
    expect(mine.some((c) => c.compact && c.expected.endsWith(` ${lakh}`))).toBe(true);
    expect(mine.some((c) => c.compact && c.expected.endsWith(` ${crore}`))).toBe(true);
    if (NON_LATIN.includes(locale)) expect(mine.some((c) => c.native)).toBe(true);
  });
});

describe('code tables equal the fixture locales section', () => {
  it('lists the same locales in the same order', () => {
    expect([...LOCALES]).toEqual(Object.keys(SPEC));
  });
  it.each(Object.keys(SPEC) as Locale[])('%s', (locale) => {
    const row = SPEC[locale];
    expect(LAKH_CRORE[locale]).toEqual([row.lakh, row.crore]);
    expect(NATIVE_ZERO[locale] ?? null).toBe(row.nativeZero);
    expect(INTL_LOCALE[locale]).toBe(row.intl);
  });
});

describe('dates: day edges', () => {
  it('does not pad a single-digit day', () => {
    expect(formatDate(new Date('2026-11-05T12:00:00+05:30'), 'en')).toBe('Thu, 5 Nov');
  });
  it('uses the IST calendar day for a late-evening instant', () => {
    expect(formatDate(new Date('2026-10-29T23:30:00+05:30'), 'en')).toBe('Thu, 29 Oct');
  });
});

describe('guards', () => {
  it('isLocale narrows known locales only', () => {
    expect(isLocale('hi-Latn')).toBe(true);
    expect(isLocale('fr')).toBe(false);
    expect(isLocale('toString')).toBe(false);
  });
  it('rejects unknown locales everywhere', () => {
    const bad = 'fr' as Locale;
    expect(() => formatMoney(100, bad)).toThrow(LocaleError);
    expect(() => formatMoney(100, bad)).toThrow("unsupported locale 'fr'");
    expect(() => formatMoney(10_000_000, bad, { compact: true })).toThrow(LocaleError);
    expect(() => formatDate(day, bad)).toThrow(LocaleError);
    expect(() => toNativeDigits('29', bad)).toThrow(LocaleError);
    expect(() => formatMoney(100, 'toString' as Locale)).toThrow(LocaleError);
  });
  it.each([1.5, Number.NaN, Number.POSITIVE_INFINITY, 2 ** 53])('rejects non-safe-integer paise %s', (n) => {
    expect(() => formatMoney(n, 'en')).toThrow(RangeError);
    expect(() => formatMoney(n, 'en')).toThrow('paise must be a safe integer');
  });
});
```

- [ ] **Step 3: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_i18n.py -q` → FAIL (`No module named 'arth.core.i18n'`).
Run: `pnpm --filter frontend run test` → FAIL (`Cannot find module '../lib/format'`).

- [ ] **Step 4: Implement the Python side**

`backend/arth/core/i18n.py`:
```python
"""Locales and formatting shared with the web app (spec Part I6).

Money always uses Indian grouping (₹1,12,400), whatever the locale; digits are Latin unless
`native=True`. Keep this file in lockstep with frontend/lib/format.ts via
contracts/fixtures/format_cases.json.

Contract: money is byte-identical on both sides. Dates are rendered by whichever side shows them
(frontend for screens, backend for messages/PDFs) and are only required to be byte-identical for
`en` and `hi-Latn`: Babel and Node ICU ship different CLDR versions, so non-Latin month/weekday
names may differ. Other locales are tested per side for structure (weekday, day, month) only.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from types import MappingProxyType
from typing import Final, Literal, get_args

from babel.dates import format_date as _babel_format_date

Locale = Literal["hi", "en", "hi-Latn", "mr", "ta", "bn", "gu", "te"]
LOCALES: Final[tuple[str, ...]] = get_args(Locale)

BABEL_LOCALE: Final[Mapping[str, str]] = MappingProxyType(
    {
        "hi": "hi_IN",
        "en": "en_IN",
        "hi-Latn": "en_IN",
        "mr": "mr_IN",
        "ta": "ta_IN",
        "bn": "bn_IN",
        "gu": "gu_IN",
        "te": "te_IN",
    }
)
NATIVE_ZERO: Final[Mapping[str, int]] = MappingProxyType(
    {"hi": 0x0966, "mr": 0x0966, "bn": 0x09E6, "ta": 0x0BE6, "gu": 0x0AE6, "te": 0x0C66}
)
LAKH_CRORE: Final[Mapping[str, tuple[str, str]]] = MappingProxyType(
    {
        "en": ("lakh", "crore"),
        "hi-Latn": ("lakh", "crore"),
        "hi": ("लाख", "करोड़"),
        "mr": ("लाख", "कोटी"),
        "ta": ("லட்சம்", "கோடி"),
        "bn": ("লাখ", "কোটি"),
        "gu": ("લાખ", "કરોડ"),
        "te": ("లక్ష", "కోటి"),
    }
)
LAKH: Final = 100_000
CRORE: Final = 10_000_000


class LocaleError(ValueError):
    """Unsupported locale."""


def _check(locale: str) -> None:
    if locale not in LOCALES:
        raise LocaleError(f"unsupported locale {locale!r}; use one of {', '.join(LOCALES)}")


def group_indian(n: int) -> str:
    digits = str(n)
    if len(digits) <= 3:
        return digits
    head, tail = digits[:-3], digits[-3:]
    pairs: list[str] = []
    while len(head) > 2:
        pairs.insert(0, head[-2:])
        head = head[:-2]
    if head:
        pairs.insert(0, head)
    return ",".join(pairs) + "," + tail


def to_native_digits(text: str, locale: str) -> str:
    _check(locale)
    zero = NATIVE_ZERO.get(locale)
    if zero is None:
        return text
    return "".join(chr(zero + int(ch)) if ch in "0123456789" else ch for ch in text)


def _compact_round(rupees: int) -> tuple[int, int]:
    """Round whole rupees (>= 1 lakh) half-up to one decimal of lakh or crore.

    Returns (tenths, unit). Compact output deliberately drops paise: at lakh scale they are noise.
    99.95+ lakh would print as "100 lakh", so it is promoted to crore instead.
    """
    unit = CRORE if rupees >= CRORE else LAKH
    tenths = (rupees * 10 + unit // 2) // unit
    if unit == LAKH and tenths >= 1000:
        unit = CRORE
        tenths = (rupees * 10 + unit // 2) // unit
    return tenths, unit


def format_money(paise: int, locale: str, *, compact: bool = False, native: bool = False) -> str:
    if isinstance(paise, bool) or not isinstance(paise, int):
        raise TypeError("paise must be an int")
    _check(locale)
    sign = "-" if paise < 0 else ""
    rupees, rest = divmod(abs(paise), 100)
    suffix = ""
    if compact and rupees >= LAKH:
        tenths, unit = _compact_round(rupees)
        word = LAKH_CRORE[locale][1 if unit == CRORE else 0]
        whole, frac = divmod(tenths, 10)
        text = group_indian(whole) + (f".{frac}" if frac else "")
        suffix = f" {word}"
    else:
        text = group_indian(rupees) + (f".{rest:02d}" if rest else "")
    if native:
        text = to_native_digits(text, locale)
    return f"{sign}₹{text}{suffix}"


def format_date(value: date, locale: str, *, native: bool = False) -> str:
    """Short weekday, day and month: 'Thu, 29 Oct'. Same composition on the web side."""
    _check(locale)
    babel_locale = BABEL_LOCALE[locale]
    weekday = _babel_format_date(value, format="EEE", locale=babel_locale)
    month = _babel_format_date(value, format="MMM", locale=babel_locale)
    text = f"{weekday}, {value.day} {month}"
    return to_native_digits(text, locale) if native else text
```

- [ ] **Step 5: Implement the web side**

`frontend/lib/format.ts`:
```ts
// Keep in lockstep with backend/arth/core/i18n.py via contracts/fixtures/format_cases.json.
// Contract: money is byte-identical on both sides. Dates are rendered by whichever side shows them
// (frontend for screens, backend for messages/PDFs) and are only required to be byte-identical for
// `en` and `hi-Latn`: Node ICU and Babel ship different CLDR versions, so non-Latin month/weekday
// names may differ. Other locales are tested per side for structure (weekday, day, month) only.
export const LOCALES = ['hi', 'en', 'hi-Latn', 'mr', 'ta', 'bn', 'gu', 'te'] as const;
export type Locale = (typeof LOCALES)[number];

export const INTL_LOCALE: Readonly<Record<Locale, string>> = Object.freeze({
  hi: 'hi-IN',
  en: 'en-IN',
  'hi-Latn': 'en-IN',
  mr: 'mr-IN',
  ta: 'ta-IN',
  bn: 'bn-IN',
  gu: 'gu-IN',
  te: 'te-IN',
});
export const NATIVE_ZERO: Readonly<Partial<Record<Locale, number>>> = Object.freeze({
  hi: 0x0966,
  mr: 0x0966,
  bn: 0x09e6,
  ta: 0x0be6,
  gu: 0x0ae6,
  te: 0x0c66,
});
export const LAKH_CRORE: Readonly<Record<Locale, readonly [string, string]>> = Object.freeze({
  en: ['lakh', 'crore'],
  'hi-Latn': ['lakh', 'crore'],
  hi: ['लाख', 'करोड़'],
  mr: ['लाख', 'कोटी'],
  ta: ['லட்சம்', 'கோடி'],
  bn: ['লাখ', 'কোটি'],
  gu: ['લાખ', 'કરોડ'],
  te: ['లక్ష', 'కోటి'],
});
const LAKH = 100_000;
const CRORE = 10_000_000;

export class LocaleError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'LocaleError';
  }
}

export function isLocale(x: string): x is Locale {
  return (LOCALES as readonly string[]).includes(x);
}

function assertLocale(locale: string): asserts locale is Locale {
  if (!isLocale(locale)) {
    throw new LocaleError(`unsupported locale '${locale}'; use one of ${LOCALES.join(', ')}`);
  }
}

// Round whole rupees (>= 1 lakh) half-up to one decimal of lakh or crore. Returns [tenths, unit].
// Compact output deliberately drops paise: at lakh scale they are noise.
// 99.95+ lakh would print as "100 lakh", so it is promoted to crore instead.
function compactRound(rupees: number): [number, number] {
  let unit = rupees >= CRORE ? CRORE : LAKH;
  let tenths = Math.floor((rupees * 10 + Math.floor(unit / 2)) / unit);
  if (unit === LAKH && tenths >= 1000) {
    unit = CRORE;
    tenths = Math.floor((rupees * 10 + Math.floor(unit / 2)) / unit);
  }
  return [tenths, unit];
}

export function groupIndian(n: number): string {
  const digits = String(n);
  if (digits.length <= 3) return digits;
  let head = digits.slice(0, -3);
  const tail = digits.slice(-3);
  const pairs: string[] = [];
  while (head.length > 2) {
    pairs.unshift(head.slice(-2));
    head = head.slice(0, -2);
  }
  if (head) pairs.unshift(head);
  return `${pairs.join(',')},${tail}`;
}

export function toNativeDigits(text: string, locale: Locale): string {
  assertLocale(locale);
  const zero = NATIVE_ZERO[locale];
  if (zero === undefined) return text;
  return text.replace(/[0-9]/g, (d) => String.fromCodePoint(zero + Number(d)));
}

export function formatMoney(
  paise: number,
  locale: Locale,
  opts: { compact?: boolean; native?: boolean } = {},
): string {
  assertLocale(locale);
  if (!Number.isSafeInteger(paise)) throw new RangeError('paise must be a safe integer');
  const sign = paise < 0 ? '-' : '';
  const abs = Math.abs(paise);
  const rupees = Math.floor(abs / 100);
  const rest = abs % 100;
  let text: string;
  let suffix = '';
  if (opts.compact && rupees >= LAKH) {
    const [tenths, unit] = compactRound(rupees);
    const word = LAKH_CRORE[locale][unit === CRORE ? 1 : 0];
    const frac = tenths % 10;
    text = groupIndian(Math.floor(tenths / 10)) + (frac ? `.${frac}` : '');
    suffix = ` ${word}`;
  } else {
    text = groupIndian(rupees) + (rest ? `.${String(rest).padStart(2, '0')}` : '');
  }
  if (opts.native) text = toNativeDigits(text, locale);
  return `${sign}₹${text}${suffix}`;
}

const dateFormats = new Map<Locale, Intl.DateTimeFormat>();

function dateFormat(locale: Locale): Intl.DateTimeFormat {
  let fmt = dateFormats.get(locale);
  if (!fmt) {
    fmt = new Intl.DateTimeFormat(INTL_LOCALE[locale], {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      timeZone: 'Asia/Kolkata',
      numberingSystem: 'latn',
    });
    dateFormats.set(locale, fmt);
  }
  return fmt;
}

export function formatDate(value: Date, locale: Locale, opts: { native?: boolean } = {}): string {
  assertLocale(locale);
  const parts = dateFormat(locale).formatToParts(value);
  const get = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value ?? '';
  const text = `${get('weekday')}, ${get('day')} ${get('month')}`;
  return opts.native ? toNativeDigits(text, locale) : text;
}
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_i18n.py -q` → all pass.
Run: `pnpm --filter frontend run test` → `format.test.ts` all pass.
If an English weekday or month abbreviation differs between Babel and Node's ICU (e.g. "Sept" vs "Sep"), fix the **fixture** to a date that avoids the ambiguity. Don't special-case the code.

- [ ] **Step 7: Checkpoint**

Run: `python dev.py lint typecheck test`
Expected: all green.

---

### Task 11: Spans and the SSE stream (T0.10)

**Files:**
- Create: `backend/arth/core/spans.py`, `backend/arth/api/__init__.py`, `backend/arth/api/stream.py`
- Test: `backend/tests/test_spans.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_spans.py`:
```python
import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from time import perf_counter
from typing import Any

import pytest
from sqlalchemy import select

from arth.api.stream import span_events
from arth.core.clock import IST, SimClock
from arth.core.db import Database
from arth.core.spans import Span, SpanBus
from arth.core.tables import spans

START = datetime(2026, 10, 29, 7, 45, tzinfo=IST)


def make_span(n: int) -> Span:
    return Span(
        id=f"span_{n}",
        trace_id="trace_x",
        parent_id=None,
        kind="tool",
        name=f"s{n}",
        start_at="2026-10-29T02:15:00.000000Z",
        dur_ms=1.0,
        mode="none",
        cost_paise=0,
    )


class BrokenDb:
    @asynccontextmanager
    async def write(self) -> AsyncIterator[Any]:
        raise RuntimeError("disk on fire")
        yield  # pragma: no cover


async def test_span_reaches_subscriber_within_200ms_and_is_persisted(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    queue = bus.subscribe()
    started = perf_counter()
    async with bus.span("tool", "analytics.sales", mode="live") as attrs:
        attrs["rows"] = 3
        attrs["cost_paise"] = 2
    span = await asyncio.wait_for(queue.get(), timeout=0.2)
    assert perf_counter() - started < 0.2
    assert (span.kind, span.name, span.mode, span.cost_paise) == ("tool", "analytics.sales", "live", 2)
    assert span.attrs == {"rows": 3}
    assert span.status == "ok"
    assert span.start_at == "2026-10-29T02:15:00.000000Z"
    await bus.flush()
    async with db.read() as conn:
        row = (await conn.execute(select(spans))).mappings().one()
    assert json.loads(row["attrs"]) == {"rows": 3, "status": "ok"}


async def test_persisted_row_has_cost_mode_parent_and_duration(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    async with bus.span("tool", "x", parent_id="span_parent", mode="replay") as attrs:
        attrs["cost_paise"] = 7
    await bus.flush()
    async with db.read() as conn:
        row = (await conn.execute(select(spans))).mappings().one()
    assert (row["cost_paise"], row["mode"], row["parent_id"]) == (7, "replay", "span_parent")
    assert row["dur_ms"] >= 0


async def test_child_span_shares_trace(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    queue = bus.subscribe()
    async with bus.span("turn", "turn") as parent:
        async with bus.span("tool", "x", trace_id=parent.trace_id, parent_id=parent.span_id):
            pass
    child, outer = await queue.get(), await queue.get()
    assert child.trace_id == outer.trace_id
    assert child.parent_id == outer.id


async def test_body_error_is_recorded_and_propagates(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    queue = bus.subscribe()
    with pytest.raises(ValueError, match="boom"):
        async with bus.span("tool", "bad"):
            raise ValueError("boom")
    span = queue.get_nowait()
    assert span.status == "error"
    assert span.attrs["error"] == "ValueError: boom"
    await bus.flush()
    async with db.read() as conn:
        row = (await conn.execute(select(spans))).mappings().one()
    stored = json.loads(row["attrs"])
    assert stored["status"] == "error"
    assert stored["error"] == "ValueError: boom"


async def test_cancellation_is_recorded_and_propagates() -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe()

    async def body() -> None:
        async with bus.span("tool", "slow"):
            await asyncio.sleep(10)

    task = asyncio.ensure_future(body())
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    span = queue.get_nowait()
    assert span.status == "cancelled"
    assert span.attrs["cancelled"] is True


async def test_bad_cost_and_unserialisable_attrs_do_not_break_caller(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    async with bus.span("tool", "weird") as attrs:
        attrs["cost_paise"] = "lots"
        attrs["ratio"] = float("nan")
        attrs["obj"] = object()
    await bus.flush()
    async with db.read() as conn:
        rows = (await conn.execute(select(spans))).mappings().all()
    assert len(rows) == 1
    assert rows[0]["cost_paise"] == 0
    json.loads(rows[0]["attrs"])  # valid JSON, no NaN literal


async def test_persistence_failure_does_not_break_caller_or_mask_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    bus = SpanBus(SimClock(START), BrokenDb())  # type: ignore[arg-type]
    queue = bus.subscribe()
    async with bus.span("tool", "ok"):
        pass
    with pytest.raises(ValueError, match="body failed"):
        async with bus.span("tool", "bad"):
            raise ValueError("body failed")
    with caplog.at_level(logging.ERROR):
        await bus.flush()
        await bus.aclose()
    assert queue.qsize() == 2
    assert "disk on fire" in caplog.text


async def test_background_task_batches_and_aclose_flushes(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    await bus.start()
    for n in range(120):
        await bus.emit(make_span(n))
    await bus.aclose()
    async with db.read() as conn:
        count = len((await conn.execute(select(spans.c.id))).all())
    assert count == 120


async def test_flush_without_started_task_persists_inline(db: Database) -> None:
    bus = SpanBus(SimClock(START), db)
    await bus.emit(make_span(1))
    await bus.flush()
    async with db.read() as conn:
        assert len((await conn.execute(select(spans.c.id))).all()) == 1


async def test_bus_without_db_flush_and_close_are_noops() -> None:
    bus = SpanBus(SimClock(START))
    await bus.start()
    await bus.emit(make_span(1))
    await bus.flush()
    await bus.aclose()


async def test_full_subscriber_drops_oldest_and_does_not_raise(
    caplog: pytest.LogCaptureFixture,
) -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe(maxsize=2)
    with caplog.at_level(logging.WARNING):
        for n in range(1, 204):
            await bus.emit(make_span(n))
    assert [queue.get_nowait().id for _ in range(2)] == ["span_202", "span_203"]
    assert (
        len([r for r in caplog.records if r.levelno == logging.WARNING]) == 3
    )  # drops 1, 101 and 201 of 201


async def test_span_events_formats_server_sent_events() -> None:
    bus = SpanBus(SimClock(START))
    stream = span_events(bus, limit=1)
    pending = asyncio.ensure_future(anext(stream))
    await asyncio.sleep(0.01)  # let the stream subscribe
    async with bus.span("guard", "grounding"):
        pass
    item = await asyncio.wait_for(pending, timeout=1)
    assert item["event"] == "span"
    assert json.loads(item["data"])["name"] == "grounding"


async def test_span_events_unsubscribes_on_aclose() -> None:
    bus = SpanBus(SimClock(START))
    stream = span_events(bus)
    pending = asyncio.ensure_future(anext(stream))
    await asyncio.sleep(0.01)
    assert len(bus._subscribers) == 1
    await bus.emit(make_span(1))
    await asyncio.wait_for(pending, timeout=1)
    await stream.aclose()
    assert len(bus._subscribers) == 0


async def test_base_exception_in_body_is_recorded_as_error() -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe()
    with pytest.raises(SystemExit):
        async with bus.span("tool", "exit"):
            raise SystemExit(3)
    span = queue.get_nowait()
    assert span.status == "error"
    assert span.attrs["error"] == "SystemExit: 3"


async def test_long_error_text_is_truncated() -> None:
    bus = SpanBus(SimClock(START))
    queue = bus.subscribe()
    with pytest.raises(ValueError):
        async with bus.span("tool", "big"):
            raise ValueError("x" * 5000)
    error = queue.get_nowait().attrs["error"]
    assert len(error) <= 500
    assert error.startswith("ValueError: xxx") and error.endswith("…")
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_spans.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.core.spans'`.

- [ ] **Step 3: Implement**

`backend/arth/core/spans.py`:
```python
"""Spans: one row per step of a turn or playbook (OBS-1). Published live to subscribers (stage, SSE)."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Literal

from sqlalchemy import insert

from arth.core.clock import SimClock, iso_utc
from arth.core.db import Database
from arth.core.ids import new_id
from arth.core.tables import spans as spans_table

log = logging.getLogger(__name__)
Mode = Literal["live", "replay", "none"]
Status = Literal["ok", "error", "cancelled"]

BATCH_SIZE = 50
BATCH_WINDOW_S = 0.1
PERSIST_QUEUE_MAX = 10_000
DROP_LOG_EVERY = 100


def safe_json(value: Any) -> str:
    """JSON text that is always valid (no NaN/Infinity); never raises."""
    try:
        return json.dumps(value, sort_keys=True, default=str, allow_nan=False)
    except (TypeError, ValueError):
        return json.dumps({"_unserialisable": repr(value)[:2000]})


@dataclass(frozen=True)
class Span:
    id: str
    trace_id: str
    parent_id: str | None
    kind: str
    name: str
    start_at: str
    dur_ms: float
    mode: Mode
    cost_paise: int
    attrs: dict[str, Any] = field(default_factory=dict)
    status: Status = "ok"


class SpanAttrs:
    """Mutable attributes yielded by `SpanBus.span`; also carries the ids for child spans.

    `attrs["cost_paise"] = n` sets the span cost; any other key lands in the span's attrs.
    """

    def __init__(self, span_id: str, trace_id: str) -> None:
        self.span_id = span_id
        self.trace_id = trace_id
        self.attrs: dict[str, Any] = {}
        self.cost_paise: int = 0

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "cost_paise":
            self.cost_paise = value
        else:
            self.attrs[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.cost_paise if key == "cost_paise" else self.attrs[key]


def _cost(raw: Any) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError, OverflowError):
        log.warning("invalid span cost_paise %r; recording 0", raw)
        return 0


ERROR_TEXT_MAX = 500


def _error_text(exc: BaseException) -> str:
    """`Type: message`, capped so user data in exception text can't flood the stream or DB."""
    text = f"{type(exc).__name__}: {exc}"
    return text if len(text) <= ERROR_TEXT_MAX else text[: ERROR_TEXT_MAX - 1] + "…"


class SpanBus:
    """Publishes spans to live subscribers and persists them in the background (best-effort).

    `emit` fans out to subscribers immediately, then enqueues the span for persistence. One
    background task drains the queue in batches (<= 50 spans or 100 ms) into a single multi-row
    insert per transaction. Persistence and serialisation failures are logged, never raised.

    Lifecycle: the app lifespan must `await bus.start()` on startup and `await bus.aclose()` on
    shutdown (flushes pending spans, then stops the task). Without `start()` (or without a DB)
    no task runs; `flush()` then persists any queued spans inline.

    Never call `flush()`/`aclose()` while holding `db.write()`: the persister needs that lock, so
    it would deadlock. `emit()` itself never awaits and is safe anywhere.
    """

    def __init__(self, clock: SimClock, db: Database | None = None) -> None:
        self.clock = clock
        self.db = db
        self._subscribers: set[asyncio.Queue[Span]] = set()
        self._drops: dict[asyncio.Queue[Span], int] = {}
        self._pending: asyncio.Queue[Span] = asyncio.Queue(maxsize=PERSIST_QUEUE_MAX)
        self._task: asyncio.Task[None] | None = None

    def subscribe(self, maxsize: int = 1000) -> asyncio.Queue[Span]:
        queue: asyncio.Queue[Span] = asyncio.Queue(maxsize=maxsize)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[Span]) -> None:
        self._subscribers.discard(queue)
        self._drops.pop(queue, None)

    async def start(self) -> None:
        """Start the persister (idempotent; restarts it if a previous task died)."""
        if self.db is not None and (self._task is None or self._task.done()):
            self._task = asyncio.create_task(self._run(), name="span-persister")

    async def flush(self) -> None:
        """Wait until every span emitted so far has been written (or logged as failed)."""
        if self.db is None:
            return
        if self._task is not None and not self._task.done():
            await self._pending.join()
            return
        while not self._pending.empty():
            await self._write_batch(self._take_nowait(BATCH_SIZE))

    async def aclose(self) -> None:
        await self.flush()
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def emit(self, span: Span) -> None:
        for queue in list(self._subscribers):
            self._publish(queue, span)
        if self.db is None:
            return
        if self._pending.full():
            with contextlib.suppress(asyncio.QueueEmpty):
                self._pending.get_nowait()
                self._pending.task_done()
            log.warning("span persistence backlog full; dropped oldest span")
        self._pending.put_nowait(span)

    def _publish(self, queue: asyncio.Queue[Span], span: Span) -> None:
        try:
            queue.put_nowait(span)
            return
        except asyncio.QueueFull:
            pass
        with contextlib.suppress(asyncio.QueueEmpty):
            queue.get_nowait()  # drop the oldest so the live view stays current
        with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(span)
        drops = self._drops.get(queue, 0) + 1
        self._drops[queue] = drops
        if drops % DROP_LOG_EVERY == 1:
            log.warning("span subscriber is full; dropped oldest span (%d dropped so far)", drops)

    def _take_nowait(self, limit: int) -> list[Span]:
        batch: list[Span] = []
        while len(batch) < limit:
            try:
                batch.append(self._pending.get_nowait())
            except asyncio.QueueEmpty:
                break
        return batch

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            batch = [await self._pending.get()]
            deadline = loop.time() + BATCH_WINDOW_S
            while len(batch) < BATCH_SIZE:
                batch.extend(self._take_nowait(BATCH_SIZE - len(batch)))
                remaining = deadline - loop.time()
                if len(batch) >= BATCH_SIZE or remaining <= 0:
                    break
                try:
                    batch.append(await asyncio.wait_for(self._pending.get(), remaining))
                except TimeoutError:
                    break
            await self._write_batch(batch)

    async def _write_batch(self, batch: list[Span]) -> None:
        if not batch:
            return
        try:
            if self.db is not None:
                rows = [self._row(span) for span in batch]
                async with self.db.write() as conn:
                    await conn.execute(insert(spans_table).values(rows))
        except Exception:
            log.exception("failed to persist %d span(s); telemetry dropped", len(batch))
        finally:
            for _ in batch:
                self._pending.task_done()

    @staticmethod
    def _row(span: Span) -> dict[str, Any]:
        return {
            "id": span.id,
            "trace_id": span.trace_id,
            "parent_id": span.parent_id,
            "kind": span.kind,
            "name": span.name,
            "start_at": span.start_at,
            "dur_ms": span.dur_ms,
            "mode": span.mode,
            "cost_paise": span.cost_paise,
            "attrs": safe_json({**span.attrs, "status": span.status}),
        }

    @asynccontextmanager
    async def span(
        self,
        kind: str,
        name: str,
        *,
        trace_id: str | None = None,
        parent_id: str | None = None,
        mode: Mode = "none",
    ) -> AsyncIterator[SpanAttrs]:
        span_id = new_id("span")
        handle = SpanAttrs(span_id, trace_id or new_id("trace"))
        start_at = iso_utc(self.clock.now())
        started = perf_counter()
        status: Status = "ok"
        try:
            yield handle
        except asyncio.CancelledError:
            status = "cancelled"
            handle.attrs["cancelled"] = True
            raise
        except BaseException as exc:  # incl. SystemExit/KeyboardInterrupt; CancelledError handled above
            status = "error"
            handle.attrs["error"] = _error_text(exc)
            raise
        finally:
            try:
                await self.emit(
                    Span(
                        id=span_id,
                        trace_id=handle.trace_id,
                        parent_id=parent_id,
                        kind=kind,
                        name=name,
                        start_at=start_at,
                        dur_ms=(perf_counter() - started) * 1000,
                        mode=mode,
                        cost_paise=_cost(handle.cost_paise),
                        attrs=dict(handle.attrs),
                        status=status,
                    )
                )
            except Exception:
                log.exception("failed to emit span %s", span_id)
```

`backend/arth/api/__init__.py`:
```python
"""HTTP routers. Each module owns one route family (spec Part C2)."""
```

`backend/arth/api/stream.py`:
```python
"""GET /v1/stream: server-sent events. L0 streams spans; L1 adds domain events and view invalidations."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import asdict

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from arth.core.spans import SpanBus, safe_json

router = APIRouter()


async def span_events(bus: SpanBus, *, limit: int | None = None) -> AsyncGenerator[dict[str, str]]:
    queue = bus.subscribe()
    sent = 0
    try:
        while limit is None or sent < limit:
            span = await queue.get()
            yield {"event": "span", "data": safe_json(asdict(span))}
            sent += 1
    finally:
        bus.unsubscribe(queue)


@router.get("/v1/stream")
async def get_stream(request: Request) -> EventSourceResponse:
    return EventSourceResponse(span_events(request.app.state.spans))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_spans.py -q`
Expected: `3 passed`.

- [ ] **Step 5: Checkpoint**

Run: `python dev.py lint typecheck test`
Expected: all green.

---

### Task 12: Design tokens from the design source (T0.11)

**Files:**
- Create: `contracts/tokens.json`, `frontend/scripts/build-tokens.mjs`
- Generated: `frontend/app/tokens.css`
- Test: `backend/tests/test_tokens.py`, `frontend/tests/tokens.test.ts`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_tokens.py`:
```python
import json
import re

from arth.core.paths import CONTRACTS_DIR, DESIGN_DIR

C2_TO_TOKEN = {
    "MID": "midnight",
    "CYAN": "paytm-blue",
    "SKY": "sky",
    "GROUND": "ground",
    "LINE": "line",
    "INK": "ink",
    "INK2": "ink-2",
    "INK3": "ink-3",
    "CYT": "cyan-text",
    "RED": "red",
    "REDT": "red-tint",
    "GRN": "green",
    "GRNF": "green-fill",
    "GRNT": "green-tint",
    "AMB": "amber",
    "AMBT": "amber-text",
    "AMBTINT": "amber-tint",
}


def c2_constants() -> dict[str, str]:
    text = (DESIGN_DIR / "generator" / "c2.py").read_text(encoding="utf-8")
    return dict(re.findall(r"\b([A-Z][A-Z0-9]*) = '([^']*)'", text))


def tokens() -> dict:
    return json.loads((CONTRACTS_DIR / "tokens.json").read_text(encoding="utf-8"))


def test_colours_match_design_source() -> None:
    consts, colour = c2_constants(), tokens()["color"]
    for c2_name, token in C2_TO_TOKEN.items():
        assert colour[token].upper() == consts[c2_name].upper(), token


def test_shadows_match_design_source() -> None:
    consts, shadow = c2_constants(), tokens()["shadow"]
    assert shadow["1"] == consts["SH"]
    assert shadow["2"] == consts["SH2"]


def test_device_canvas_is_4_by_3() -> None:
    device = tokens()["device"]
    assert (device["width"], device["height"]) == (960, 720)
    assert device["width"] * 3 == device["height"] * 4
```

`frontend/tests/tokens.test.ts`:
```ts
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const css = readFileSync(fileURLToPath(new URL('../app/tokens.css', import.meta.url)), 'utf-8');

describe('generated tokens.css', () => {
  it('exposes design-language colours, radii, type and the 4:3 device canvas', () => {
    expect(css).toContain('--color-midnight: #002E6E;');
    expect(css).toContain('--color-paytm-blue: #00BAF2;');
    expect(css).toContain('--radius-card: 24px;');
    expect(css).toContain('--text-amount: 56px;');
    expect(css).toContain('--text-amount--font-weight: 800;');
    expect(css).toContain('--device-width: 960px;');
    expect(css).toContain('--device-height: 720px;');
  });
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_tokens.py -q` → FAIL (`tokens.json` not found).

- [ ] **Step 3: Write the tokens and the generator**

`contracts/tokens.json` (values from `design/generator/c2.py` and the Foundations board):
```json
{
  "color": {
    "midnight": "#002E6E",
    "paytm-blue": "#00BAF2",
    "sky": "#E8F8FE",
    "ground": "#F5F7FA",
    "line": "#EDEFF0",
    "ink": "#0B1B33",
    "ink-2": "#475467",
    "ink-3": "#5B6475",
    "cyan-text": "#0077B6",
    "red": "#D0103F",
    "red-tint": "#FDECEF",
    "green": "#067647",
    "green-fill": "#12B76A",
    "green-tint": "#E7F8EF",
    "amber": "#F5A524",
    "amber-text": "#8A5300",
    "amber-tint": "#FFF6E0"
  },
  "shadow": {
    "1": "0 1px 2px rgba(16,24,40,0.04), 0 6px 20px rgba(16,24,40,0.05)",
    "2": "0 2px 6px rgba(16,24,40,0.06), 0 16px 40px rgba(16,24,40,0.10)"
  },
  "radius": { "card": "24px", "dock": "999px", "ground": "20px", "button": "16px", "chip": "999px", "nav": "16px" },
  "font": {
    "sans": "'Inter', 'Noto Sans Devanagari', 'Noto Sans Tamil', 'Noto Sans Bengali', 'Noto Sans Gujarati', 'Noto Sans Telugu', system-ui, sans-serif"
  },
  "text": {
    "amount": ["56px", 800],
    "title": ["24px", 700],
    "arth": ["21px", 500],
    "body": ["15px", 500],
    "meta": ["12.5px", 500]
  },
  "device": { "width": 960, "height": 720, "rail": 80, "header": 76 }
}
```

`frontend/scripts/build-tokens.mjs`:
```js
// tokens.json -> app/tokens.css (Tailwind v4 @theme + device CSS variables).
// Run via: python dev.py gen   (or: pnpm --filter frontend run tokens)
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const FRONTEND = join(dirname(fileURLToPath(import.meta.url)), '..');
await mkdir(join(FRONTEND, 'app'), { recursive: true });
const tokens = JSON.parse(await readFile(join(FRONTEND, '..', 'contracts', 'tokens.json'), 'utf-8'));

const lines = [
  '/* Generated from contracts/tokens.json. Do not edit; run `python dev.py gen`. */',
  '@theme {',
];
for (const [name, value] of Object.entries(tokens.color)) lines.push(`  --color-${name}: ${value};`);
for (const [name, value] of Object.entries(tokens.shadow)) lines.push(`  --shadow-${name}: ${value};`);
for (const [name, value] of Object.entries(tokens.radius)) lines.push(`  --radius-${name}: ${value};`);
lines.push(`  --font-sans: ${tokens.font.sans};`);
for (const [name, [size, weight]] of Object.entries(tokens.text)) {
  lines.push(`  --text-${name}: ${size};`);
  lines.push(`  --text-${name}--font-weight: ${weight};`);
}
lines.push('}', '', ':root {');
for (const [name, value] of Object.entries(tokens.device)) lines.push(`  --device-${name}: ${value}px;`);
lines.push('}', '');

await writeFile(join(FRONTEND, 'app', 'tokens.css'), lines.join('\n'));
console.log('tokens: wrote app/tokens.css');
```

- [ ] **Step 4: Generate and run the tests**

Run: `pnpm --filter frontend run tokens`
Expected: `tokens: wrote app/tokens.css`.

Run: `cd backend && uv run pytest tests/test_tokens.py -q` → `3 passed`.
Run: `pnpm --filter frontend run test` → `tokens.test.ts` passes.

- [ ] **Step 5: Checkpoint**

Run: `python dev.py gen lint typecheck test`
Expected: all green (`gen` now runs all three generators).

---

### Task 13: Boot the API and the web app; auth stub; OpenAPI contract test (T0.12)

**Files:**
- Create: `backend/arth/main.py`, `backend/arth/api/problems.py`, `backend/arth/api/auth.py`, `backend/arth/api/health.py`, `backend/arth/api/director.py`, `frontend/next.config.ts`, `frontend/postcss.config.mjs`, `frontend/app/globals.css`, `frontend/app/layout.tsx`, `frontend/app/page.tsx`, `frontend/app/health-badge.tsx`
- Test: `backend/tests/test_app.py`, `backend/tests/test_openapi_contract.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_app.py`:
```python
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
```

`backend/tests/test_openapi_contract.py`:
```python
from pathlib import Path

import yaml

from arth.core.config import Settings
from arth.core.paths import CONTRACTS_DIR
from arth.main import create_app

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def operations(paths: dict[str, dict[str, object]]) -> set[tuple[str, str]]:
    return {(method.upper(), path) for path, ops in paths.items() for method in ops if method in HTTP_METHODS}


def test_served_routes_equal_documented_routes(tmp_path: Path) -> None:
    # FastAPI >= 0.16x nests included routers instead of flattening app.routes, so read the served
    # operations from FastAPI's own generated OpenAPI document (excludes /docs, /redoc, /openapi.json).
    documented = operations(
        yaml.safe_load((CONTRACTS_DIR / "openapi.yaml").read_text(encoding="utf-8"))["paths"]
    )
    served = operations(
        create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path)).openapi()["paths"]
    )
    assert served == documented, f"undocumented: {served - documented}; unserved: {documented - served}"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd backend && uv run pytest tests/test_app.py tests/test_openapi_contract.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'arth.main'`.

- [ ] **Step 3: Implement the API**

`backend/arth/api/problems.py`:
```python
"""RFC 9457 problem responses with a stable code and an i18n message key (spec Part C1)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

ParamValue = str | int | float | bool


class ProblemError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message_key: str,
        *,
        title: str,
        detail: str | None = None,
        params: dict[str, ParamValue] | None = None,
    ) -> None:
        super().__init__(f"{status} {code}")
        self.status, self.code, self.message_key = status, code, message_key
        self.title, self.detail, self.params = title, detail, params or {}


def install_problem_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProblemError)
    async def _handle(_request: Request, exc: ProblemError) -> JSONResponse:
        body: dict[str, object] = {
            "type": f"https://arth.local/problems/{exc.code}",
            "title": exc.title,
            "status": exc.status,
            "code": exc.code,
            "message_key": exc.message_key,
        }
        if exc.detail:
            body["detail"] = exc.detail
        if exc.params:
            body["params"] = exc.params
        return JSONResponse(body, status_code=exc.status, media_type="application/problem+json")
```

`backend/arth/api/auth.py`:
```python
"""Bearer-token stubs per surface (device, console, director). Real sessions and PINs arrive in L1 (STF-2)."""

from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable
from typing import Literal

from fastapi import Request

from arth.api.problems import ProblemError

Surface = Literal["device", "console", "director"]


def require_token(surface: Surface) -> Callable[[Request], Awaitable[None]]:
    async def dependency(request: Request) -> None:
        # The tokens are SecretStr: unwrap only here, and compare in constant time.
        token = getattr(request.app.state.settings, f"{surface}_token")
        expected = f"Bearer {token.get_secret_value()}"
        given = request.headers.get("authorization", "")
        if not secrets.compare_digest(given.encode(), expected.encode()):
            raise ProblemError(
                401,
                "auth.missing_token",
                "error.auth.missing_token",
                title="Unauthorized",
                params={"surface": surface},
            )

    return dependency
```

`backend/arth/api/health.py`:
```python
"""GET /healthz: liveness, mode, sim clock, packs and provider-key status (booleans only)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from arth.core.clock import iso_utc
from arth.core.config import provider_status

router = APIRouter()


@router.get("/healthz")
async def get_health(request: Request) -> dict[str, object]:
    state = request.app.state
    return {
        "status": "ok",
        "mode": state.settings.mode,
        "clock": iso_utc(state.clock.now()),
        "packs": state.packs.names,
        "providers": provider_status(state.settings, state.providers),
    }
```

`backend/arth/api/director.py`:
```python
"""Director API (presenter only). L0 has a ping; L2/L8 add scenario control."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from arth.api.auth import require_token

router = APIRouter(prefix="/v1/director", dependencies=[Depends(require_token("director"))])


@router.get("/ping")
async def director_ping() -> dict[str, bool]:
    return {"ok": True}
```

`backend/arth/main.py`:
```python
"""App factory: validates config, migrates the DB, wires clock, scheduler and spans, mounts routers.

Startup order: config checks -> migrate -> open DB -> scheduler.recover() (re-queue jobs a crash left
`running`) -> start the span persister -> tick loop. Shutdown runs in reverse: stop the tick loop,
flush and stop the span persister (outside any db.write()), close the DB.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arth.api import director, health, stream
from arth.api.problems import install_problem_handlers
from arth.core.calendar import CalendarIndex, load_calendar
from arth.core.clock import SimClock
from arth.core.config import (
    Settings,
    check_auth_tokens,
    check_provider_keys,
    load_policies,
    load_providers,
)
from arth.core.db import Database
from arth.core.migrate import upgrade
from arth.core.packs import PackRegistry
from arth.core.scheduler import Scheduler, tick_loop
from arth.core.spans import SpanBus


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        check_auth_tokens(settings)  # prod refuses the dev-* default tokens
        policies = load_policies(settings.config_dir / "policies.yaml")
        app.state.providers = load_providers(settings.config_dir / "providers.yaml")
        check_provider_keys(settings, app.state.providers)
        app.state.calendar = CalendarIndex(load_calendar(settings.config_dir / "calendar"))
        app.state.packs = PackRegistry.load(settings.packs_dir, policies)
        app.state.policies = policies
        upgrade(settings.db_path)
        db = Database(settings.db_path)
        await db.open()
        clock = SimClock(settings.clock_start)
        app.state.db, app.state.clock = db, clock
        scheduler = Scheduler(db, clock)
        await scheduler.recover()
        app.state.scheduler = scheduler
        spans = SpanBus(clock, db)
        await spans.start()
        app.state.spans = spans
        stop = asyncio.Event()
        ticker = asyncio.create_task(tick_loop(scheduler, stop, settings.tick_interval_s))
        try:
            yield
        finally:
            stop.set()
            await ticker
            await spans.aclose()
            await db.close()

    app = FastAPI(title="Arth API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"]
    )
    install_problem_handlers(app)
    app.include_router(health.router)
    app.include_router(stream.router)
    app.include_router(director.router)
    return app


app = create_app()
```

- [ ] **Step 4: Run the API tests to verify they pass**

Run: `cd backend && uv run pytest tests/test_app.py tests/test_openapi_contract.py -q`
Expected: `5 passed` (incl. the lifespan test: span persister runs while up and is flushed on shutdown).

- [ ] **Step 5: Create the web app shell**

`frontend/next.config.ts`:
```ts
import type { NextConfig } from 'next';

const config: NextConfig = { reactStrictMode: true };

export default config;
```

`frontend/postcss.config.mjs`:
```js
export default { plugins: { '@tailwindcss/postcss': {} } };
```

`frontend/app/globals.css`:
```css
@import 'tailwindcss';
@import './tokens.css';

html,
body {
  background: var(--color-ground);
  color: var(--color-ink);
  font-family: var(--font-sans);
}
```

`frontend/app/layout.tsx`:
```tsx
import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import './globals.css';

export const metadata: Metadata = { title: 'Arth', description: 'AI business partner for Paytm merchants' };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="hi">
      <body>{children}</body>
    </html>
  );
}
```

`frontend/app/health-badge.tsx`:
```tsx
'use client';

import { useEffect, useState } from 'react';
import type { components } from '@/lib/contracts/api';

type Health = components['schemas']['Health'];

export function HealthBadge() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
    fetch(`${base}/healthz`)
      .then((r) => r.json() as Promise<Health>)
      .then(setHealth)
      .catch((e: unknown) => setError(String(e)));
  }, []);

  if (error) return <p className="text-red">API unreachable: {error}</p>;
  if (!health) return <p className="text-ink-3">Checking API…</p>;
  return (
    <p className="text-green">
      API {health.status} · mode {health.mode} · sim clock {health.clock} · packs {health.packs.join(', ')}
    </p>
  );
}
```

`frontend/app/page.tsx` (a developer index; the product surfaces and the no-literal-strings lint arrive in L7):
```tsx
import { HealthBadge } from './health-badge';

// Developer index. The product surfaces (and the no-literal-strings lint) arrive in L7.
const SURFACES: [string, string][] = [
  ['Device · Display (4:3)', '/device'],
  ['Device · Voice', '/device-voice'],
  ['Customer display', '/customer-display'],
  ['Phones', '/phone/owner'],
  ['Console', '/console'],
  ['Stage', '/stage'],
  ['Director', '/director'],
];

export default function DevIndex() {
  return (
    <main className="mx-auto max-w-2xl p-8">
      <h1 className="text-title text-midnight">Arth · dev index</h1>
      <div className="mt-4 rounded-card bg-white p-6 shadow-1">
        <HealthBadge />
      </div>
      <ul className="mt-6 space-y-2 text-body text-ink-2">
        {SURFACES.map(([label, href]) => (
          <li key={href}>
            {label} <span className="text-meta text-ink-3">({href}, arrives in L7)</span>
          </li>
        ))}
      </ul>
    </main>
  );
}
```

- [ ] **Step 6: Build and run both apps**

Run: `python dev.py gen build-web`
Expected: `next build` completes and lists route `/`.

In one terminal run `python dev.py api`, in another `python dev.py web`, then open `http://localhost:3000`.
Expected: the dev index shows "API ok · mode dev · sim clock 2026-10-29T02:15:00.000000Z · packs kirana" (provider key status is in the JSON at http://localhost:8000/healthz) on a white card with the soft card shadow and midnight title. Stop both servers.

- [ ] **Step 7: Checkpoint**

Run: `python dev.py lint typecheck test`
Expected: all green.

---

### Task 14: CP-0, the L0 checkpoint

**Files:**
- Modify: `docs/superpowers/plans/2026-10-30-arth-plan-index.md` (L0 status row)

- [ ] **Step 1: Run the full gate from a clean generate**

Run: `python dev.py gen check build-web`
Expected: generators succeed; ruff, prettier, mypy and tsc are clean; pytest and vitest are all green; `next build` succeeds.

- [ ] **Step 2: Confirm each spec acceptance criterion for L0 explicitly**

| Spec task | Proven by |
|---|---|
| T0.1 repo + task runner | `python dev.py check` runs end to end |
| T0.2 contracts | `test_contract_schemas.py` (7) |
| T0.3 codegen round-trip | `test_contract_roundtrip.py`, `contracts.test.ts` |
| T0.4 clock jump runs nightly jobs in order | `test_scheduler.py::test_jumping_eight_days_runs_eight_nightly_jobs_in_order`; wall-clock ban test |
| T0.5 money/qty/ids | `test_money_qty.py`, `test_ids.py` |
| T0.6 snapshot → restore | `test_db.py::test_snapshot_and_restore_round_trip` |
| T0.7 invalid config fails boot; secrets; India-wide calendar | `test_config.py` (policies, providers, `.env` secrets, prod key check), `test_calendar.py` (Lucknow vs Chennai vs Kolkata vs Varanasi, overrides, recurring) |
| T0.8 pack loosening fails boot | `test_packs.py` loosening, contact-cap, unknown-key tests |
| T0.9 formatting per locale | `test_i18n.py`, `format.test.ts` (shared fixture) |
| T0.10 span < 200 ms | `test_spans.py::test_span_reaches_subscriber_within_200ms_and_is_persisted` |
| T0.11 tokens equal c2.py | `test_tokens.py`, `tokens.test.ts` |
| T0.12 apps boot, health green | `test_app.py`, `test_openapi_contract.py`, manual dev-index check |

Run: `cd backend && uv run pytest -q`, and confirm every file in the table appears in the output with no failures or skips.

- [ ] **Step 3: Mark L0 done in the index**

In `docs/superpowers/plans/2026-10-30-arth-plan-index.md`, change the L0 row's Status cell from `**Written, ready to execute**` to `**Done: CP-0 green (date)**`, and the L1 row's Status to `**Next: write plan**`.

- [ ] **Step 4: Snapshot the empty baseline**

Run: `cd backend && uv run python -c "import asyncio; from pathlib import Path; from arth.core.db import Database; from arth.core.migrate import upgrade; p = Path('data/arth.db'); upgrade(p); asyncio.run(Database(p).snapshot(Path('scenarios/snapshots/l0-baseline.db')))"`
(`snapshot` doesn't need an open engine; it uses its own SQLite connection.)
Expected: `scenarios/snapshots/l0-baseline.db` exists. This is the rollback point for L1 (the project doesn't use git).
