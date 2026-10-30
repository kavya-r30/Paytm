# Arth v6: Implementation Plan Index

> **For agentic workers:** each layer has its own plan. Execute one layer plan at a time with superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Do not start a layer until the previous layer's checkpoint (CP-n) is green.

**Spec:** `docs/specs/2026-10-30-arth-v6-merged-design.md` (Part K lists every task; this index turns Part K into plans).
**Scenarios and demo:** `docs/specs/2026-10-30-arth-v6-demo-and-scenarios.md`.

**Why one plan per layer, written just in time.** Each layer's plan needs the real interfaces of the layers below it, for exact file paths, function signatures and test fixtures. Writing all nine plans now would mean guessing those interfaces and rewriting the plans later. So each plan is written when its layer starts, from the code that actually exists.

**Project conventions (apply to every plan):**
- **No git.** Tasks end with a **Checkpoint** step (run the named tests, all green) instead of a commit. Before risky steps, copy `data/` and `scenarios/snapshots/` if they matter.
- **Windows-first tooling.** Use `python dev.py <target>` (a cross-platform task runner at the repo root) wherever the spec says `make <target>`.
- **TDD** for all domain, governance and money code: write the failing test, watch it fail, implement, watch it pass.
- **Contracts first.** Change `contracts/`, run `python dev.py gen`, then write code against the regenerated types.

| Layer | Plan file | Spec tasks | Checkpoint | Status |
|---|---|---|---|---|
| L0 Foundations | `2026-10-30-arth-L0-foundations.md` | T0.1–T0.12 | CP-0: `python dev.py check` green; contract round-trip; clock-jump test; snapshot test; web build | **Done: CP-0 green (30 Oct 2026): 388 pytest + 118 vitest, gen-check, build** |
| L1 Commerce Core and governance | `2026-10-30-arth-L1a-foundation.md`, `2026-10-30-arth-L1b-identity-catalog.md`, `2026-10-30-arth-L1c-stock-patrons-ledger.md`, `2026-10-30-arth-L1d-commerce-completion.md` (T1.12, T1.13, T1.16–T1.23 in one pass) | T1.1–T1.23 | CP-1 | **Done: CP-1 green (30 Oct 2026): 1175 pytest + 340 Vitest; fixture shop per pack through the API, every J9 view schema-valid, audit verifies** |
| L2 Simulators | `…-arth-L2-simulators.md` | T2.1–T2.11 | CP-2 | Write after CP-1; per the user, each later layer runs as one batch (all its tasks together) |
| L3 Intelligence | `…-arth-L3-intelligence.md` | T3.1–T3.13 | CP-3 | Write after CP-2 |
| L4 AI platform | `…-arth-L4-ai-platform.md` | T4.1–T4.16 | CP-4 | Write after CP-3 |
| L5 Agentic layer | `…-arth-L5-agents.md` | T5.1–T5.14 | CP-5 | Write after CP-4 |
| L6 Growth layer | `…-arth-L6-growth.md` | T6.1–T6.12 | CP-6 | Write after CP-5 |
| L7 Frontend | `…-arth-L7-frontend.md` (likely split: 7a shell + design system, 7b existing screens, 7c new screens, 7d other surfaces, 7e stage) | T7.1–T7.18 | CP-7 | **Parallel lane (second Claude account), started after CP-1 against the L1 contracts; coordinated in GitHub issues** |
| L8 Scenario library and demo | `…-arth-L8-scenarios-demo.md` | T8.1–T8.7 | CP-8 | Write after CP-7 |

**Deviations from the spec, adopted in the L0 plan.** The spec has been updated to match:
1. `make` → `python dev.py` (make isn't installed on the team's Windows machines).
2. Web runtime validation uses **Ajv on the same JSON Schemas** instead of generated Zod. Same source of truth, one less generator.
3. Indian number **words** for TTS move from T0.5 to T4.4, where the TTS normaliser that uses them lives (YAGNI in L0).
4. **India-wide festival calendar moved into L0** (spec Part D3, CAL-1…7). Written during planning in `backend/config/calendar/`:
   - 21 states and 72 cities;
   - the 2025 festive season (for last-year comparisons) and all of 2026, with a source and confidence on every row;
   - a partial 2027 and seasons.

   T2.10 becomes the yearly refresh: complete 2027 from official notices, plus owner-added local events.
5. **AI and agent frameworks are final** (spec Part G0):
   - LangGraph ≥ 1.2.12 with the SQLite checkpointer for orchestration;
   - direct `mistralai`, `groq` and `sarvamai` SDKs behind Arth's Provider Router;
   - Pydantic v2 for structured output;
   - Sarvam **Saaras v4** for speech to text and **Bulbul v4 Flash** for text to speech.
6. **Secrets.** API keys live in the `backend/.env` (template `.env.example`). Only the API reads them, as `SecretStr`. `prod` refuses to boot without them, and `/healthz` reports per-provider key status as booleans.

**Parallel lanes after CP-1 (user, 30 Oct 2026).** The project is now a hackathon prototype due 31 Oct; rigour is reduced to "prototype": tests for money/governance invariants and contract validity, thinner coverage elsewhere.
- **Lane A (backend, this account):** L2 → L3 → L4 → L5 → L6, then L8 with Lane B. Branch `claude/modest-cannon-38l5jl`.
- **Lane B (frontend, second account):** L7 (T7.1–T7.18) against `contracts/` and `/v1/views/*`. Contract changes needed by the UI are requested in a GitHub issue, never hand-edited in generated files.
- Coordination: GitHub issues labelled `lane:backend`, `lane:frontend`, `contract-change`. Each lane opens draft PRs into `main`.
