# Arth L5 Agentic Layer Implementation Plan (prototype pace)

> One batch, per-task review, commit to `main`. Hackathon prototype due 31 Oct 2026.

**Goal:** T5.1–T5.14: durable playbooks that do the shop's routine work and propose through the bus. Owners
answer gates, and agents can never approve.

**Architecture:** `arth/agents/`.
- `runtime.py` holds `Playbook` (named async steps) and `Runtime` (persisted cursor + JSON context; `Next`, `Wait`,
  `Done`, `Fail`).
  - Exactly-once side effects use `run_id:label` idempotency keys.
  - An Event Matcher (a Dispatcher consumer) wakes waiting runs, and `tick` handles deadlines.
  - Contact locks and per-agent pause with a `*` kill switch.
  - A step ceiling per tick, and `playbook.updated` events.
- Agents act on the owner's authority on the `agent` channel: R1 runs, R2/R3 become gates, R4 is refused.
  `CommandBus.decide` rejects any agent session (AIQ-1).
- `playbooks.py`: Night Shift (alerts, daily close, brief, spawns, memory derivations); Reorder with Delivery Check
  and Claims; Collections (reminder R3 → wait → promise sleep → follow-up → work item after three tries);
  Concierge (untrusted text → drafts only; own balance only; medical → pharmacist; injection flagged); Feedback
  recovery; Expiry clearance (above cost, return for Rx); Analyst weekly; salon reminders; pharmacy refill run;
  batch recall.
- Triggers: `message.in`, `feedback.recorded` (low), `batch.recalled`; Night Shift is a daily 22:00 scheduler job.
- `commands.py`: `messages.reply` (10-minute reply window), `memory.propose` (untrusted → unverified),
  `memory.confirm/retract/forget`, `agents.pause`, `playbooks.start/cancel`.
- `views.py` + `config/helpers.yaml`: `team_view` (tier badges computed from `policies.yaml`), `run_view`,
  `memory_view`, and the home `brief`.
- `arena.py`: scripted personas × scenarios, pass^k.
- The Conductor gains the Work Board's partial answer ("Haan, Mehta ko chhod ke" → approve all, snooze Mehta).
- Migration `0009_agents.py`.

| Task | Evidence (`test_l5_agents.py`) |
|---|---|
| T5.1 Runtime | restart mid-wait (fresh Runtime) resumes; one PO and one gate, nothing sent twice |
| T5.2 Waits | approval → PO sent → event wakes the run; supplier-bill variance wakes the claim step |
| T5.3 Work Board | `POST /v1/work/batches`; partial answer approves all but the excluded supplier |
| T5.4 Contact locks | second playbook deferred for the same person |
| T5.5 Memory guard | customer claim stored unverified; owner forget scrubs the value |
| T5.6 Controls | kill switch stops all runs; resume continues |
| T5.7 Night Shift | brief stored (yesterday, typical, dues, one suggestion), collections/reorder spawned |
| T5.8 Procurement | reorder → R3 PO → wait → GRN + bill → variance → R3 claim |
| T5.9 Collections | reminder R3, wait on credit.changed, promise sleeps until its date |
| T5.10 Concierge | order draft + R3 accept gate; own balance only; injection flagged with no order |
| T5.11 Analyst/Curator/Expiry/Feedback | work items with computed parameters |
| T5.12 Pack playbooks | salon reminders, refill run (reminder consent), recall (consented buyers) |
| T5.13 Helpers | 8 display groups; Kharid tier R3 computed |
| T5.14 Arena | 3 scenarios × k = 4, pass^4 |

## Execution ledger

Deviation: LangGraph is not used. A ~300-line durable runtime keeps the same guarantees (persisted state, idempotent
effects, event waits, deadlines) without a new dependency or the checkpointer. Deviation: LLM personas in Arena need
live providers; the scripted cards run offline. Review fixes: a waiting run stores its next step (tests read
`wait_topic`); runs started from bus commands or event consumers use `start_in` inside the open transaction, which
avoids a nested-write deadlock.

CP-5 (30 Oct 2026): every playbook path above passes end to end, including restart mid-wait; Arena pass^4.
