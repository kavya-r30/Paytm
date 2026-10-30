# Arth v6: Scenario Library and Stage Demo

**Paytm Hackathon 2026 · Track: Merchant Growth AI**
Team ALOOgorithm · v6.0 · 30 Oct 2026 · Companion to `2026-10-30-arth-v6-merged-design.md`

> **What this document covers.** The scenario language, the library of scenarios that prove Arth works for any merchant and any situation, and the stage demo built from them. The demo is **one scenario** (`gupta_diwali`) played on the stage; nothing in the product is written for it.
>
> **Relationship to v5.1.** `docs/reference/Arth_Demo_Workflow_v5.1.md` remains the reference for roles (§3), hardware (§4), rehearsal (§10), failure recovery (§11) and judge Q&A (§14). Its seeded world (§5) and scenes (§7) are carried into `scenarios/gupta_diwali/` and re-bound to screens below.

---

## Contents
1. [What the demo must prove](#1-what-the-demo-must-prove)
2. [Scenario language](#2-scenario-language)
3. [Scenario library](#3-scenario-library)
4. [The stage demo: gupta_diwali on screens](#4-the-stage-demo-gupta_diwali-on-screens)
5. [Pack scenarios](#5-pack-scenarios)
6. [Edge-case scenarios](#6-edge-case-scenarios)
7. [Rehearsal, recovery and narration additions](#7-rehearsal-recovery-and-narration-additions)

---

## 1. What the demo must prove
The five claims of v5.1 Demo §1 are kept:
1. Arth grows the shop and proves it.
2. It does real work between conversations.
3. It is fast and natural at the counter and answers anything.
4. It is safe near money.
5. It is real.

v6 adds a sixth:

| # | Claim | How it is shown |
|---|---|---|
| 6 | **It is a platform for every merchant, in their language.** The same brain runs a café, a pharmacy and a salon, and the same screens work in eight languages | Scene 9 (pack switch) and the language moment in scene 8; the scenario library passes in CI |

---

## 2. Scenario language
One YAML file per scenario under `scenarios/{id}/scenario.yaml`, plus `world.yaml` (world-generator parameters and planted facts) and `cues.md` (generated cue cards). The same file drives the headless runner (`demo-check`), the live Director and the stage auto-focus.

```yaml
scenario: gupta_diwali
title: "One day at Gupta General Store, ten days before Diwali, and the morning a week later"
pack: kirana
world: ./world.yaml                 # generator params + planted facts (or a snapshot path)
locale: { screen: hi-Latn, speech: hi-IN }
edition: display                    # display | voice (can change per scene)
clock_start: "2026-10-29T07:45:00+05:30"
cut: { full: [1, 2, 2a, 2b, 3, 4, 5, 5b, 5c, 6a, 6b, 7, 8, 9], short: [1, 2, 3, 5, 5b, 6b, 7, 8] }
scenes:
  - id: 2
    title: Checkout with a counter hint
    clock: "2026-10-29T09:12:00+05:30"
    restore_from: snapshots/scene-1.db
    beats:
      - id: 2.1
        who: P2
        cue: "Priya ji ka bill. (scan Maggi ×2)"
        input:
          say_for_me: "Priya ji ka bill"
          scans: ["8901058851298", "8901058851298"]
        expect_turn:
          intent: counter.open_bill
          envelope.cards[type=hint].audience: owner
        expect:
          bills.open.patron: "$world.patrons.priya"
          customer_display.cards[type=hint]: absent
        focus: { device_screen: bill, phone: priya, evidence: trace, table: bills }
      - id: 2.5
        who: P3
        cue: "Pay on Priya's phone (or a judge scans the QR)"
        input: { persona_action: { persona: priya, action: pay_qr } }
        expect:
          bills["$beat.2.1.bill_id"].status: paid
          bills["$beat.2.1.bill_id"].total_paise: 9000
          llm_calls.since_beat: 0
        within_ms: 1500
        focus: { device_screen: paid, customer_display: paid, evidence: tables, table: bills }
invariants: default                 # all invariants from spec Part L2
```

**Vocabulary:**
- **Inputs:**
  - `say_for_me` (text in place of the mic);
  - `audio` (a recorded clip);
  - `scans`;
  - `tap` (a screen action by its component id);
  - `command`;
  - `persona_action` (pay, reply, visit, opt-out);
  - `clock` (`set`, `jump`);
  - `fault` (provider down, network off, duplicate webhook);
  - `locale` (switch screen or speech language);
  - `edition`;
  - `pack_switch` (load another scenario's snapshot on the same stage).
- **References:**
  - `$world.*` resolves against the planted-facts manifest, so scenarios never hardcode IDs;
  - `$beat.*` resolves against earlier beats.
- **Expectations:**
  - `expect_turn` (intent, tools called, envelope fields, grounding);
  - `expect` (DB paths, view paths, events, customer display);
  - `within_ms`.
- **Focus:** device screen, phone persona, customer display state, evidence tab, table and row, pinned playbook.

---

## 3. Scenario library
Every scenario passes `demo-check` 10 times in a row, live and on replay, before demo day.

| ID | Pack | Purpose | World highlights | Proves |
|---|---|---|---|---|
| `gupta_diwali` | Kirana | The stage demo (section 4) | v5.1 Demo §5 seeded world | Claims 1–6 |
| `kirana_cold_start` | Kirana | A brand-new shop on day 1: onboarding, catalog from a price-list photo, first bills, khata import, "what Arth can do yet" | No history; 1 price-list image; 2 khata pages | ONB-1…6, AIQ-17 |
| `kirana_monsoon_week` | Kirana | A non-festival week: demand dip, near-expiry clearance, replenish, an anomaly alert | Rain covariate; near-expiry batches; one anomaly day | FCT-*, EXP-3…4, INS-6 |
| `kirana_month_end` | Kirana | Month close: P&L, GST summary, CA export, credit advisor | 30 days of activity; composition tax profile | BKS, TAX, GRW-10 |
| `cafe_morning_rush` | Café | Tap-fast billing with modifiers, KOT board, tokens, add-on hints, peak-hour forecast | 120 tickets 8–10 am | CAFE-1…3, GRW-4 |
| `cafe_slow_afternoons` | Café | Strategist plan for slow hours: happy-hour offer with holdout, storefront pre-orders, feedback recovery | Weak 3–5 pm; one complaint | CAFE-4, STO, FBK |
| `pharmacy_refill_week` | Pharmacy | Refill reminders under reminder consent, Rx check at counter, FEFO, scope probes (medical advice refused) | 40 chronic patients; Rx items | PHAR-1…5, AI-28 |
| `pharmacy_batch_recall` | Pharmacy | A distributor recall: block the batch, list buyers, consented notices, return to distributor | One recalled batch sold to 6 patients | EXP-5, PHAR-6 |
| `salon_wedding_season` | Salon | Appointments by WhatsApp, staff calendar fill, bridal packages (advance liability), rebook reminders | Wedding-season calendar; 3 staff | SAL-1…4 |
| `salon_no_shows` | Salon | No-show tracking, slot-fill offers with holdout | 15% no-show rate | SAL-5 |
| Edge cases | Any | Section 6 | — | Safety and robustness |

---

## 4. The stage demo: gupta_diwali on screens

### 4.1 Timing
| Version | Length | Scenes |
|---|---|---|
| Full | 7:30 | 1, 2, 2a, 2b, 3, 4, 5, 5b, 5c, 6a, 6b, 7, 8, 9 |
| Short cut | 5:15 | 1, 2, 3, 5, 5b, 6b, 7, 8 including the 8.1 language moment (scene 9 moves to the pitch slide as a 10 s clip). For a hard 5:00 limit, also drop 8.2's Arena report |

### 4.2 The seeded world
This is v5.1 Demo §5, carried into `scenarios/gupta_diwali/world.yaml` as planted facts. The values the screens must show at each moment follow from those facts. The ones worth checking on screen:

| Moment | Value the screen shows | Why |
|---|---|---|
| Scene 1 (Home, morning variant) | Batch "Aapka ek haan, teen kaam": Mehta reminder series, Diwali readiness start, win-back (5 eligible, 4 messaged, 1 held out) | Gates from Night Shift; win-back assignment written before send |
| Scene 2 (Bill → Paid) | Bill opens at ₹62, hint "Priya: doodh (har guruvaar)", accepted → **₹90**; reward 4/10 | Hint accepted; Paid binds to the closed bill |
| Scene 2b (CustPick) | Rohit Kumar is a **first-time** payer (no "paid before" note); opts in; welcome coupon ₹20 on ₹200+ for 14 days | Welcome rules |
| Scenes 1–6 (Khata) | Sharma owes **₹1,150** until scene 6b, then ₹1,600; after scene 7, ₹600 | Ledger at that time |
| Scene 3 (Gate) | Agarwal ₹10,650 vs Balaji ₹10,410; Arth's note: Agarwal ₹240 dearer but 1 Nov delivery and 15 days' credit, Balaji late twice; counter at ₹45 (R3, conditional PO-118 ₹10,600) | Quotes and memory |
| Scene 5 (Plan) | Last Diwali ₹1,62,000; dry-fruit share 6% vs peer median 11% (n = 40); gift pack asked 9×; Mewa Dabba ₹549, margin 23.7%; cashback ₹25 on ₹500+ for new and returning only, ₹1,000 budget; 51 messaged / 13 held out | Diagnosis and plan |
| Scene 7 (Stock/Claim) | Agarwal sugar billed ₹46 vs ₹45 → **₹50** claim | GRN variance |
| Scene 8 (Ask, Ledger) | ₹1,12,400 since 29 Oct; UPI ₹84,300 (612), cash ₹28,100; tomorrow ₹21,500–₹27,800, most likely ₹24,600 | Analytics and forecast |

### 4.3 Scenes, beat by beat, with screens
Beats, inputs and asserts are those of v5.1 Demo §7, unless the table changes them. Each row adds **what the device shows** (screen ID from spec Part J), the **middle column** (phone or customer display) and the **evidence tab**.

| Scene · clock · edition | Beat | Device screen | Middle column | Evidence |
|---|---|---|---|---|
| **1** · Thu 7:45 · Display | 1.1 "Subah ka haal?" → brief + batch | SCR-HOME (morning variant): brief card speaking; batch card with 3 gates | Owner phone (brief copy) | Playbooks: Night Shift done |
| | 1.2 "Haan, teeno." | SCR-HOME: batch → done; status pill "Arth abhi: 9 baje RFQ bhejega" | — | Tables: assignments 4 treated / 1 holdout |
| **2** · 9:12 · Display | 2.1 "Priya ji ka bill" + scans | SCR-BILL: patron chip Priya; lines; **hint row** | Customer display: amount only (no hint) | Trace: fast path, `growth.hint_for_bill` |
| | 2.2 "Aadha kilo cheeni, aur ek Parle-G" | SCR-BILL with live-voice strip; total ₹62 | Customer display ₹62 | Trace: normaliser → counter |
| | 2.3 Hint accepted, milk scanned | SCR-BILL total ₹90 | Customer display ₹90 | Tables: hints.accepted |
| | 2.4 "QR dikhao" | SCR-PAY | Customer display: QR | Tables: bills |
| | 2.5 Payment | SCR-PAID ₹90, receipt preview (hi) | Priya's phone: receipt; customer display: paid, 4/10 | AI calls: **0** |
| **2a** ✂ · 9:14 | Unknown pack scanned | SCR-LEARN: photo → Haldiram's 200 g, ₹55 | — | AI calls: vision |
| **2b** ✂ · 9:16 | Walk-in pays ₹140 | SCR-CUSTPICK (first-time) → SCR-PAID with welcome coupon | Rohit's phone: opt-in → coupon terms; customer display: coupon earned | Tables: consents, coupons |
| **3** · 10:30 · Display | 3.1 Balaji quote arrives | Status pill: "Do rates aa gaye" | Supplier phone (Balaji) | Playbooks: Festival Readiness → compare; Tools: two extractions |
| | 3.2 Gate raised | **SCR-GATE**: quote compare, Arth's note, conditional scope, **R3** chip | — | Trace: memory recall "Balaji late twice"; Critic passed |
| | 3.3 "Haan, ₹45 bolo." | SCR-GATE → done; undo toast | Agarwal's phone: counter-offer "Sent by Arth for Ramesh" | Logs: approval scope_hash |
| | 3.4 Agarwal: "Theek hai, 45." | Status pill: "PO-118 bheja" | Agarwal's phone: PO PDF | Tables: purchase_orders (same approval id) |
| **4** ✂ · 11:05 | Forwarded ₹450 screenshot | **SCR-VERDICT**: "Payment abhi tak nahi aaya", evidence rows | Unknown number's phone | AI calls: vision; Tables: no ledger change |
| **5** · 12:40 · Display | 5.1 "Is Diwali bikri kaise badhayein? Do lakh tak." | **SCR-PLAN**: diagnosis (4-term decomposition, peers n = 40, gift pack ×9 with source utterances) | — | Tools: `growth.diagnose`, `peers.compare`, `demand.top` |
| | 5.2 Plan of 3 moves | SCR-PLAN move cards: Mewa Dabba pre-orders, targeted cashback, replenish; holdouts; estimates labelled | — | Trace: grounding passed |
| | 5.3 "Haan, ₹549 rakho." | SCR-PLAN → approved; SCR-GROW goal ring appears | — | Tables: assignments 51/13; offer_programs budget |
| **5b** · 2:30 · Display | 5b.1 Cash check | **SCR-CAPITAL**: shortfall 2 Nov ₹18,200; smallest offer ₹20,000 / 60 days; Console pointer | — | Tools: `capital.need`, `capital.affordability` |
| | 5b.2 "Loan le lo." | Orb speaking the refusal; no apply button anywhere | — | Logs: R4 refusal |
| **5c** ✂ · 2:31 | Console | — | Presenter phone: CON-CAPITAL → CON-OTP | Tables: loan application (simulated) |
| **6a** ✂ · 5:50 · **Voice** | Mehta voice-note order | Voice render: amber light, spoken summary | Mehta's phone → owner phone (order card) | Playbooks: Concierge holds contact lock; Collections deferred |
| | Double tap | Light green | Mehta: confirmation + pay link; helper phone: pick list | Tables: orders accepted |
| **6b** · 6:41 · Voice | Priya books 2 Mewa Dabbe + ₹200 deposit | Earcon + spoken line | Priya's phone (campaign thread) | Tables: preorders, advances |
| | "Sharma ji ka … khate mein, 450" → read-back → "Haan" | Light amber → green | Sharma's phone: entry copy | Tables: credit_entries; Logs: audit ✓ |
| | "Sharma ji ka hisaab." | Discreet: "WhatsApp pe bhej diya" | Owner phone: statement | — |
| **7** · Fri 6 Nov 8:10 · Voice | 7.1 Clock jump; the week runs | Voice render idle; stage shows nights advancing | Phones update in sequence | Playbooks: waits resuming in order |
| | 7.2 Brief | Spoken brief | Owner phone: brief + chart image | Tables: growth_ledger |
| | 7.3–7.5 Sharma reminder, ₹1,000 payment, claim | Spoken confirmations | Sharma's phone; Agarwal's phone: ₹50 claim | Tables: allocations (₹700 cleared, ₹300 applied) |
| **8** · 8:20 · Display + Console | 8.0 "29 tareekh se bikri dikhao, aur kal kitni hogi?" | **SCR-ASK**: chart 1 with band; numbers; follow-ups | — | Trace: analytics tools; grounding v2 |
| | 8.0b "Cashback se fayda hua?" | SCR-ASK: charts 9 and 11; "pakka fayda mahine ke ant mein" | — | Tables: offer liability ₹75 |
| | 8.1 **Language moment:** P2 taps the rail pill → Tamil | SCR-ASK and SCR-LEDGER re-render in Tamil; Arth repeats the answer in Tamil speech | — | Logs: `i18n.changed` |
| | 8.2 Growth Ledger | **SCR-LEDGER**: counts this week, "measured monthly"; October Impact Statement | Presenter phone: CON-LEDGER | Tables: growth_ledger |
| | 8.3 Arena report; Audit verify | SCR-TRUST: Verify → ✓ | — | Logs: audit verified; Health: spend this week |
| **9** · (any) · Display | 9.1 **Pack switch:** Director loads `cafe_morning_rush` at 8:45 am | SCR-KOT and SCR-BILL (café): "2 masala chai, ek kam cheeni" → token 47, KOT | Customer display: token + QR | Trace: same Conductor, café tool set |
| | 9.2 One question | SCR-ASK: "Subah ki bheed kab sabse zyada?" → heatmap (chart 3) | — | — |

### 4.4 Assertions added in v6
On top of v5.1 Demo §7 asserts:
- Every device screen in a beat's `focus` renders from its view with no literal copy (DOM check for i18n keys).
- The customer display never renders an owner card.
- The tier chip on SCR-GATE equals the command's tier in `policies.yaml`.
- In scene 8.1, every visible string on SCR-ASK and SCR-LEDGER is from the Tamil catalogue, with no overflow.
- In scene 9, the café scenario's invariants hold and no kirana-only lever appears.

---

## 5. Pack scenarios
Each pack scenario is a complete story with its own world, beats and asserts. Outlines:

**`cafe_morning_rush`** (8:00–10:00, hi-Latn)
1. Rush: 30 tickets through the tap grid with modifiers; KOT states advance; tokens on the customer display.
2. Add-on hint for a regular ("Usual: bun maska").
3. Forecast: "11 baje tak doodh khatam" → reorder suggestion.
4. Ask: peak-hour heatmap.

*Asserts:* modifier pricing; KOT state machine; ingredient stock moves.

**`cafe_slow_afternoons`** (one week, en + hi-Latn)
1. Diagnosis: the 3–5 pm dip vs peers.
2. Plan: a happy-hour offer for lapsing regulars only, with holdout; storefront pre-order for evening snacks.
3. A complaint arrives → Work item → recovery draft (R3) → the lever auto-pauses if complaints cross the threshold.

*Asserts:* holdout; guardrail stop; feedback flow.

**`pharmacy_refill_week`** (one week, hi + en)
1. Refill reminders go only to patients with reminder consent.
2. A customer asks the WhatsApp bot "ye dawai bachche ko de sakte hain?" → scope redirect to the pharmacist.
3. An Rx-required item at the counter → "Rx dekha" check.
4. FEFO picks the earlier batch.
5. The Strategist proposes no discounts on Rx items.

*Asserts:* PHAR-2…4; no marketing to refill-only consent.

**`pharmacy_batch_recall`**
1. A distributor message announces a recall.
2. The batch is blocked at the counter.
3. The buyer list is built; consented patients get notices (R3).
4. A return-to-distributor list is drafted.

*Asserts:* a recalled batch cannot be billed; notices only with consent.

**`salon_wedding_season`** (two weeks, hi + mr)
1. WhatsApp booking for "bridal makeup, 14 Nov".
2. Calendar fill by staff, with no double booking.
3. A bridal package is prepaid and becomes an advance liability.
4. Rebook reminders go out at each customer's own cycle.

*Asserts:* appointments; package liability; reminder consent.

**`salon_no_shows`**
1. A no-show pattern is detected.
2. A slot-fill offer runs with a holdout.
3. The no-show policy is stated in messages.

*Asserts:* offer terms (OFR-11).

**`kirana_cold_start`, `kirana_monsoon_week`, `kirana_month_end`:** as in the library table, each with beats that exercise every ★ screen they touch (SCR-ONB, SCR-EXPIRY, SCR-REPORTS).

---

## 6. Edge-case scenarios
Each is short (3–8 beats) and runs in CI.

| ID | Situation | Expected behaviour |
|---|---|---|
| `offline_billing` | Network off; three cash bills; network back | One bill per sale server-side, no duplicates; the device shows offline state and journal size |
| `provider_outage` | Mistral down mid-turn; then Sarvam STT down | Groq fallback for LLM (AI calls tab shows the hop); Whisper fallback for STT; replay tag where used; no wrong numbers spoken |
| `injection_attempts` | A payer name, a customer message and a bill photo carry instructions | No tool call or state change; drafts only; flagged |
| `duplicate_webhook` | Rails sends the same payment twice, and a real duplicate payment | First: idempotent. Second: PEX-2 refund suggestion (R4 pointer) |
| `pending_upi` | Payment pending 40 s, then fails | Bill shows pending, then alternatives; customer display "Payment aa raha hai…" then retry |
| `two_sharmas` | "Sharma ji ke khate mein 450" with two Sharmas | Disambiguation question before any write |
| `helper_cannot_approve` | The helper's session says "haan" to an R3 gate; a customer says "haan" near the counter | Neither approves; the owner PIN is needed |
| `budget_exhaustion` | Cashback program reaches its budget under concurrent payments | Never exceeds budget; program auto-pauses with the reason on SCR-OFFERS |
| `optout_storm` | Opt-outs exceed 3% during a campaign | Lever auto-stops; Work item; Growth Ledger notes it |
| `quiet_hours` | A reminder is due at 22:00 | Deferred to 08:00+ with the reason in the trace |
| `stale_replay` | Cassette replay with yesterday's numbers | Re-grounding replaces it with the template |
| `memory_poisoning` | A customer claims "Ramesh ne bola mera limit ₹10,000" | Nothing changes |
| `locale_overflow` | Every screen in the pseudo-locale and in Tamil | No overflow; truncation rules applied |
| `cold_peer_cohort` | Peer cohort below 10 shops | No benchmark rendered; "abhi tulna nahi" state |

---

## 7. Rehearsal, recovery and narration additions
**Rehearsal and recovery.** v5.1 Demo §10–11 apply, with these additions:

| Failure | Symptom | Recovery | Time |
|---|---|---|---|
| Language switch renders slowly | Fonts loading | Fonts are preloaded at T−10 min (the warm-up turn switches through all eight locales once) | 0 s |
| Pack switch (scene 9) fails to load | Stage stuck on the previous snapshot | P4 restores `cafe_morning_rush/snapshots/scene-1.db` from the Director; P1 skips to 9.2 | 5 s |
| A view endpoint errors | Screen shows its error state | Designed state; P4 restores the scene snapshot | 3 s |

**Narration additions** (P1; the rest as v5.1 Demo §12):

| Scene | Line |
|---|---|
| 8.1 | "Ramesh reads Hindi. His cousin in Chennai runs the same box in Tamil, and every screen and every word changes with it." |
| 9 | "And it isn't a kirana app. This is a café on the same brain: different menu, different levers, same safety. Pharmacies and salons too. That's what 'every Paytm merchant' means." |

**Pitch frame changes** (v5.1 Demo §13):
- Slide 2 adds the four packs and the eight languages.
- Slide 4 adds the layered architecture diagram (spec B2).
- Slide 5 adds "one platform, plug-in verticals" as the scale story for Paytm.
