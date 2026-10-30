# Arth: Handoff for L1 (continue in a fresh Claude Code / Codex session)

## Current checkpoint (30 Oct 2026, CP-8) — L8 DONE (backend complete)

L8 is in `backend/arth/sim/scenario.py` and `backend/scenarios/` (plan:
`docs/superpowers/plans/2026-10-30-arth-L8-scenarios-demo.md`). 16 scenarios run headless; `python dev.py demo-check
-- --runs 10` is green and writes `cues.md` per scenario. Director: `POST /v1/director/snapshot|restore {name}`, `GET
/v1/director/scenarios`. Remaining: Lane B binds the stage/Director to the library (L7) and re-runs `ai-smoke` live.

## Checkpoint CP-6 — L6 DONE

L6 growth is in `backend/arth/growth/` (plan: `docs/superpowers/plans/2026-10-30-arth-L6-growth.md`). Migration 0010
is frozen. Lane B's requests 8–10 are done. Next: L8 scenario library and demo, together with Lane B.

## Checkpoint CP-5 — L5 DONE

L5 agents are in `backend/arth/agents/` (plan: `docs/superpowers/plans/2026-10-30-arth-L5-agents.md`). The dispatch
loop ticks the runtime; Night Shift runs at 22:00 IST. Migration 0009 is frozen. Next: L6 growth.

## Checkpoint CP-4 (offline) — L4 DONE (live evals pending)

L4 is in `backend/arth/ai/` (plan: `docs/superpowers/plans/2026-10-30-arth-L4-ai-platform.md`). `POST /v1/turns`
works on device/console/WhatsApp; providers fall back to cassettes/templates when unreachable (they are blocked in
cloud sessions; run `python dev.py ai-smoke` on a laptop to record cassettes). Migration 0008 is frozen.

## Checkpoint CP-3 — L3 DONE

L3 intelligence is in `backend/arth/intel/` (plan: `docs/superpowers/plans/2026-10-30-arth-L3-intelligence.md`):
analytics tools, 12 charts, forecasts with accuracy, cash flow, lifecycle, alerts, decisions. Migration 0007 is frozen.
Next: L4 AI platform (provider router with real Mistral/Groq/Sarvam keys in `backend/.env`, cassettes for tests).

## Checkpoint CP-2 — L2 DONE

L2 simulators are in `backend/arth/sim/` (plan: `docs/superpowers/plans/2026-10-30-arth-L2-simulators.md`).
`python dev.py seed -- --pack kirana --days 30` builds a demo shop into the data DB and prints the device credential;
`python dev.py scenario` runs `backend/scenarios/billing_smoke.yaml` headless. Migration 0006 is now frozen.
`backend/.env` now holds real provider keys (git-ignored) for L4.

## Checkpoint CP-1 — L1 DONE

**CP-1 green:** 1175 pytest + 340 Vitest, gen-check/lint/typecheck clean. L1d (T1.12, T1.13, T1.16–T1.23) is recorded in
`docs/superpowers/plans/2026-10-30-arth-L1d-commerce-completion.md`. New tables are in migration 0005 (frozen from now on;
L2+ tables go in 0006+). `arth.domains.wiring.register_commerce` registers every domain; `arth.api.views` serves every J9 screen.
Domain-table writes outside a bus command now raise (`Repository._writable`); tests seed with `conftest.seed_repo`.

**Next (user, 30 Oct 2026): prototype pace, two parallel lanes** — Lane A backend L2→L6 (this account), Lane B frontend L7
(second account), coordinated through GitHub issues; see the plan index. Git is now used: commit per layer, push, draft PR.

## Previous checkpoint (CP-1c)

L1a (T1.1–T1.6), L1b (T1.7–T1.10) and L1c (T1.11 Stock, T1.14 Patrons, T1.15 Ledger) are complete.
CP-1c: `python dev.py check` exit 0, **741 pytest passed (1 existing Starlette/httpx warning), 214 Vitest passed**,
ruff, mypy and gen-check clean. The execution ledgers are in `docs/superpowers/plans/2026-10-30-arth-L1a-foundation.md`,
`…-L1b-identity-catalog.md` and `…-L1c-stock-patrons-ledger.md`. Migrations 0001–0004 are frozen: new tables go in 0005.

**Next: L1d, all remaining L1 tasks as ONE batch.** That is T1.12 Counter, T1.13 Treasury/payments, T1.16 Orders/appointments,
T1.17 Supply, T1.18 Offers, T1.19 Tax/Books, T1.20 Storefront/Feedback/Privacy/Device, T1.21 Capital reads + Console-only R4 apply,
T1.22 Sentinel core and T1.23 view endpoints for every J9 screen. Then run CP-1. After L1, the user wants **each layer (L2, L3, …)
done as one batch, all of its tasks together**, still with a per-task review.

L1c hooks that L1d must reuse (do not duplicate them):
- **Stock:** `arth.domains.stock`: `issue_stock(repo, clock, item_id, qty_milli, ref_id, buyer_id?, override_batch_id?, reason?)`
  is a transaction-local FEFO issue for Counter; `stock.receive` serves GRN.
- **Ledger:** `arth.domains.ledger_money`: `allocate_payment(...)` and `apply_advance(...)` are transaction-local for Counter khata/Treasury.
  Payables come from `ledger.add_payable` / `ledger.pay_payable`, which Supply GRN should create.
  `ledger_projection.promise_status` and `statement` (with `pay_link_ref`) are the khata read models.
- **Patrons:** `arth.domains.patrons` / `patron_identity`: `has_consent`, `outbound_context`, `resolve_identity`.
  The trusted system actor `patrons._system(merchant_id)` handles verified R1 callbacks (`private={"payment_verified": True}`).
- **Offers:** the shared `offer_liability` table already exists (reward-linked, from PAT-4). T1.18 must extend it, not add a new liability ledger.
- **Privacy:** customer PII lives only in the erasable patron/identity tables, and command/audit/outbox rows carry IDs only.
  T1.20 erasure must scrub those tables without touching the audit chain.

## 1. Paste this into the new chat

```
You are continuing the build of "Arth" (Paytm Hackathon 2026, Merchant Growth AI): an AI business partner on the
Paytm Soundbox for Indian shop owners. Repo: C:\Users\kavya\Desktop\Hackathon\Paytm (Windows 11; Python 3.12, Node 22, pnpm 10).

FIRST read docs/HANDOFF-L1.md in full (rules, state, L1c hooks), then docs/superpowers/plans/2026-10-30-arth-plan-index.md
and the L1c plan's execution ledger. L1a–L1c are done (CP-1c green: 741 pytest + 214 Vitest). Do not redo them.

Your job: L1d = ALL remaining L1 tasks as one batch: T1.12 Counter, T1.13 Treasury/payments/payment exceptions,
T1.16 Orders/appointments, T1.17 Supply, T1.18 Offers, T1.19 Tax/Books, T1.20 Storefront/Feedback/Privacy/Device,
T1.21 Capital reads + Console-only R4 apply boundary, T1.22 Sentinel core, T1.23 view endpoints for every J9 screen.
Requirement IDs and acceptance criteria: spec Part K2 (task table) and the Part J9/traceability table
(CTR, TRS, PEX, ORD, SAL, CAFE, SUP, OFR, TAX, BKS, STO, FBK, TRU-5, HLT, CAP, SEN).
1. Write docs/superpowers/plans/2026-10-30-arth-L1d-commerce-completion.md in the L1c plan format
   (header, global constraints, file structure, one task section per spec task, execution ledger).
   Order by dependency: Counter → Treasury → Orders → Supply → Offers → Tax/Books → Storefront/Privacy/Device → Capital → Sentinel → Views.
2. Implement inline (NO subagents), TDD, with a captured RED run for each task. Contracts first (`python dev.py gen`).
   New tables go in migration 0005 (0001–0004 are frozen).
3. Review EVERY task yourself, first against its spec IDs, then for code quality. Fix via RED/GREEN.
4. Run `python dev.py check` yourself and paste the real output. Then run CP-1: all L1 property and contract tests,
   every write through the bus, audit chain verifies, all views schema-valid for a fixture shop of each pack
   (kirana, cafe, pharmacy, salon). Then mark CP-1 in the plan index and this handoff, and write the L2 handoff prompt.
   From L2 on, each layer runs as one batch (all of its tasks together), with a per-task review.

Hard rules: no git (never run git). Never open, print, cat or grep backend/.env or generated signing-key files.
Use `python dev.py <target>`, not make. Run uv as `python -m uv`. Never hand-edit generated files.
```

## 2. Hard rules (the user set these; follow them exactly)
1. **No git.** Never run `git init/add/commit`. Each task ends with a *Checkpoint* (tests green) instead of a commit. For rollback, use the DB snapshot `backend/scenarios/snapshots/l0-baseline.db` and copy files before risky edits.
2. **Never read `backend/.env`.** It holds the real Mistral, Groq and Sarvam keys; `/healthz` shows all three as configured. `backend/.env.example` is the template and is fine to read. Keys reach code only through `Settings` (`SecretStr`).
3. **Work inline, no subagents.** Do the implementation, reviews and tests yourself in the main session.
4. **One batch per layer** (user, 30 Oct 2026: L1d = all remaining L1 tasks; each later layer = all its tasks together), but **every task gets reviewed**: check it against the plan *and* the spec requirement IDs (spec compliance first, then code quality), fix, re-check, and run the gate before marking it done.
5. **TDD:** write the failing test, run it and see it fail, implement, run it and see it pass. Capture the red run. It matters: twice in L0 code was written before the tests.
6. **Run tests yourself** (`python dev.py check`), and paste the real outputs in your summaries.
7. Contracts first: change `contracts/`, then run `python dev.py gen`. **Never hand-edit generated files** (`backend/arth/contracts/*`, `frontend/lib/contracts/*`, `frontend/app/tokens.css`).
8. Keep the plan doc as the record: when code changes after review, sync the plan's fenced code blocks to the files on disk. Preserve each plan doc's existing line endings (the current plan docs are LF).

## 3. Documents (read in this order)
| Doc | Why |
|---|---|
| `docs/specs/2026-10-30-arth-v6-merged-design.md` | **The spec.** For L1: Part C (contracts, C1 conventions, C2 API families incl. Commands/Views, C5 events, C6 tiers + pipeline), Part D (packs), Part F2 (L1 components + domain modules + invariants), Part K2 (L1 task table T1.1–T1.23 + acceptance), Part L2 (invariants) |
| `docs/reference/Arth_Spec_v5.1.md` | Detailed acceptance criteria the v6 spec cites as "v5.1 §x": D3 data model, D4 Command Bus & tiers, D5 Event Spine, D11 Governance, E4 Work Board/approvals/scope hash, C1–C10 requirement tables (CTR, LED, …), AIQ-1 |
| `docs/specs/2026-10-30-arth-v6-demo-and-scenarios.md` | Scenario library + demo (L8); useful for seed data shapes |
| `docs/superpowers/plans/2026-10-30-arth-plan-index.md` | Layer plans and status. L0 is done; L1 is next |
| `docs/superpowers/plans/2026-10-30-arth-L0-foundations.md` | **Format to copy** for the L1a plan (header, file-structure section, tasks with `- [ ]` steps and full code, Checkpoints). Its code blocks equal the files on disk |
| `contracts/README.md` | Contract rules (draft-07, `definitions`, `anyOf` nullables, integer before number, per-card/per-topic extension pattern) |

## 4. Repo layout (after restructure)
```
backend/   Python 3.12 FastAPI app, package `arth` (uv venv at backend/.venv)
  arth/core/      paths, clock, ids, money, qty, db, tables, migrate, scheduler, yamlconf, config, calendar, packs, schemas, i18n, spans
  arth/api/       problems, auth, health, director, stream
  arth/contracts/ GENERATED Pydantic (do not edit)
  arth/tools/     gen_contracts.py
  arth/main.py    create_app() + lifespan
  config/         policies.yaml, providers.yaml, calendar/{regions,events-2025,events-2026,events-2027,seasons-2026-27}.yaml
  packs/kirana/manifest.yaml
  migrations/     Alembic (env.py imports table modules; 0001 = jobs, spans)
  tests/          pytest (conftest: async `db` fixture)
  data/ (runtime DB), scenarios/snapshots/l0-baseline.db
  .env (secrets: NEVER read), .env.example
frontend/  Next.js 16 / React 19 / Tailwind v4 (pnpm package "frontend")
  app/ (layout, page = dev index, health-badge, globals.css, tokens.css GENERATED), lib/ (format.ts, validate.ts, contracts/ GENERATED), scripts/, tests/ (vitest)
contracts/ shared JSON Schemas (common, envelope, events/event, problem), openapi.yaml, examples/, fixtures/, tokens.json, README.md
design/    boards/ (*.dc.html screens), generator/ (c2.py tokens), previews/ (PNGs)
docs/      specs/, superpowers/plans/, reference/ (v5.1 docs), HANDOFF-L1.md
dev.py     task runner
```

## 5. Commands (Windows; uv is not on PATH)
| Do | Command |
|---|---|
| Install everything | `python dev.py setup` |
| Regenerate contracts and tokens | `python dev.py gen` |
| Full gate (gen-check, lint, typecheck, test) | `python dev.py check` |
| Web production build | `python dev.py build-web` |
| Run API / web | `python dev.py api` (port 8000) / `python dev.py web` (port 3000) |
| One backend test file | `cd backend && python -m uv run pytest tests/test_x.py -q` |
| Format / lint backend | `cd backend && python -m uv run ruff format arth tests && python -m uv run ruff check arth tests` |
| Types | `cd backend && python -m uv run mypy arth`; `pnpm --filter frontend exec tsc --noEmit` |
| Web tests / format | `pnpm --filter frontend exec vitest run`; `pnpm --filter frontend exec prettier --write .` |

**CP-0 baseline (30 Oct 2026):** `python dev.py gen check build-web` is all green, with **388 pytest + 118 vitest**. Live smoke test: `/healthz` returns ok/dev with the clock at 2026-10-29T02:15Z, the kirana pack, and all 3 providers configured; `/v1/director/ping` returns 401 problem+json without a token and `{"ok": true}` with `Bearer dev-director`.

## 6. L0 public APIs you will build on
- **`arth.core.paths`:** `REPO_ROOT`, `BACKEND_DIR`, `CONTRACTS_DIR`, `CONFIG_DIR`, `PACKS_DIR`, `DATA_DIR`, `DESIGN_DIR`.
- **`arth.core.ids`:** `new_id(kind) -> "kind_<ULID>"` (kind is 2–10 lowercase alphanumeric characters starting with a letter), `parse_id`, `kind_of`, `IdError`.
- **`arth.core.money` / `qty`:**
  - `to_paise(str|int|Decimal)` is exact and rejects float/bool/nan and plain-decimal strings with more than 2 places.
  - `div_round_half_even(n, d)` uses pure integer maths.
  - `to_milli` and `line_amount(unit_price_paise, qty_milli)`.
  - `MoneyError`, `QtyError`, `scale_exact`.
- **`arth.core.clock`:** `SimClock(start, *, running=False, rate=1.0, monotonic=time.monotonic)` with `now()` (UTC), `now_ist()`, `set()` (forward only), `reset()` (any direction, used only for restore), `freeze()`, `run(rate)`, plus `running` and `rate`. Also `iso_utc()` (fixed-width `...Z`), `parse_iso()`, `next_daily(after, "HH:MM")`, `IST`, `UTC`, `ClockError`. **Never use `datetime.now()`**; an AST test bans it outside clock.py.
- **`arth.core.db`:**
  - `Database(path)` with `open()`, `close()`, `engine`, `read()` (async ctx, gated during restore), `write()` (async ctx, single asyncio write lock, commit/rollback), `snapshot(dest)` (VACUUM INTO), `restore(src)` (SQLite backup API in place, waits ≤5 s for readers).
  - `metadata`, a SQLAlchemy Core `MetaData` with a naming convention.
  - **Rules:** go through `read()`/`write()`; don't nest `read()`; don't call `restore`/`snapshot` inside `write()`.
- **`arth.core.tables`:** `jobs`, `spans` (SQLAlchemy Core `Table`s on `metadata`).
- **`arth.core.migrate`:** `upgrade(db_path)` (Alembic). `migrations/env.py` must import every new table module, and a drift test (`tests/test_migrations.py`) compares models against migrations with `compare_type=True`. **New tables need a new migration file `0002_...` and an import in env.py.**
- **`arth.core.scheduler`:** `Scheduler(db, clock)` with `on(name, handler)`, `schedule(name, due_at, payload, every_seconds=|daily_at=)`, `schedule_daily(name, "HH:MM")`, `recover()`, `run_due()`, `advance_to(target)`, `count(status=)`, plus `tick_loop(scheduler, stop, interval_s)`.
  - Delivery is at-least-once, so handlers must be idempotent.
  - Rows are claimed atomically.
  - Handlers must not call `run_due` or `advance_to`.
- **`arth.core.spans`:** `SpanBus(clock, db=None)` with `subscribe()`, `unsubscribe()`, `start()`, `flush()`, `aclose()`, `emit()`, and `async with bus.span(kind, name, trace_id=, parent_id=, mode=) as h: h["k"]=v; h["cost_paise"]=n`.
  - Spans record `status` (ok/error/cancelled).
  - Persistence is batched and best-effort.
  - Never call `flush` while holding `db.write()`.
- **`arth.core.config`:**
  - `Settings` reads `backend/.env`; prefix `ARTH_`; keys are `SecretStr`; tokens `director_token`/`device_token`/`console_token` are `SecretStr`.
  - Fields `mode` (dev/test/demo/prod), `data_dir`, `config_dir`, `packs_dir`, `clock_start` (2026-10-29 07:45 IST) and `tick_interval_s`, plus `db_path`.
  - Functions: `load_policies` → `Policies` (`tiers` maps command type → R0–R4; `roles`, `quiet_hours`, `contact_caps`, `reminders`, `growth`, `expiry_alert_days`, `discreet_mode`, `attention`, `forbid_offers_on_flags`), `load_providers`, `check_provider_keys`, `check_auth_tokens`, `provider_status`, `ConfigError`.
- **`arth.core.calendar`:** `load_calendar(dir)` and `CalendarIndex` with `between(city, start, end)`, `upcoming(city, today, within_days=)`, `days_until(kind, today, city=)` and `state_of(city)`. Each `Occurrence` has id, kind, start, end, confidence, source, type, names, closure, note, lead_days, tail_days and priors.
- **`arth.core.packs`:** `PackRegistry.load(packs_dir, policies)` with `names`, `get(pack)`, `lever(pack, name)` and `policies_for(pack)`. Packs may only tighten policies (`PackPolicyError`).
- **`arth.core.schemas`:** `discover_schemas()`, `schema(name)`, `validator(name)` (a Draft7 validator with a `referencing` registry, so cross-file `$ref`s resolve).
- **`arth.core.i18n`:** `format_money(paise, locale, *, compact, native)`, `format_date`, `LOCALES` (hi, en, hi-Latn, mr, ta, bn, gu, te), `LocaleError`. Money output is byte-identical to `frontend/lib/format.ts`.
- **`arth.api`:**
  - `problems.ProblemError(status, code, message_key, *, title, detail, params)` plus `install_problem_handlers(app)`, which renders RFC 9457 `application/problem+json`.
  - `auth.require_token("device"|"console"|"director")` is a FastAPI dependency.
  - Routers in `health`, `stream` (SSE, spans) and `director`.
- **`arth.main.create_app(settings)` lifespan:** config checks → `upgrade` → `Database.open` → `scheduler.recover()` → `spans.start()` → `tick_loop`. Shutdown runs in reverse. `app.state` holds settings, providers, calendar, packs, policies, db, clock, scheduler and spans. **When you add routers, also add them to `contracts/openapi.yaml`**: `tests/test_openapi_contract.py` asserts served == documented, using `app.openapi()["paths"]` because FastAPI 0.162 nests routers.

## 7. Conventions and gotchas learned in L0
- Money is integer **paise**, quantities integer **milli-units**, IDs prefixed ULIDs, times UTC ISO strings from `iso_utc()` stored as TEXT (fixed width, so they sort lexically).
- `sqlalchemy[asyncio]` (greenlet) is required, and is already in pyproject.
- In JSON Schemas, list `integer` before `number` so Pydantic keeps ints; use `anyOf` with null for nullable fields, never union `type` arrays (Ajv runs strict).
- Ruff line length is 110 (E501). Run `ruff format` and then `ruff check`.
- `pytest-asyncio` runs in auto mode, so async tests and fixtures need no decorator.
- FastAPI 0.162: `app.routes` no longer lists included routes. Use `app.openapi()`.
- `next build` may rewrite `frontend/tsconfig.json`; run prettier on it once.
- The repo has no `.git`. The `.gitignore` only exists to keep secrets out if git is ever added.
- Windows: a shell whose cwd is inside a folder locks it, so `cd` out before moving or deleting folders.

## 8. What L1 is (spec Part K2, T1.1–T1.23)
**L1 = Commerce Core + governance.** Do it in parts, writing each part's plan against the real code.
- **L1a (do now): T1.1–T1.6**
  - T1.1, data model foundation: only the tables the foundation needs. These are merchants/merchant_settings, minimal staff (actor identity), commands, approvals, audit_log, outbox and consumer_offsets, plus the tenancy filter (every domain query is scoped by `merchant_id`; a test asserts no raw query lacks it).
  - T1.2, Command Bus: typed commands; per-type tier from `policies.yaml`; Idempotency-Key, where a replay returns the stored result; execution in one transaction with an outbox event and an audit row.
  - T1.3, Policy Engine: roles, consent, quiet hours, caps, discreet mode, R1 message classes, pack policies.
  - T1.4, Approval Service: gates; `scope_hash = sha256(type ‖ canonical(payload) ‖ conditions)`; conditional approvals; batches with partial answers; series; plan scope; the 30 s send queue as data; owner-bound approvals (a helper session cannot approve R2/R3, AIQ-1).
  - T1.5, hash-chained audit: `hash = sha256(prev_hash ‖ canonical_json(row))`, with a verifier and a tamper test.
  - T1.6, outbox + dispatcher + consumer offsets + `view.invalidate` derivation, published on the existing SSE stream.
  - Routes `POST /v1/commands`, `POST /v1/approvals/{thread_id}` and `GET /v1/audit/verify` go in `contracts/openapi.yaml` and the routers.
  - Contract schemas for commands and for the event payloads `command.*`, `approval.*` and `audit.*`.
  - **Suggested batches:** A = T1.1 data model + tenancy + migration 0002; B = T1.2 bus + T1.3 policy + T1.5 audit; C = T1.4 approvals + T1.6 outbox/dispatcher + routes.
  - **CP-1a** maps each acceptance criterion (GOV-1, GOV-2, WFL-3, WFL-4 data side, AIQ-1, idempotency) to the test that proves it.
- **L1b and later:** T1.7–T1.23 are merchants/settings/onboarding, staff/shifts, catalog, stock with batches/expiry/FEFO, counter, payments/treasury, patrons/consent/rewards, the khata ledger, orders/appointments, supply, the offers engine, tax/books, storefront/feedback/privacy/device, capital read tools, sentinel core, and **view endpoints for every screen in spec Part J9**. Plan each part after the previous part is green. **CP-1:** all L1 property and contract tests pass; every write goes through the bus; the audit chain verifies; views return valid payloads for a hand-built fixture shop of each pack.

## 9. Small known follow-ups (optional, low priority)
- `restore()` doesn't check that a snapshot's Alembic revision matches the live one. Consider running `upgrade()` after restore.
- The migration drift test doesn't set `compare_server_default`.
- `SpanAttrs` lacks `get` and `update`; one NaN attr makes `safe_json` fall back for the whole attrs object.
- Scheduler: failing recurring jobs reschedule forever with no backoff, and `done` rows are never pruned.
- Calendar: 2027 is partial, and T2.10 (L2) completes it from official notices. Re-check the Tamil Nadu Deepavali (7 Nov 2026) and Holika Dahan dates.
- Tokens: no line-height tokens yet, which L7 will need.
- Spec open questions are in Part N2: hosting, a real WhatsApp bridge, extra UI locales (kn/ml/pa/or/as), physical hardware, and producing the new screens as React stories.
