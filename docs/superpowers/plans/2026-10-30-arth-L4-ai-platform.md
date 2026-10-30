# Arth L4 AI Platform Implementation Plan (prototype pace)

> One batch, per-task review, commit to `main`. Hackathon prototype due 31 Oct 2026.

**Goal:** T4.1–T4.16: voice/text turns on every channel, with models that only route, read and phrase. Numbers come
from L3 tools, writes go through the bus at their tier, and every sentence is a template checked by the guards.

**Architecture:** `arth/ai/`. `router.py` holds role chains from `providers.yaml`: Mistral, Groq and Sarvam
adapters over httpx, per-hop timeouts, per-provider token buckets, data tags (merchant data never goes to
synthetic-only providers), cassette record/replay keyed by request hash, and spans with cost. `language.py`
normalises numerals, units, money and relative dates, and produces Indian number words for TTS. `fastpath.py` is
the deterministic grammar. `guards.py` holds the PII vault, Injection Shield, scope classifier, Grounding Guard
and Critic. `templates.py` holds the narration catalogue. `conductor.py` handles a turn and returns envelope v2.
`perception.py` does screenshot fields and order extraction with deterministic fallbacks. `prompts.py` is the
versioned registry. The persona LLM mode lives in `sim/personas.py`. HTTP: `POST /v1/turns`,
`GET /v1/views/ask` (the shared turn log, migration 0008), `GET /v1/tts`. `python dev.py ai-smoke` runs a live
call per role and records cassettes.

| Task | Evidence (`test_l4_ai_platform.py`) |
|---|---|
| T4.1 Router | live call via mock transport → cassette recorded → offline replay identical; 500 → fallback; rate limit; merchant data refused by synthetic-only provider |
| T4.2 Pinned models + smoke | `providers.yaml` pins; `python dev.py ai-smoke` (must run where providers are reachable) |
| T4.3 Prompt registry/evals | `prompts.py` versions; fast-path and probe sets in tests (LLM eval sets need live providers) |
| T4.4 Speech | Sarvam STT/TTS + Groq Whisper adapters; TTS normaliser: zero digits in spoken text |
| T4.5 Normaliser + fast path | quantities, money, relative dates; 20-case grammar set ≥ 95% |
| T4.6 PII vault | names/phones/VPAs masked before any model call, filled after; turn log stores masked text |
| T4.7 Shield | 20 injection probes flagged; a WhatsApp injection changes no state |
| T4.8 Conductor | shield → scope → fast path → model route → bus → templates → guards → envelope |
| T4.9 Grounding | unsupported numbers rejected; templates are grounded by construction |
| T4.10 Critic | hard rules: dignity, interest/late fee, medical, tax advice, fake urgency, misleading "free" (earned rewards allowed) |
| T4.11/12 Perception/extraction | screenshot fields from OCR text; order lines resolved against the catalog, unknowns flagged |
| T4.13 Narration | template catalogue hi-Latn/hi/en (others fall back to hi-Latn with locale numbers) |
| T4.14 Scope | medical and tax-advice probes → refusal templates |
| T4.15 Turns | same answer on device, console and WhatsApp; voice billing ("do kilo khuli cheeni", "hatao") |
| T4.16 Persona LLM | `PersonaEngine.reply_llm` with scripted fallback |

## Execution ledger

Blocker (environment): this cloud session's network policy denies `api.mistral.ai`, `api.groq.com` and
`api.sarvam.ai`, so no live call ran here. The adapters were tested against an httpx mock transport, and turns
use the spec's cassette and template fallback. The user's laptop has the keys in `backend/.env`. Lane B was asked
(issue #2) to run `python dev.py ai-smoke` and commit the recorded cassettes. CP-4's "every touchpoint passes its
eval on primary and backup" and the latency budget therefore stay open until providers are reachable.

Review fixes: "ek Parle-G" read the trailing G as grams (units must follow the number directly); the Critic flagged
an earned "10th visit: chai free"; the Shield missed "50% discount"; the SEN-3 scan allow-lists only the Critic's
rule table, which must name the word it blocks.

CP-4 (partial, 30 Oct 2026): offline gates green, **1246 pytest + 414 Vitest**; gen-check, lint and typecheck clean.
