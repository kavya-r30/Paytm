# Parallel lanes: backend (Lane A) and frontend (Lane B)

Two Claude sessions build Arth at the same time. This file is the contract between them; the conversation
happens in GitHub issues (label `lane:backend`, `lane:frontend`, `contract-change`), or, while Issues are
disabled on the repo, in comments on each lane's draft PR (PR #1 is Lane A's L1 PR).

## Baseline
- L1 is complete: CP-1 green (1175 pytest + 340 Vitest), commit `cff6247` on branch `claude/modest-cannon-38l5jl`
  (PR #1 into `main`). Both lanes start from that commit until PR #1 is merged, then from `main`.
- Spec: `docs/specs/2026-10-30-arth-v6-merged-design.md` (Part I frontend, Part J screens, J9 view index).
  State: `docs/HANDOFF-L1.md`, `docs/superpowers/plans/2026-10-30-arth-plan-index.md`.
- Pace: hackathon prototype, due 31 Oct 2026. Keep invariant and contract tests; thinner coverage elsewhere.

## Lanes
| Lane | Scope | Branch |
|---|---|---|
| A backend | L2 simulators → L3 intelligence → L4 AI platform → L5 agents → L6 growth; L8 with Lane B | `claude/modest-cannon-38l5jl` |
| B frontend | L7 T7.1–T7.18: design system, i18n, shell, data layer, cards, every J screen, voice edition, customer display, phones, Console, public pages, stage, director | `frontend/l7` (branched from `cff6247`) |

## Rules
1. Only `contracts/` is hand-edited; then `python dev.py gen`. Never hand-edit `backend/arth/contracts/*`,
   `frontend/lib/contracts/*` or `frontend/app/tokens.css`.
2. Lane B needs a new/changed view, field or command: open a `contract-change` issue (or PR comment) with the
   shape. Lane A implements it and replies with the commit SHA. Lane B may stub against the proposed schema meanwhile.
3. Lane A changes a schema the UI consumes: announce schema name, change and SHA before merging.
4. Lane B does not edit `backend/arth/`; Lane A does not edit `frontend/` beyond generated contract output.
   Shared files (`contracts/openapi.yaml`, `dev.py`, `package.json`, `pnpm-lock.yaml`) are edited only after a
   heads-up comment, to avoid merge conflicts.
5. Each lane commits per layer/batch, pushes its own branch, opens a draft PR into `main`, and posts the link and the
   `python dev.py check` result.
6. Everything is simulated (spec A5): no real payments, WhatsApp or lenders. Provider keys are absent in cloud
   sessions: use recorded or stubbed provider responses.
7. Never read `backend/.env` or generated signing-key files.

## Running the app for the frontend
`python dev.py setup`, then `python dev.py api` (port 8000) and `python dev.py web` (port 3000).
Views: `GET /v1/views/*` (see `contracts/openapi.yaml`); writes: `POST /v1/commands`; live updates: `GET /v1/stream`
(`view.invalidate` events name the views to refetch). Lane A will add a seeded demo shop (`python dev.py seed`) in
L2 and announce it.
