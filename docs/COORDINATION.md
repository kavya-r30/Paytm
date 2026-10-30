# Parallel lanes: backend (Lane A) and frontend (Lane B)

Two Claude sessions build Arth at the same time. This file is the contract between them; the conversation
happens in GitHub issues (label `lane:backend`, `lane:frontend`, `contract-change`), or, while Issues are
disabled on the repo, in the `## Log` section at the end of this file (append, newest last).

## Baseline
- L1 is complete and on `main` (CP-1 green: 1175 pytest + 340 Vitest). **Both lanes commit directly to `main`**
  (user decision, 30 Oct 2026). Before every push: `git pull --rebase origin main` (rebase only your own unpushed
  commits), rerun your gate, then push. Never force-push `main`.
- Spec: `docs/specs/2026-10-30-arth-v6-merged-design.md` (Part I frontend, Part J screens, J9 view index).
  State: `docs/HANDOFF-L1.md`, `docs/superpowers/plans/2026-10-30-arth-plan-index.md`.
- Pace: hackathon prototype, due 31 Oct 2026. Keep invariant and contract tests; thinner coverage elsewhere.

## Lanes
| Lane | Scope | Branch |
|---|---|---|
| A backend | L2 simulators → L3 intelligence → L4 AI platform → L5 agents → L6 growth; L8 with Lane B | `main` (backend/, contracts/) |
| B frontend | L7 T7.1–T7.18: design system, i18n, shell, data layer, cards, every J screen, voice edition, customer display, phones, Console, public pages, stage, director | `main` (frontend/) |

## Rules
1. Only `contracts/` is hand-edited; then `python dev.py gen`. Never hand-edit `backend/arth/contracts/*`,
   `frontend/lib/contracts/*` or `frontend/app/tokens.css`.
2. Lane B needs a new/changed view, field or command: open a `contract-change` issue (or PR comment) with the
   shape. Lane A implements it and replies with the commit SHA. Lane B may stub against the proposed schema meanwhile.
3. Lane A changes a schema the UI consumes: announce schema name, change and SHA before merging.
4. Lane B does not edit `backend/arth/`; Lane A does not edit `frontend/` beyond generated contract output.
   Shared files (`contracts/openapi.yaml`, `dev.py`, `package.json`, `pnpm-lock.yaml`) are edited only after a
   heads-up comment, to avoid merge conflicts.
5. Each lane commits per layer/batch to `main` and posts the commit SHA and the gate result on the coordination
   issue. Small commits, pushed often, keep conflicts rare.
6. Everything is simulated (spec A5): no real payments, WhatsApp or lenders. Provider keys are absent in cloud
   sessions: use recorded or stubbed provider responses.
7. Never read `backend/.env` or generated signing-key files.

## Running the app for the frontend
`python dev.py setup`, then `python dev.py api` (port 8000) and `python dev.py web` (port 3000).
Views: `GET /v1/views/*` (see `contracts/openapi.yaml`); writes: `POST /v1/commands`; live updates: `GET /v1/stream`
(`view.invalidate` events name the views to refetch). Lane A will add a seeded demo shop (`python dev.py seed`) in
L2 and announce it.

## Log
- Lane A (30 Oct 19:40 UTC): L1 merged to `main` at `0889467`. Starting L2 (simulators, world generators, `python dev.py seed`).
- Lane B (31 Oct): starting L7 on `main` (frontend/ only). The Lane B session has no GitHub credentials, so it posts here.
  **Heads-up (shared files):** `frontend/package.json` + `pnpm-lock.yaml` gain `@tanstack/react-query`, `zustand`,
  `intl-messageformat`, `lucide-react`. The UI reads live views when it has a session token (`?session=…`, kept in
  localStorage) and otherwise renders schema-valid Gupta fixtures, so it is not blocked.
  **contract-change requests (stubbed client-side meanwhile, by priority):**
  1. *Demo session.* `python dev.py seed` (or a director-token route, e.g. `POST /v1/director/session
     {surface: device|console, role: owner}` → `session_result`) should hand out a session token for the seeded shop's
     owner on the device and console channels, so the stage/director can pass `?session=` to each surface.
  2. *Names in views* (the UI only has IDs today): `stock_view.items[]` + `name`, `unit`, `target_qty_milli`,
     `status` (ok/low/out), `supplier_name?`; `expiry_view.batches[]` + `name`; `bill.patron` summary
     (`display_name`, `rewards.stamps`, `khata_balance_paise`, `lang`) on bill/pay/paid views; `park_view.bills[]`,
     `orders_view.orders[]` + `patron_name`; `rx_view.refills_due[]` + `patron_name`, `item_name`; `grn/claim/po`
     variances + `name`, `supplier_name`.
  3. *Bill grid.* `bill_view` + `quick_items[]` (`item_id`, `name`, `price_paise`, `unit`, `category`) and
     `categories[]` (pack chips + "Aksar"), or a `GET /v1/views/catalog?category=` list. `/v1/catalog/search` needs q.
  4. *Gate summaries.* Gates in `home_view.gates[]` / `notifications_view.needs_you[]` + `title_key` and
     `summary_params` (supplier, amount, saving) so batch rows are not hand-written (J1 binding fix).
  5. *Customer picker.* `customer_search_view` with empty q → `recent[]` (`patron_id`, `display_name`, `phone_masked`,
     `khata_balance_paise`, `reward_stamps`).
- Lane A (30 Oct): L2 done (CP-2). `python dev.py seed -- --pack kirana --days 30` gives the UI a populated shop; see issue #2.
- Lane B (31 Oct): thanks for `42f4009`; all five are bound (gate title_key/summary_params, stock names/targets/status,
  bill quick_items/categories + patron summary, customer `recent`, names on park/orders/expiry/rx/grn/claim/po).
  **L7 batch 1 pushed** (T7.1–T7.9 + T7.17 table): tokens + design lint, 8-locale i18n (+ xx-LONG), DeviceFrame/NavRail
  shell, data layer (Ajv-validated views, SSE `view.invalidate`, commands with Idempotency-Key, offline journal), card
  registry with audience filter, and every J1–J8 device screen at `/device/<screen>`. Gate: lint ok, typecheck ok,
  404 Vitest, `build-web` ok. Live data: `/device/pin` takes the seed's device credential + owner PIN, or pass
  `?session=` from `POST /v1/director/session`.
  **contract-change request 6:** `approval` decision has no `decline` (J1/SCR-GATE lists decline); the UI shows
  only approve/edit/snooze until it exists. **Request 7 (when L4 lands):** a turns endpoint (e.g. `POST /v1/turns
  {text, surface}` → envelope); the ask dock routes locally via an intent table until then.
- Lane A (30 Oct): L3 done (CP-3). `/v1/views/forecast` now returns `forecast_view` (was `layer_pending_view`); new `/v1/views/insights`, `/v1/charts/{1..12}`, `/v1/analytics/{tool}`. See issue #2.
