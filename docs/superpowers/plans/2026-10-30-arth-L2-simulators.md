# Arth L2 Simulators Implementation Plan (prototype pace)

> One batch, per-task review, commit to `main`. Hackathon prototype due 31 Oct 2026 (user steering).

**Goal:** T2.1–T2.11: the simulated outside world and generated shop histories, so every later layer and the
frontend run against realistic data through the real API.

**Architecture:** `arth/sim/` holds simulated outside parties. `Simulators` (hub.py) is the Rails (dynamic/static QR,
links, pending/failed, faults, settlement with fee/EDI/refund lines, cashback and refund execution), the messaging
network (threads, Cloud-API-shaped outbound with its own marketing cap, inbound) and the lender sandbox. Everything
reaches Arth through **HMAC-signed webhooks** verified at ingress (`/webhooks/rails`, `/webhooks/messages`), which
hash the VPA, drop the untrusted payer name and submit R1 commands as the restricted system actor. What Arth decides
reaches the world through an outbox consumer (`sim.world`). Simulator state is in `sim_*` tables (exempt from the
bus-only write guard because it is not Arth's state); migration `0006_simulators.py`.

| Task | Where | Acceptance evidence |
|---|---|---|
| T2.1 Rails | `sim/hub.py`, `api/sim.py` | webhook-driven bill close; duplicate delivery idempotent; delay → pending→success; drop → redeliver; wrong signature 401; settlement explainer matches (`test_l2_simulators.py`) |
| T2.2 UPI pay page backend | `GET/POST /sim/pay/{token}` | payee + amount only; page itself is Lane B (frontend) |
| T2.3 Messaging | `sim/hub.py`, `domains/inbox.py` (`messages.receive`, `message.in`) | marketing cap enforced by the network; inbound stored as untrusted data; PO → supplier thread delivery |
| T2.4 Lender | `Simulators.lender_offers`, `capital.applied` consumer | three offers with every CAP-4 field; applied loan's EDI appears in settlement |
| T2.5 Forge | `sim/forge.py`, `POST /sim/tools/screenshot` | genuine vs edited SVG + fields + phash + ELA score |
| T2.6 Personas | `config/personas.yaml`, `sim/personas.py` | scripted cues, manual queue; LLM mode is T4.16 |
| T2.7/T2.8 Worlds | `sim/world.py`, `python dev.py seed`, `POST /v1/director/world` | all four packs, invariants hold, planted facts manifest (lapsing regulars, near-expiry batch, GRN variance, anomaly day, unmet demand, duplicate payment, forged screenshot), reproducible hash |
| T2.9 Peers | `sim/peers.py`, `GET /v1/peers/{pack}` | n = 12 per pack, percentiles only (n ≥ 10 gate) |
| T2.10 Calendar | `calendar.add_local_event`, `GET /v1/views/calendar` | owner local events + "tentative within 60 days" count |
| T2.11 Runner | `sim/scenario.py`, `scenarios/billing_smoke.yaml`, `python dev.py scenario` | 5-beat billing scenario passes headless through the real API |
| Invariants | `sim/invariants.py` | Σ payments + khata = bill total, invoice reconciles, batch stock ≥ 0, allocations ≤ charges, advances, offer liability vs budget, audit chain |

## Execution ledger

Deviation (prototype pace): tests were written alongside each simulator rather than strictly first; every failure
was fixed before commit. Deviation: T2.10's "complete 2027 from official notices" is not done (no reliable source in
a cloud session); the owner local-events table and the tentative-date report are. Review fixes during the batch:
starter-catalog import needs `confirmed: true`; consent source refs must be prefixed IDs; café milk restock sized to
recipe consumption; scenario settings never read `.env`.

CP-2 (30 Oct 2026): all four packs generate worlds with zero invariant violations; the billing scenario passes headless;
`python dev.py gen-check lint typecheck` exit 0; **1206 pytest passed, 346 Vitest passed**.
