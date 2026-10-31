# Arth L8 Scenario Library and Demo Implementation Plan (prototype pace)

> One batch, per-task review, commit to `main`. Hackathon prototype due 31 Oct 2026. L7 (frontend) is Lane B's; L8
> is the backend half of the demo: the scenario language, the library, the headless runner, and the Director hooks the
> stage and the Director screen bind to.

**Goal:** T8.1–T8.7: every demo story is a validated scenario that runs headless through the real API, ten times in a
row, and can be rehearsed and recovered from on stage.

**Architecture:** `contracts/scenario.schema.json` (the language, generated to `arth/contracts/scenario.py` and
`frontend/lib/contracts/scenario.ts`); `arth/sim/scenario.py` (the `ScenarioRunner`, cue cards and the CLI);
`backend/scenarios/<id>/scenario.yaml` (the library, plus a generated `cues.md` per scenario); Director routes in
`arth/api/sim.py`.

| Task | Where | Evidence (`test_l8_scenarios.py`, `demo-check`) |
|---|---|---|
| T8.1 Scenario language | `scenario.schema.json`: scenes → beats with `cue`, `who`, `focus` (device screen, phone, evidence tab), inputs (`say_for_me` with surface, `command` with optional fixed `key`, `approve_all`, `persona_action`, `clock`, `fault`, `locale`, `read`, `settle`, `tick`), `save`, `expect_turn`, `expect` (view path `equals`/`gte`/`lte`/`len`/`contains`/`present`/`absent`, the last `result`, `sim_thread` + `outbound_template`, invariants), `within_ms`; `cut` lists scenes per short cut; `world.cold_start` | every library file validates |
| T8.2 Snapshots + restore | the runner snapshots before each scene; `POST /v1/director/snapshot {name}` and `POST /v1/director/restore {name}` restore the DB and the sim clock | restore < 3 s |
| T8.3 Gupta Diwali | `gupta_diwali` (full) and `--cut short` (the 5-minute cut), with `focus` on every beat for the stage | passes headless; the short cut runs only its scenes |
| T8.4 Packs + cold start | `cafe_morning_rush`, `pharmacy_batch_recall`, `salon_wedding_season`, `kirana_cold_start`, `kirana_month_end` | green |
| T8.5 Edge cases | `edge_offline_billing` (queued commands replay under their own keys; nothing doubles), `edge_provider_outage`, `edge_injection`, `edge_duplicate_webhook`, `edge_two_sharmas` (Arth asks which Sharma), `edge_ambiguous_item`, `edge_budget_exhaustion`, `edge_opt_out`, `edge_pending_upi`; the recall is `pharmacy_batch_recall` | green |
| T8.6 `demo-check` | `python dev.py demo-check -- --runs 10`: every scenario, ten runs in a row, each on a fresh data dir; replay mode (providers are cassettes or templates) | 10 consecutive green per scenario |
| T8.7 Rehearsal tooling | `--cues` writes `cues.md` (cue, who, focus and measured ms per beat); recovery = Director restore of the scene snapshot; `GET /v1/director/scenarios` serves the library to the Director and the stage | cue cards cover every beat |

Fixes made while running the library (all behind the existing tests): approve-all grammar accepts "Haan, teeno"; a
spoken first name resolves when it is unique (else Arth asks); an unknown item asks with catalog matches instead of
guessing; `isolated_settings()` defaults to a fresh data dir (it used to share `data/arth.db` across processes);
the runner sends `patrons.add` through `/v1/patrons` (profiles are PII and stay off the command log).

## Execution ledger

Deviations (prototype): "live" `demo-check` runs only where provider hosts are reachable (Lane B's laptop, after
`ai-smoke`); in the cloud session every run is replay. The stage's timing per beat comes from the headless run, not
a live rehearsal. Timing budgets (`within_ms`) get a 5× headless margin.

CP-8 (30 Oct 2026): 16 scenarios, each 10/10 green under `demo-check`; gen-check, lint and typecheck clean; full
pytest and Vitest green (counts in the index).
