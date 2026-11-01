# Arth: next-session handoff (31 Oct 2026)

## Status checklist

Done and verified by running the real app (fresh browser and/or live API) on 31 Oct 2026:

- [x] L0–L8 built (earlier sessions); full gate last run: 1352 passed, 2 failed → both fixed (contract list +
      openapi routes for `/v1/views/latest/{kind}`, `GET /v1/director/play`); full gate not re-run since the AI changes
- [x] Frontend talks to the backend in normal mode: auto live session (dev), no silent fixture fallback
      (red banner when the API is unreachable), CORS for any local origin, Next `allowedDevOrigins` 127.0.0.1
- [x] Stale/foreign session token replaced automatically; one session request per page load
- [x] Sim clock runs in dev, resumes after restart; Director freeze/run buttons
- [x] Detail screens without an id open the newest real record (`/v1/views/latest/{kind}`) or a designed empty state
- [x] UI at 80% zoom on desktop (fixed canvases scaled; stage iframes keep their slots)
- [x] Billing: new bill once, tap items, voice add/remove, hold/resume, cash, return, void, UPI QR → pay page → paid
- [x] Khata: credit sale from the bill (`checkout_khata`, R2), money received with amount (R2), voice payment,
      promises, reminders (consent enforced), consent withdraw only, language via PII-safe route, "New credit" → bill
- [x] Orders: full state machine on the order screen (place → accept → pack → deliver → settle), substitute picker
- [x] Learn (new item) is a real form; demand/bundle "add to catalog" build valid payloads
- [x] Approval (gate) screen works for every gate type (summary sentence), not only purchase orders
- [x] Every UI command payload and literal value checked against its contract (fixed `tapped`, return, KOT, undo…)
- [x] No raw i18n keys on screen: 212+ labels added, readable refusal messages, humanised fallback for gaps
- [x] Collections agent only for consented, undisputed, overdue accounts (E7.2); demo worlds seed reminder consent
- [x] Reorder playbook end to end (draft PO → owner haan → supplier short delivery → 3-way match → claim)
- [x] AI: Azure `renaiscent-gpt-5.4-mini` (Groq backup); pooled HTTP client; Sarvam Bulbul v4 Flash
      `priya_hi_recovery` TTS + Saaras v4 STT wired into the device dock
- [x] AI agent with tools for every module (`arth/ai/agent.py`): reads + actions via the Command Bus, chained
      actions, open-bill context, Grounding Guard with one repair round, answers open the matching screen with a caption
- [x] Verified prompts: billing with customer/items/cash/QR/khata, khata balance/payment/promise/reminder,
      stock info/receive/price, reorder with "did you mean", sales/compare/top/slow/busy hours, Diwali plan, greetings
- [x] `python dev.py demo`: saved kirana demo restores in ~2.5 s; Director picks it up ("Ready") and plays beats
- [x] Gen-check fixed (CRLF from git checkout; `.gitattributes` keeps LF); Prettier ignores `e2e-output/`

Still open (this session's tasks):

- [~] 1. Queries sometimes don't reach the AI — fixed in code, needs the 20-question fresh-browser check:
      on-screen phrases ("cash", "qr", "khate mein") stay local only on a screen that handles them (`handlesHere`
      in components/shell/device.tsx); dock waits for the live session ("Connecting…", `useLink` in lib/api/live.tsx);
      Azure timeouts 12 s (providers.yaml)
- [x] 2. Stage Trace / AI calls / Tools / Logs fill live (verified): per-turn `span_context` (core/spans.py) tags
      LLM/tool/policy spans with the shop + one trace; agent emits `tool.*` spans; evidence.tsx reads dur_ms/latency/cost
- [x] 3. Forecast works in the demo (verified): `python dev.py demo -- --fresh` builds in a clean DB in ~90 s
      (`arth/tools/build_demo.py`): 40 days of history, shop "Gupta General Store", Night Shift run, 3 reorder
      approvals waiting (beat 1.2 "Haan, teeno"); forecast 12 days ahead incl. Diwali 8 Nov; Director continues at 1.2
- [x] Collections no longer fail at night: quiet hours → wait till morning; other refusals end quietly
- [ ] 4. Full gate `python dev.py check` after the AI changes; fix regressions; update docs
- [ ] Known, lower priority: world build is slow and grows with shops in the DB (~7.5 min with 3 shops)

Paste the block below into a fresh Claude Code / Codex session opened at `C:\Users\kavya\Desktop\Hackathon\Paytm`.

```
You are continuing "Arth" (Paytm Hackathon 2026, Merchant Growth AI): an AI business partner on the Paytm
Soundbox for Indian kirana owners. Repo: C:\Users\kavya\Desktop\Hackathon\Paytm (Windows 11, Python 3.12,
Node 22, pnpm 10). All layers L0-L8 are built. Read docs/HANDOFF-NEXT.md (this file) fully first.

HARD RULES
- No git commands. Never open, print, cat or grep backend/.env or generated signing-key files.
- Use PowerShell for commands (faster here). Run uv as `python -m uv`. Use `python dev.py <target>`.
- Do NOT add new test cases. Prove each fix by running the real thing (API + a fresh browser), then fix
  what fails. Existing tests must keep passing (`python dev.py check` takes ~35 min; run it last).
- Contracts first: edit contracts/, then `python dev.py gen`. Never hand-edit backend/arth/contracts/*,
  frontend/lib/contracts/*, frontend/app/tokens.css.
- When writing files from shell heredocs, `\b`/`\n` inside Python strings get mangled (we found literal
  backspace chars twice). Prefer the Edit tool for regexes and escapes; afterwards scan for bytes 0x08/0x0C.
- Use Chrome DevTools MCP if it is connected; otherwise Playwright (installed, Chromium) via the scripts below.

HOW TO RUN
1. Terminal 1: `python dev.py api` (port 8000). Terminal 2: `python dev.py web` (port 3000).
2. `python dev.py demo` restores the saved Gupta Diwali kirana shop (snapshot `kirana-demo`, ~3 s);
   `python dev.py demo -- --fresh` rebuilds it (slow: minutes).
3. Stage: http://localhost:3000/stage . Director: http://localhost:3000/director (same browser; it says
   "Ready" and continues the restored scenario; press Next beat). Device: http://localhost:3000/device/home
4. Ask the AI from the terminal: `python -m uv run python -m arth.tools.ask "hi" "Priya ka bill banao, 2 Parle-G aur ek Maggi" "khate mein daal do"`
   (run in backend/; one session, carries the open bill between turns).
5. Fresh-browser module checks: `node frontend/scripts/module-check.mjs <ai|agent|billing|khata|stock|supply|orders|growth|money|agents|settings>`
   API flow check: `python -m uv run python -m arth.tools.flow_check` (backend/).
   Note: `uvicorn --reload` does not reload when the API is started from a console-less background shell;
   restart the API after backend edits.

WHAT WAS DONE LAST SESSION (do not redo)
- LLM: Azure OpenAI deployment `renaiscent-gpt-5.4-mini` is the main model (config/providers.yaml; keys
  AZURE_OPENAI_* in backend/.env), Groq backup, Mistral only for OCR. Sarvam: STT Saaras v4, TTS Bulbul v4
  Flash speaker `priya_hi_recovery`.
- AI agent: backend/arth/ai/agent.py = GPT function calling with ~30 tools (sales, payments, compare, top/slow,
  busy hours, item info, low stock, expiry, khata summary/aging/customer, lapsed, forecast, forecast_week,
  festivals, growth_options, pending, insights; actions add_to_bill(customer, items), bill_action
  (pay_qr/pay_cash/put_on_khata/remove_last/undo/park), record_khata_payment, send_khata_reminder,
  record_khata_promise, change_price, receive_stock, start_reorder, create_growth_plan, approve_pending,
  open_screen). Writes go through the Command Bus (R2/R3 become approval cards). Grounding Guard checks every
  number (owner-said numbers allowed; one repair round). backend/arth/ai/conductor.py `handle()` sends
  everything to the agent except `counter_command()` (instant counter commands on an open bill, "haan teeno").
- Frontend dock (frontend/components/shell/device.tsx `useTurnSubmit`/`AskDock`): sends turns to
  POST /v1/turns, shows the answer (Ask screen, or an `AnswerCaption` on the screen the answer opened),
  speaks with Bulbul via GET /v1/tts (frontend/lib/voice/sarvam.ts), mic records WAV for Saaras.
- Normal mode is live: lib/api/live.tsx `LiveBootstrap` takes a director session automatically in dev
  (red banner when the backend is unreachable); CORS allows any local origin in dev; next.config has
  allowedDevOrigins 127.0.0.1; sim clock runs in dev and resumes on restart; `/v1/views/latest/{kind}`.
- Verified working prompts (all modules): see the table in the previous session's final message; e.g.
  billing with customer + items + cash/QR/khata, khata payments/promises/reminders (consent enforced),
  stock receive/price change, reorder, sales/compare/top/slow/busy hours, Diwali plan, greetings.

TASKS FOR THIS SESSION (in order; verify each in a fresh browser before moving on)

1. "Sometimes the query doesn't go through; I type 'hi' first and then it works."
   Reproduce in a fresh browser (module-check style: type a question right after opening /device/home, and
   on several screens). Likely causes to check, in this order:
   a) frontend/lib/voice/intents.ts + `useTurnSubmit`: phrases matching an in-screen action intent
      (`action` without `screen`: "khate mein", "qr", "cash", "undo", "sab haan") are handled locally and
      never reach /v1/turns; off the bill screen nothing listens, so the query silently does nothing.
      Fix: only handle those locally when the current screen handles that action (bill/gate screens);
      otherwise send to the backend.
   b) First load: `LiveBootstrap` reloads the page after taking a session; a query typed before that reload
      is answered by the fixture intent table or lost. Fix: disable the dock (or queue the text) until the
      live session is ready, or avoid the reload by updating the data mode in place.
   c) `useTurnSubmit` awaits `speak()` (Bulbul) before returning; check a second question asked while the
      first answer is still speaking is not dropped (presence stuck at 'thinking'/'speaking').
   d) The API sometimes falls back when the model times out (llm.large timeout 4000 ms in
      backend/config/providers.yaml): check backend logs/`router.last_errors`; raise to ~8000 ms for the
      agent role if needed and keep the fast-path fallback.
   Done when 20 mixed first-try questions in a fresh browser all reach POST /v1/turns and show an answer.

2. Stage Trace and Logs panels are empty ("No spans yet").
   Files: frontend/screens/stage/evidence.tsx (Trace, Tools, AI calls, Logs tabs), frontend/lib/api/live.tsx
   `StreamConnector` (SSE /v1/stream: pushes `span` and other events into `useStream`), backend
   arth/core/spans.py (SpanBus), arth/api/stream.py, arth/ai/router.py `_span`, arth/governance/commands.py.
   Check: does /v1/stream emit `span` events for this merchant (curl it with a director session token while
   asking a question)? Does the stage page itself hold a live session (it is top-level, so LiveBootstrap
   runs) and open the stream? Are agent turns (new agent.py) and Command Bus writes emitting spans/events?
   Done when asking a question on the stage's device makes Trace (normalise → route → tools → write →
   compose → guard with latency), AI calls (provider/model/latency) and Logs (domain events, audit rows)
   fill live.

3. Forecast says "not enough history" in the demo shop.
   arth/intel/forecast.py `sales_forecast` needs >= 14 days with sales (`sufficient`), and the demo world
   (backend/scenarios/gupta_diwali/scenario.yaml `world.days`) has ~9 days. Give the demo shop at least
   35-45 days of history (raise world.days, or add a seed step that back-fills realistic daily bills), so
   forecast, forecast_week, compare_periods and "kal ke liye kya mangana chahiye" work. Then rebuild and
   re-save the demo: `python dev.py demo -- --fresh`. World building is slow and scales with the number of
   shops in backend/data/arth.db (it was ~7.5 min with 3 shops): if needed, build the demo into a clean
   data dir (ARTH_DATA_DIR) or speed up WorldBuilder. Check the scenario still plays (Director, all beats
   pass) and `python dev.py demo-check` for gupta_diwali, since beats may assert numbers that depend on the
   world. Also give the scenario world a shop name so the device says "Gupta General Store", not "Demo Kirana".
   Done when "kal ki bikri kitni hogi", "Diwali ke liye plan banao" and the Forecast screen show real numbers.

4. Finally run `python dev.py check` (expect ~35 min) and fix regressions; update docs/HANDOFF-L1.md /
   plan index briefly with what changed. Report results with the real output.
```
