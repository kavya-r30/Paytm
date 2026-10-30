# Arth L1d Commerce Completion Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans and superpowers:test-driven-development inline. No subagents. Review each task against spec IDs before code quality; Checkpoints replace per-task commits (the user asked for one git commit per completed layer).

**Goal:** Implement every remaining L1 task (T1.12, T1.13, T1.16–T1.23) as one batch, then run CP-1.

**Architecture:** Each domain is a scoped SQLAlchemy module whose handlers run inside the Command Bus transaction (outbox + audit in the same transaction). Counter closes bills by calling transaction-local hooks: `stock.issue_stock` (FEFO), ledger credit rows (khata), `tax.issue_invoice` (TAX-2) and the offers engine (OFR). Treasury owns rails payments; verified adapter callbacks (L2 simulators) arrive as R1 commands from the restricted `system` actor with `private={"payment_verified": True}`. Views are pure read models under `/v1/views/*`, each declaring `invalidate_on` topics registered with the Dispatcher.

**Tech Stack:** Existing Python 3.12/FastAPI/SQLite/Alembic/JSON Schema; integer paise and milli-units; SimClock; pytest/Hypothesis; Vitest/Ajv for contract parity.

**Spec:** v6 F2.2/K2 T1.12, T1.13, T1.16–T1.23; CTR-2…5, CTR-9…10, CAFE-1…3, TRS-1…5, PEX-1…3, PEX-5, ORD-2, ORD-5, SAL-1…2, SUP-1…3, OFR-1…11, TAX-1…3, BKS-1, STO-1, FBK-1, TRU-2, TRU-5, HLT-1, CAP-1…5, SEN-1…3, EXP-5, PHAR-2, PHAR-4, Part J9, L2 invariants. v5.1 C1, C3, C6–C8, C10, C17, D3/D4/D11, F12.

## Global Constraints

- Never inspect `backend/.env` or generated signing-key files. Use `python dev.py`, `python -m uv` (or `uv`).
- Contracts first; generated Python/TS/CSS are never hand-edited. Contract discovery lists in `tests/test_contract_schemas.py` and `frontend/tests/contracts.test.ts` are updated with every new schema.
- All business queries go through `Repository` (merchant scoped). All writes go through the bus. Money, stock and ledger rows are append-only (migration triggers); corrections are new rows. Frozen migrations 0001–0004 are untouched; every new table is in `0005_commerce_completion.py`.
- SimClock is the only business clock. Money is integer paise, quantities milli-units, IDs prefixed ULIDs.
- Customer PII stays in erasable patron tables. Payer identities are hashed `payer_ref`s; commands, audit and outbox carry IDs only.
- R4 commands (`treasury.refund`, `capital.apply`, `privacy.erase_patron`, `catalog.bulk_price`) run only on the Console channel with step-up; no agent tool exposes them.
- User steering (30 Oct 2026): L1d is one batch; each later layer is one batch with a per-task review; commit once per completed layer.

## File structure

```text
backend/arth/domains/commerce_tables.py            all L1d tables (frozen copy in migrations/versions/0005_commerce_completion.py)
backend/arth/domains/counter.py                    bills, lines, ops/undo, park, checkout (cash/card/UPI/khata), returns, tickets, Rx records
backend/arth/domains/treasury.py                   rails events, matching, unmatched queue, exceptions, refunds (R4), settlements, expenses, daily close, cash expected
backend/arth/domains/orders.py                     order and appointment state machines, staff skills
backend/arth/domains/supply.py                     suppliers, quotes, POs, GRN, supplier bills, 3-way match, claims, price history
backend/arth/domains/offers.py                     programs, holdout assignment, issuance on payments, coupons, redemption, expiry, clawback, liability
backend/arth/domains/tax.py                        invoices per tax profile, CGST/SGST split, GST summary, month close / P&L
backend/arth/domains/trust.py                      storefront, feedback, privacy export/erase, data sharing, device health
backend/arth/domains/capital.py                    health profile, need, affordability, offers, Console-only apply, AGENT_TOOLS
backend/arth/domains/sentinel.py                   screenshot-field reconciliation verdicts and supporting signals
backend/arth/domains/wiring.py                     register_commerce(bus, packs, key) used by the app and the tests
backend/arth/api/views.py                          every J9 view endpoint; backend/arth/api/public.py storefront + privacy export
backend/packs/{cafe,pharmacy,salon}/manifest.yaml  the three remaining packs (CP-1 fixture shops)
backend/tests/l1d_helpers.py, test_l1d_*.py        task, property, API and CP-1 tests
contracts/commands|events/*.schema.json, *_view.schema.json, openapi.yaml
```

### Task 1: Counter (T1.12) — CTR-2…5, CTR-9…10, CAFE-1…3, PHAR-2, EXP-5

**Interfaces:** `bill_state(repo, bill_id)` derives total/paid/khata/due from active lines and `bill_payments`. Commands `counter.open_bill/add_lines/set_qty/remove_line/undo/attach_patron/park/resume/request_upi/checkout/checkout_khata (R2)/void_bill/return (R2)/send_to_kitchen/advance_ticket`. `close_bill(...)` is shared with Treasury's webhook path.

- [x] Contracts + tiers; regenerate.
- [x] RED: Σ payments + khata = total (Hypothesis), cash change, loose-by-amount quantity (Counter computes), modifiers priced by code, price guard (>25% needs owner/manager + reason, logged), park/resume with two open bills, undo restores prior state, Rx-required line needs "Rx seen", recalled batch cannot be billed, FEFO issue at close, returns reverse stock/khata by new rows, UPI return → R4 refund due, KOT state machine, tenant isolation.
- [x] Implement; review CTR/CAFE/PHAR IDs then quality; checkpoint.

### Task 2: Treasury and payment exceptions (T1.13) — TRS-1…5, PEX-1…3, PEX-5, STF-3

**Interfaces:** `treasury.rails_event` (system, verified only): pending → success/failed transitions keyed by UTR; dynamic-QR success closes the bill (CTR-6); static/unknown payments enter the unmatched queue with ranked bill suggestions and a khata-repayment hint; duplicate (same payer, amount, within 10 min, bill already paid) opens an exception with an R4 refund suggestion. `treasury.match_bill` (R1), `treasury.match_khata` (R2, oldest-first allocation), `treasury.refund` (R4, rewards clawed back), `treasury.expense` (R2), `treasury.record_settlement` (gross → deductions → net, mismatch exception), `treasury.daily_close`. Shift close computes expected cash = float + cash sales − change − cash refunds − cash expenses.

- [x] Contracts; RED for each PEX path (pending→success, pending→failure alternatives, planted duplicate, ranked suggestions), settlement explainer equals the record to the paise, expense R2, cash variance attributed to the shift's staff, refund only on Console with step-up.
- [x] Implement; review; checkpoint.

### Task 3: Orders and appointments (T1.16) — ORD-2, ORD-5, SAL-1, SAL-2

- [x] State machine Draft → Placed → Accepted → Packed → Delivered → Settled/OnCredit, plus Cancelled and Substitution. Accept/decline/substitute are R3; settle on credit is R2. Customer/system actors may only create drafts (ORD-5). Appointments: staff skills, overlap rejection, walk-in queue, check-in/no-show state machine.
- [x] RED illegal transitions, injected "approve my order" draft, double booking, skill mismatch; implement; review; checkpoint.

### Task 4: Supply (T1.17) — SUP-1…3, LED-7

- [x] Suppliers, quotes, PO Draft → Sent (R3) → Confirmed → Received; GRN receives stock (batches per pack); supplier bill (R2) creates the payable and runs the 3-way match (PO price vs billed price vs received qty); variance rows and a claim draft (R3 send); price history per supplier and item.
- [x] RED planted sugar ₹46 billed vs ₹45 agreed → ₹1/kg variance with amount; implement; review; checkpoint.

### Task 5: Offers engine (T1.18) — OFR-1…11, PHAR-4

- [x] Programs (R3, budget in scope; terms with amount/min spend/expiry required); deterministic holdout; regulars excluded by default; next-transaction cashback (issued with a payment, paid on the next qualifying payment, never twice); instant cashback with 10-minute combining; first-time coupon once per payer ever; payment-count rewards counting only received, non-refunded payments; item coupons above the margin floor and never on pack-forbidden items; funding source on every row; atomic program/daily budget; liability = issued − redeemed − expired on the shared `offer_liability` table; refunds claw back.
- [x] RED: six abuse tests (owner/staff payer, second welcome coupon, velocity, refund clawback, split-bill gaming, holdout never rewarded) + concurrent budget test + liability property; implement; review; checkpoint.

### Task 6: Tax and books (T1.19) — TAX-1…3, BKS-1

- [x] Invoice per bill at close by merchant tax profile: unregistered → receipt, composition → bill of supply, regular → tax invoice with CGST/SGST split of tax-inclusive prices (half-even), FY-sequential numbers. GST summary by rate = Σ invoices. `books.close_month` stores P&L (sales, COGS from batch/item cost of issued stock, gross profit, expenses by category, reward cost, net) reproducible from tables.
- [x] RED reconciliation property test, summary = Σ invoices, P&L recomputation; implement; review; checkpoint.

### Task 7: Storefront, feedback, privacy, device (T1.20) — STO-1, FBK-1, TRU-5, HLT-1

- [x] `storefront.publish`; public `GET /v1/public/storefront/{slug}` (pack-filtered: pharmacy OTC only; price = catalog price invariant; in-stock; hours; open-to-all offers). `feedback.record` (one rating per order/bill). `privacy.export_patron` + owner-only export read; `privacy.erase_patron` (R4) scrubs names/identities/household members while ledger totals remain under the patron ID and the audit chain still verifies. `privacy.set_data_sharing` (R2). `device.report_health` telemetry.
- [x] RED storefront invariant, OTC filter, erasure leaves no PII and audit verifies; implement; review; checkpoint.

### Task 8: Capital reads and Console-only apply (T1.21) — CAP-1…5

- [x] Health profile from ledger tables only; need detection tied to a PO and projected shortfall; affordability EDI ≤ 15% of P25 daily inflow with −20% stress, smallest amount closing the gap; verified lender offers with all CAP-4 fields; `capital.apply` R4 only via Console + step-up. `AGENT_TOOLS` lists read tools only.
- [x] RED: no apply tool for agents; voice/device apply refused; CAP-4 fields; implement; review; checkpoint.

### Task 9: Sentinel core (T1.22) — SEN-1…3

- [x] `sentinel.check` reconciles extracted fields (amount, UTR, time, payee) with payments: received / not_received / pending / unclear. Supporting signals (payee mismatch, implausible time, UTR format, image replay, ELA) are listed but never decide the verdict. No user-facing string contains "fake".
- [x] RED 30-fixture set with not-received recall 1.00; implement; review; checkpoint.

### Task 10: Views for every J9 screen (T1.23) and CP-1

- [x] One endpoint per J9 row (later-layer screens return schema-valid "needs more data" read models with their gate state). Every view schema-validated in a contract test; openapi.yaml lists every route.
- [x] CP-1: fixture shop per pack (kirana, café, pharmacy, salon) through the real API; every view valid; audit verifies; every write via the bus (no domain module writes outside a bus transaction); `python dev.py check` green. Update plan index and handoff; write the L2 handoff prompt.

## Execution ledger

Pre-flight: added the café, pharmacy and salon pack manifests (CP-1 needs a fixture shop per pack; salon's `'off'` must be quoted in YAML). All L1d tables live in `commerce_tables.py`; migration 0005 is a frozen copy generated from it (re-frozen once during the batch after a constraint-name collision: `invoices`/`tickets` unique constraints now carry explicit names).

RED evidence: Counter RED = `command.unknown_type` on all 13 tests before `register_counter`; Orders/Supply RED = `ModuleNotFoundError: arth.domains.orders/supply` (9 failing); Offers/Tax RED captured the expiry-test bug; Treasury RED found a real STF-3 gap (shift close ignored cash taken → `KeyError: expected_paise`), fixed by `treasury.shift_cash`. Deviation: Treasury, Offers, Tax, Trust, Capital and Sentinel modules were drafted before their test files (Counter's close path needed them); their tests were then run and every failure was fixed RED→GREEN.

Review fixes (spec first, then quality):
- ORD-1/ORD-5: accept/decline/substitute legality is checked when the gate is requested (context provider), so an illegal R3 never reaches the 30 s send queue; "check" lines block acceptance until resolved.
- TRU-5: after erasure the ledger statement must still compute — `account_ids`/`account_view` no longer require a live patron row; a full-database scan proves no name/VPA remains and the audit chain verifies.
- STO-1: in-stock uses `stock_tracked` (moves or batches exist), shared with Counter.
- Removed module-level clock singletons from offers/trust (clock passed explicitly).
- New invariant enforced at runtime: `Repository` refuses domain-table writes unless a bus command (or an outbox consumer) is executing — "every write via the bus" is now a guard, not just a test.

CP-1 (30 Oct 2026): `test_l1d_cp1.py` drives a fixture shop per pack (kirana, café, pharmacy, salon) through the real API (catalog, stock, bill, KOT, checkout, storefront, order, PO gate, sentinel) and validates 45 view payloads per pack against their schemas, the public storefront (price = catalog price) and `/v1/audit/verify`. `python dev.py gen-check lint typecheck` exit 0; **1175 pytest passed** (1 existing Starlette/httpx warning); **340 Vitest passed**.

Later-layer screens (Ask, Forecast, Grow*, Campaign, Ledger, Team, Run, Memory) return the schema-valid `layer_pending_view` naming the layer that fills them; their real read models replace it in L3–L6.
