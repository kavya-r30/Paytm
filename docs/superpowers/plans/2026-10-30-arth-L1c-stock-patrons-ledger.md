# Arth L1c Stock, Patrons and Ledger Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans and superpowers:test-driven-development inline. No git, no subagents. Review each task against spec IDs before code quality; Checkpoints replace commits.

**Goal:** Implement T1.11, T1.14 and T1.15, the inventory, customer and interest-free khata dependencies needed by Counter and payments.

**Architecture:** Scoped SQLAlchemy domain modules run within the Command Bus transaction. Stock is an append-only move projection with FEFO allocation. Patron identity/consent and reward ledgers supply trusted policy facts. Khata uses append-only entries, allocations, payments and advances; R2 gates bind account/amount/lines and R3 reminders recheck consent/caps/quiet hours immediately before reservation.

**Tech Stack:** Existing Python/FastAPI/SQLite/Alembic/JSON Schema, integer paise/milli-units, SimClock, pytest/Hypothesis. No external payment or messaging calls; verified adapter seams prepare L2 integrations.

**Spec:** v6 F2.2/K2 T1.11, T1.14, T1.15; STK-1/2, EXP-1/2/5, PAT-1…4, LED-1…12, AIQ-1/2/7, C1–C6, J3/J4/J9, L2. v5.1 D3/D4/D11, E7.2, F12.5/6.

## Global Constraints

- No git, no subagents, never inspect backend/.env or generated signing-key files. Use `python dev.py` and `python -m uv`.
- Contracts first; generated Python/TS/CSS are never hand-edited. Plans retain CRLF and synchronized full-source blocks.
- All business queries inject merchant_id. All writes use bus transactions; consumer effects share their offset transaction. No deletes/corrections in money/stock/ledger rows; append compensations instead.
- SimClock is the only business time source. Money and quantities remain exact integers. Actor/device/tenant/verification facts are server-owned.
- Customer PII must not enter durable command/audit/outbox data: public patron requests are validated at the gateway, with identifying fields passed via ephemeral R1 context; durable effects/results use IDs. This prepares actual identifying-field erasure in T1.20 without rewriting the audit chain.
- Latest user steering: finish these three L1c tasks, run CP-1c, update the handoff and **stop**. The remaining T1.12, T1.13 and T1.16–T1.23 run as one combined L1d pass (see the plan index).

## Remaining pass order

| Batch | Tasks | Dependency reason |
|---|---|---|
| C | T1.11 Stock, T1.14 Patrons, T1.15 Ledger | Counter needs inventory, customer accounts and credit allocation |
| D | T1.12 Counter, T1.13 Treasury, T1.16 Orders | Integrate bill/payment/khata/stock state machines |
| E | T1.17 Supply, T1.18 Offers, T1.19 Tax/Books, T1.20 Storefront/Feedback/Privacy/Device | Integrate procurement, liabilities, reconciliation and public/privacy boundaries |
| F | T1.21 Capital reads/Console apply boundary, T1.22 Sentinel core, T1.23 all screen views | Complete read/verification surfaces and full CP-1 fixtures for each pack |

## Review Focus

- Concurrent negative moves cannot oversell; recalled/expired batches never become sellable through a FEFO override (Task 1).
- Name-only ambiguity cannot merge customers; owner/model text cannot grant consent without verified customer instruction (Task 2).
- Duplicate payment references cannot allocate twice; excess funds are advances, not negative debt (Task 3).
- Disputes, purchase-day suppression, broken promises, changed balances and contact caps block inappropriate reminders/limit raises (Task 3).
- Privacy erasure later must not find customer names/phones/VPAs embedded in immutable command/audit/event records (Tasks 2/3 and T1.20).

## File structure

```text
backend/arth/domains/stock_tables.py, stock.py       stock moves/counts/batches/unmet demand and FEFO
backend/arth/domains/patron_tables.py, patrons.py   identity, consent, households, rewards and minimal shared offer liability
backend/arth/domains/ledger_tables.py, ledger.py    accounts, entries/lines/events, payments/allocations, advances, promises, reminders, payables
backend/arth/api/commerce_core.py                   scoped stock/patron/khata reads and verified customer-link boundary
backend/migrations/versions/0004_stock_patrons_ledger.py
backend/tests/test_l1c_*.py                         task/property/API/security regressions
contracts/commands/*.schema.json, events/*.schema.json, *view*.schema.json
```

### Task 1: Append-only stock, batches and FEFO (T1.11)

**Interfaces:** `register_stock(bus, packs)` registers stock.receive/count/adjust/recall_batch/log_unmet_demand. `on_hand(repo, item_id, batch_id?)` derives sums; `issue_stock(repo, clock, item_id, qty_milli, ref_id, buyer_id?, override_batch_id?, reason?)` is a transaction-local Counter hook with no independent commit. `stock_view`/`expiry_view` expose physical and sellable stock separately. Required batch/expiry derives from the pack, never its name.

- [x] Define strict command/event/read contracts and examples; regenerate.
- [x] Write RED tests for sums/count corrections, required pharmacy fields, FEFO order, recall/expiry, foreign batches, oversell rollback and tenant isolation; add Hypothesis FEFO/sum properties.
- [x] Implement frozen migration 0004, append-only moves and receipt batch metadata (number, expiry, MRP, cost). Exclude expiry-day/expired and recalled batches from issuance; owner-only FEFO overrides need a reason and cannot override safety blocks. Counts correct by new rows.
- [x] Expose recall buyer IDs from prior issue moves, near-expiry data and unmet-demand records; no outbound notices are sent here.
- [x] Run task tests, review STK/EXP IDs then quality; checkpoint evidence in ledger.

### Task 2: Patrons, consent, households and visit rewards (T1.14)

**Interfaces:** `PatronService` validates public requests then submits sanitized bus commands; `resolve_identity(repo, kind, value)` handles hashed VPA/phone/name evidence and ambiguity; `has_consent(repo, patron_id, purpose)` uses latest purpose state. `record_customer_instruction(...)` and verified payment/reward hooks are trusted adapter entry points. `outbound_context(repo, patron_id, purpose)` reads actual consent/contact reservations. Household membership is explicit, never inferred from names. Rewards issue/redeem through an append-only ledger and shared `offer_liability` rows (issued/redeemed/expired) in the same transaction.

- [x] Contracts first; write RED tests for identity/merge confidence boundaries, hashed VPA, same-name ambiguity, tenant isolation, no default consent, STOP, forged grants, explicit household members, duplicate visits and reward liability.
- [x] Implement patrons/identities, non-destructive merge links/proposals, append-only purpose consent records, explicit household membership and reward rules/ledger. Strong identity evidence can auto-propose/merge above 0.9; intermediate evidence asks; no low-confidence merge or name-based privilege transfer.
- [x] Keep identifying fields solely in erasable patron/identity storage. Owner/customer instruction proofs are never inferred from an arbitrary text payload. Add a restricted system role for verified R1 callbacks; it cannot approve R2/R3 or invoke R4.
- [x] Run tests including outbound policy with real stored consent, STOP across purposes, household authorization and reward accounting; review PAT/LED-11/AIQ IDs then quality; checkpoint.

### Task 3: Interest-free ledger, allocation and CP-1c (T1.15)

**Interfaces:** `register_ledger(bus)` registers open account, add entry, set limit, record payment, apply verified reminder payment, apply advance, dispute/acknowledge, promise, reminder, statement and payable commands. `allocate_payment(...)` and `apply_advance(...)` are transaction-local helpers for Counter/Treasury. `account_view`, `statement`, `khata_view` derive balances and line-level provenance. `PolicyContext` for reminders derives consent/caps/disputes/purchase dates from tables, never request flags.

- [x] Contracts/examples then regenerate. Write RED tests for ₹1,000 against ₹700 + ₹450 → ₹0/₹150; an additional ₹450 leaves ₹600 total; partial/excess payments, duplicate/concurrent refs, advances and liability, line reconciliation, limits/owner override, household mismatch, disputes/promises, payables, statement totals and no time-based interest/late-fee accrual.
- [x] Implement append-only money records, oldest-first allocations, explicit advance liabilities/applications, line-item validation and R2 read-back data. Monetary corrections append new rows; no direct balance column exists. Reject unknown fee/interest fields.
- [x] Enforce R2 for cash/unmatched UPI; verified reminder-link receipts use a private verified R1 adapter seam. Reserve purpose-scoped outbound requests atomically, with a unique link reference per reminder; actual delivery/link minting belongs to L2. Freeze reminders on disputes, purchase day, unexpired promises and cap/cadence violations. Trace policy reasons and mark sensitive replies discreet.
- [x] Add stock/expiry/customer/patron/khata/promise/statement read endpoints and invalidation metadata. Schema-validate real API responses and events.
- [x] Review each task against spec IDs, then quality; fix via RED/GREEN, sync source snapshots, run `python dev.py check`. Only then mark CP-1c, update the handoff and stop as requested.

## Execution ledger

Pre-flight: stock needs existing catalog/pack validation; patron creation precedes accounts; Counter will call stock/ledger helpers inside its own bus transaction; Treasury will call verified payment allocation; Supply will create payables from GRN. Event causation is the executing command ID. Frozen migration 0003 is unchanged.

Ruling: execute T1.14/15 before T1.12/13 to satisfy their customer/khata dependencies within L1. Cost: task IDs are not chronological, but no dependency is guessed or stubbed.

Ruling: only minimal reward-linked `offer_liability` accounting is brought forward from T1.18, because PAT-4 explicitly depends on it. Offer programs/abuse controls remain batch E. Cost: the Offers module must reuse and extend that shared table rather than declare another ledger.

Ruling: live payment/message adapters and narration/TTS are not fabricated in L1. Store verified-request/link/read-back data and test adapter seams; implement actual simulator delivery in L2 and narrated number words in L4 as the original layer plan requires. Cost: L1's backend cannot contact real customers or lenders.

CP-1c (30 Oct 2026): `python dev.py check` exit 0; **741 pytest passed** (1 existing Starlette/httpx warning), **214 Vitest passed**, ruff/mypy/gen-check clean.

Final review fixes (RED first, then GREEN):
- Contract examples carried malformed 27-char IDs; both contract-discovery lists (pytest, Vitest) missed `credit_receipt_requested`; the codegen-error test regex was brittle.
- LED promises: one `promise_status(repo, promise, clock)` in `ledger_projection` (kept / broken / active, IST due-day cutoff at 18:30 UTC) now drives the reminder freeze, the limit-raise freeze, `khata_account_view.promises[].status` and `/v1/views/promises`. That endpoint had compared UTC date prefixes against the IST due date.
- LED-9 statements: `ledger.send_statement` mints a unique pay link (`reminders` row with template `statement.balance`) when a balance is due. `statement`/`account_view` expose `pay_link_ref` (latest link while a balance is owed). Statement links do not count towards reminder cadence, and verified link payments accept either kind.
