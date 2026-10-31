# Arth L3 Intelligence Implementation Plan (prototype pace)

> One batch, per-task review, commit to `main`. Hackathon prototype due 31 Oct 2026.

**Goal:** T3.1–T3.13: every number Arth shows or says comes from a parameterised tool over the ledgers (never an LLM).

**Architecture:** `arth/intel/` — pure read functions over scoped repositories, plus two bus commands
(`alerts.scan`, `actions.snooze`) and migration `0007_intelligence.py` (alerts, action_snoozes). An hourly scheduler
job (`intel.hourly`) submits `alerts.scan` for every merchant as the system actor. HTTP: `/v1/views/forecast`
(now a real `forecast_view`), `/v1/views/insights`, `/v1/analytics/{tool}`, `/v1/charts/{1..12}` (JSON card or
`?format=svg`), `/v1/books/export/{pnl|gst|khata_aging|settlements}`.

| Task | Where | Evidence (`test_l3_intelligence.py`) |
|---|---|---|
| T3.1 Analytics | `intel/analytics.py`: sales, payments, compare, top/slow, khata aging, lifecycle, lapsed, hourly, cycles, affinity | payments by mode = Treasury day summary; daily sales = Σ closed bills |
| T3.2 Charts | `intel/charts.py`: all 12 F10.3 charts + SVG renderer | each chart rebuilt twice → identical data |
| T3.3 Forecasts | `intel/forecast.py`: weekday seasonal P50 × festival factor, empirical P10/P90, 14-day backtest WAPE + coverage | P10 ≤ P50 ≤ P90; coverage reported (prototype tolerance 50–100%) |
| T3.4 Cash flow | `cashflow`: P10/50/90 inflow vs payables, open POs, EDI → shortfall date | 14-day path |
| T3.5 Lifecycle + cycles | `lifecycle`, `purchase_cycles` | planted lapsing regulars classified lapsing/lost |
| T3.6 Affinity | `affinity`: pair lift, per-patron habits ≥ 60% | via chart/analytics API |
| T3.7 Demand clusters | `insight.demand_clusters`: token-overlap agglomerative (embeddings in L4) | planted "ghee" cluster of 2 found |
| T3.8 Peers | L2 `sim/peers.py` | n ≥ 10 gate |
| T3.9 Uplift | `forecast.bootstrap_ci`: 90% bootstrap CI, counts mode when small | CI brackets the point estimate |
| T3.10 Decision | `insight.next_best_actions`: generators, scoring, attention budget 1/day, snooze | snoozed action never returns |
| T3.11 Alerts | `insight.alerts` + `alerts.scan`: band breach, refund spike, settlement/duplicate exceptions, near-expiry | planted duplicate raises once, never repeats |
| T3.12 Sufficiency | `insight.sufficiency`: per-feature gates (days, bills, regulars) | in insights view |
| T3.13 Books | `/v1/books/export/*` CSV over L1 P&L / GST | P&L CSV contains net |

## Execution ledger

Deviations (prototype): Chronos-2 is not installed; the seasonal-naive model is behind the same read model so it can be
swapped. Forecasts are computed on read rather than stored nightly. Demand clustering uses token overlap; embeddings and
cluster naming arrive with L4. Review fixes: the band could invert when every backtest error had one sign (P10 now ≤ P50
always); chart responses now carry `invalidate_on`; world-based tests share one generated world (runtime 5½ → 2 min).

CP-3 (30 Oct 2026): planted lapsers, demand cluster and duplicate-payment alert found on a generated 35-day kirana
world; **1229 pytest passed, 353 Vitest passed**; gen-check, lint and typecheck clean.
