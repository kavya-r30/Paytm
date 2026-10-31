# Arth L6 Growth Layer Implementation Plan (prototype pace)

> One batch, per-task review, commit to `main`. Hackathon prototype due 31 Oct 2026.

**Goal:** T6.1–T6.12: grow the shop with measured, consented, plan-bounded actions. Holdouts are assigned before
any send and are never messaged.

**Architecture:** `arth/growth/` and the `/v1/views/grow*` and `campaigns` routes in `arth/api/growth.py`.
Migration `0010_growth.py` adds hints, growth_plans, campaigns, campaign_assignments and preorders.

| Task | Where | Evidence (`test_l6_growth.py`) |
|---|---|---|
| T6.1 Diagnostics | `engine.diagnostics`: sales = customers × frequency × basket, sequential attribution | parts sum exactly to the change |
| T6.2 Lever registry | `engine.levers` from the pack manifest; plans may only use pack levers | a salon-only lever in a kirana plan is refused |
| T6.3 Counter hints | `record_hint` on open/attach (arm assigned first, 20% holdout), `hint_for` on `bill_view.hint` | owner audience only, < 300 ms, none for holdout |
| T6.4 Win-back / Replenish / Repeat | lever audiences from lifecycle and purchase cycles; `outreach.send_campaign` (R3) | holdout never messaged; treated without marketing consent skipped with reason |
| T6.5 Demand capture | L3 clusters + unmet demand (notices ride Concierge templates) | covered by L3 tests |
| T6.6 Bundles + pre-orders | greedy pairs above the margin floor and in stock; `preorders.create` (R2) books the deposit as an advance | advance ≥ deposit |
| T6.7 Credit advisor | `credit_advice`: steady payers only; never with a dispute or broken promise | suggestions only raise |
| T6.8 Welcome/opt-in | marketing consent is checked at send; welcome lever audience = new | no consent → not sent |
| T6.9 Offer proposals | programs via L1 `offers.create_program` (R3) with regulars excluded | L1 tests |
| T6.10 Plan + campaign + guardrail | `growth.create_plan` (R3, pack levers, budget); campaigns outside the plan's levers are refused; a complaint stops every running campaign | auto-stop on a planted complaint |
| T6.11 Ledger + Impact | `ledger`: treated vs holdout spend, bootstrap CI or counts mode; measured/direct/estimated | one entry per campaign |
| T6.12 Pack levers | levers listed from each manifest (café slow_hour, salon slot_fill, storefront) | — |

Also in this batch (Lane B requests): #8 `POST /v1/auth/step-up {otp}` (simulated OTP `123456`, owner Console, 10
minutes, then R4 passes the policy gate); #9 `POST /v1/public/storefront/{slug}/orders` creates an order *draft* as a
customer actor; #10 every turn's envelope is pushed on `/v1/stream` as `event: envelope`. Sarvam TTS now sends `text`
(not `inputs`), with a `bulbul:v2` hop added, and `ai-smoke` prints each failed hop with the provider's error body.

## Execution ledger

Deviations (prototype): the Strategist's 10-step plan is the R3 plan command plus diagnostics; Strategist offer
proposals reuse L1 offer programs; the bandit priors and OR-Tools bundle solver are replaced by greedy pairs. Review
fix: `bill_view.hint` was made optional after it broke Lane B's typed fixture (additive contract changes must stay
optional).

CP-6 (30 Oct 2026): holdout, consent, contact-cap, plan-scope and margin-floor rules hold; **1342 pytest + 448 Vitest**; gen-check, lint and typecheck clean.
