# Arth: Demo Workflow v5.1

**Paytm Hackathon 2026 · Track: Merchant Growth AI · Offline round**
Team ALOOgorithm · Demo Workflow v5.1 · 30 Oct 2026

> **What this document covers.** This is *how we show Arth*: the story, who does what, the seeded world, every scene beat by beat, what the system must do at each beat, and how we recover when something goes wrong. The *what we build* is in `Arth_Spec_v5.1.md`; requirement IDs below (CTR-1, GRW-4, WFL-3 …) point into it.
>
> **About the UI.** This document describes what appears and changes on each surface, not how it looks. Visual design and layout come with the UI spec. The v4 mock images are reference only and predate the growth beats (e.g. the scene 2 bill is ₹62 there and ₹90 here).

---

## Contents
1. [What the demo must prove](#1-what-the-demo-must-prove)
2. [Format, timing and the stage](#2-format-timing-and-the-stage)
3. [Roles](#3-roles)
4. [Hardware and demo assets](#4-hardware-and-demo-assets)
5. [Seeded world](#5-seeded-world)
6. [Scene overview](#6-scene-overview)
7. [Scene-by-scene workflow](#7-scene-by-scene-workflow)
8. [Correctness invariants](#8-correctness-invariants)
9. [Scenario file and self-test](#9-scenario-file-and-self-test)
10. [Rehearsal plan and checklists](#10-rehearsal-plan-and-checklists)
11. [Failure recovery](#11-failure-recovery)
12. [Narration script](#12-narration-script)
13. [Pitch frame](#13-pitch-frame)
14. [Judge Q&A preparation](#14-judge-qa-preparation)

---

## 1. What the demo must prove
The judges should leave believing five things. Every scene serves at least one.

| # | Claim | Scenes |
|---|---|---|
| 1 | **Arth grows the shop, and proves it.** It finds growth leaks and acts on them (lapsing customers, run-outs, unmet demand, missing basket items, festival under-preparation), uses cashback and coupons only where they change behaviour, and shows results against holdouts | 1, 2, 2b, 5, 6b, 7, 8 |
| 2 | **Arth does real work between conversations.** Negotiation, collections and delivery checks run for days and wait on the world | 1, 3, 7 |
| 3 | **It is fast and natural at the counter, and answers anything about the shop.** Scan plus Hinglish voice; the bill closes itself when money lands; ask in chat and get numbers, a chart and a forecast range | 2, 6b, 8 |
| 4 | **It is safe near money.** Approvals are bound to exact scope, the Critic checks every message, fraud is caught by reconciliation, and no voice command or agent can take a loan | 3, 4, 5b, 6b, 8 |
| 5 | **It is real.** Live Sarvam calls, a self-testing scenario, a verifiable audit chain, and a visible cost | All, 8 |

---

## 2. Format, timing and the stage
- **Length:** 6:45 for the full run; a **5:00 cut** skips the scenes marked ✂. Both are timed and rehearsed.
- **Story:** "One day at Gupta General Store, ten days before Diwali, and the morning a week later." The sim clock starts at **Thu 29 Oct 2026, 7:45 am**.
- **The stage, by function** (layout in the UI spec):
  - **Left:** the device (Display or Voice edition), where Ramesh works.
  - **Middle:** whoever else is acting: the customer display, or the phone of a customer, supplier or helper.
  - **Right, the evidence:** running playbooks and their current step; the trace of the current run (model, tool, memory, gate, write); and the live tables (Bills, Khata, Orders, Quotes, Growth, Audit), each highlighting the row that just changed.
- **Auto-focus:** every beat in the scenario file sets the persona phone, the table tab, the highlighted row and the pinned playbook, so no one navigates the stage by hand.

---

## 3. Roles
| Person | Role | Never does |
|---|---|---|
| **P1** | Narrator. Speaks to judges, points at the stage, owns the timing | Touch any device |
| **P2** | Ramesh. Talks to Arth, scans packs, taps the device | Touch the Director |
| **P3** | Director. Advances beats on the presenter phone; types customer and supplier replies from the cue list; hands a phone to a judge for scene 2 | Speak to Arth |
| **P4** | Watch. Health panel, Work Board and assertions on the laptop; restores a scene snapshot if needed; takes technical questions | Present slides |

---

## 4. Hardware and demo assets
| Item | Required? | Purpose |
|---|---|---|
| Laptop (16 GB RAM) running everything | Yes | API, simulators, web, SQLite |
| HDMI to projector at 1920×1080 | Yes | Stage |
| Wireless handheld or lapel mic | Strongly recommended | Venue noise; push-to-talk keeps it controlled |
| Speaker (Bluetooth or venue PA) | Yes | Arth's voice must be audible |
| Presenter phone (Director) | Yes | Never on the projector |
| USB/Bluetooth HID barcode scanner (₹800–1,500) | Recommended | Live scanning |
| Real packs: Maggi, Parle-G, Amul Taaza, Haldiram's Aloo Bhujia (unknown barcode), Tata Salt (scene 2b) | Recommended | Physical moments in scenes 2, 2a and 2b |
| Mobile hotspot | Yes | Network backup |
| Android tablet in portrait | Optional | Device on real hardware |

**Demo assets:**
- Screenshot Forge set (genuine and edited ₹450 screenshots).
- Agarwal's delivered bill photo (sugar billed at ₹46).
- Cassettes for every scripted utterance and image.
- Scene snapshots `scene-0.db` … `scene-8.db`.
- The cue list printed for P3.

---

## 5. Seeded world
All values are planted by the deterministic generator (hash-checked).

**Shop and operations**
| Fact | Value |
|---|---|
| Shop | Gupta General Store, Lucknow. Owner Ramesh, helper Kiran |
| Night Shift, Wed 28 Oct | 3 payments matched, ₹20 cash short, brief prepared |
| Yesterday's sales | ₹8,450 (12% above a typical Wednesday) |
| Owner's stated limit | "Cheeni ₹45 se upar mat lena" (memory, owner-stated, 12 Oct) |
| Suppliers | **Agarwal Traders:** sugar ₹46/kg on last bill, 15 days' credit, on time. **Shree Balaji:** cheaper, cash only, late twice in festive 2025 (memory) |
| Quotes (scripted replies) | **Agarwal**, 10:21: sugar 46, kaju 780, badam 690, diya 2.50; delivery 1 Nov; 15 days' credit → ₹10,650. **Balaji**, 10:30: 44, 770, 680, 2.40; delivery 5 Nov; cash → ₹10,410 |
| Other Diwali purchase | FMCG restock from Sahu Distributors, ₹48,600, cash on delivery 2 Nov (placed by Ramesh on 27 Oct) |
| Cash-flow | Projected cash on 2 Nov is ₹30,400 against ₹48,600 due, a ₹18,200 shortfall. Agarwal's ₹10,600 falls due on 16 Nov thanks to credit (with Balaji's cash terms the gap would be ₹28,610) |
| Lender sandbox | Offers ₹20,000 / 60 days and ₹1,00,000 / 180 days |
| Delivered bill (1 Nov) | Agarwal billed sugar at ₹46 (agreed ₹45) → ₹50 variance |
| Unknown pack | Haldiram's Aloo Bhujia 200 g |

**Customers and khata**
| Patron | Facts |
|---|---|
| Priya Verma | Regular, 3/10 reward stamps; consented to receipts **and offers**; buys Amul Taaza 500 ml on 8 of her last 10 Thursdays |
| Rakesh Sharma | Khata: 21 Oct ₹700, 26 Oct ₹450, so ₹1,150 owed; limit ₹2,000; usually pays in 9 days; reliable for 12 months |
| Mehta family | Khata ₹2,150 since 21 Oct, limit ₹3,000; promise record: kept 3 of 3 |
| Imran Qureshi / Sunita Devi | ₹380 current / ₹90 on khata at 9:04 Thu (usually pays in 2 days) |

**Growth signals**
| Signal | Value |
|---|---|
| Last Diwali fortnight (2025) | Sales ₹1,62,000, gross profit ₹27,500 (17%) |
| Regulars / consented to offers | 118 regulars; **64** consented to offers |
| Lapsing regulars | 11 lapsing; **5** eligible (consented, high value): Kavita Singh, Arjun Rao, Neha Tiwari, Farhan Ali, Deepak Yadav |
| Replenish candidates this week | 9 patrons with a staple run-out due and a narrow band |
| Unmet demand (3 weeks) | "Gift pack / dry fruit box" asked **9** times; "brown bread" **5** times |
| Peer cohort | 40 synthetic Lucknow kiranas, same size band. Dry-fruit share of Diwali-fortnight sales: **you 6%, peer median 11%** |
| Slow mover | Soan papdi 250 g: 52 days of cover |
| Bundle | **"Diwali Mewa Dabba", ₹549:** kaju 200 g, badam 200 g, kishmish 100 g, soan papdi 250 g, 4 diyas, gift box. Cost ₹419, margin ₹130 (23.7%; floor 15%) |
| New walk-in (scene 2b) | Rohit Kumar, first payment ever from his VPA; opts in when asked |
| Standing offer | Welcome coupon: ₹20 off the next bill of ₹200+ (14 days), one per VPA/phone, issued with the opt-in receipt |
| Sales history for chat | The 8 days before the plan (21–28 Oct): ₹85,800. Owner chat in scene 8 compares like for like against it |

**Planted outcomes for the week (scripted replies and payments during the scene 7 jump)**
| Lever | Outcome |
|---|---|
| Win-back | 4 messaged → 3 return within 7 days (₹1,840 sales). Held-out 1 → did not return |
| Pre-orders | 51 messaged → **19 Mewa Dabba pre-orders** (₹10,431; deposits ₹1,900). Held-out 13 → 1 bought one in store |
| Replenish | 9 reminders → 5 orders (₹2,310) |
| Counter Hints | 41 hints shown, 17 accepted. Basket comparison against held-out bills is reported monthly |
| Diwali cashback program | 7 promises issued (3 returning, 4 new customers), 4 redeemed on a later ₹500+ bill: ₹100 paid of the ₹1,000 budget. Liability open: ₹75. Holdout comparison reported monthly |
| Welcome coupons | 6 issued, 2 redeemed (₹40) |
| Payments since the plan (29 Oct – 6 Nov, 8:00) | ₹1,12,400 in total: UPI ₹84,300 across 612 payments, cash ₹28,100 |
| Forecast for Sat 7 Nov | ₹21,500–27,800, most likely ₹24,600 (recent accuracy: ±9%) |
| Diwali goal | ₹1,12,400 of ₹2,00,000 sales by Fri 6 Nov, 8:00 am |

---

## 6. Scene overview
| # | Clock | Edition | Scene | Proves (spec IDs) | Time |
|---|---|---|---|---|---|
| 1 | Thu 7:45 am | Display | Morning: Night Shift results, growth snapshot, one approval batch (Mehta reminders, Diwali readiness, win-back) | PUL-1, WFL-4, GRW-1, GRW-5 | 0:30 |
| 2 | Thu 9:12 am | Display | Checkout: scan + voice, **counter hint**, exact-amount QR, auto-close, receipt | CTR-1/3/6, GRW-4, SRF-4 | 0:40 |
| 2a ✂ | Thu 9:14 am | Display | Scan-to-learn an unknown pack | CTR-8 | 0:20 |
| 2b ✂ | Thu 9:16 am | Display | **First-time customer:** opt-in receipt with a welcome coupon | GRW-11, OFR-4, OFR-10 | 0:15 |
| 3 | Thu 10:30 am | Display | Diwali quotes: parallel reading, counter-offer within limit, conditional approval, PO | WFL-2/3, MEM-1, E7.1 | 0:45 |
| 4 ✂ | Thu 11:05 am | Display | Forged payment screenshot caught by reconciliation | SEN-1/3 | 0:25 |
| 5 | Thu 12:40 pm | Display | **Growth plan:** diagnosis vs last Diwali and peers, demand capture, bundle and pre-orders, **targeted cashback program**, all with holdouts | GRW-1/3/8/9/12, OFR-1/2/8/9 | 0:45 |
| 5b | Thu 2:30 pm | Display | Cash check → right-sized, purpose-linked Capital offer; voice loan refused | CAP-2/3/5, F4.9 | 0:20 |
| 5c ✂ | Thu 2:31 pm | Console | KFS, cooling-off, OTP in Console | CAP-4 | 0:15 |
| 6a ✂ | Thu 5:50 pm | Voice | WhatsApp order; contact lock defers collections | ORD-1/3, WFL-5, WFL-10 | 0:30 |
| 6b | Thu 6:41 pm | Voice | **Pre-order arrives with a deposit**; credit by voice with read-back | GRW-9, LED-1/6 | 0:35 |
| 7 | Fri 6 Nov 8:10 am | Voice | **A week later:** the playbooks ran the week (growth results, promise to pay, part payment, delivery claim) | WFL-1/2, LED-5, GRW-13 | 0:45 |
| 8 | Fri 6 Nov 8:20 am | Console | **Ask Arth:** sales and payments with a chart and tomorrow's forecast range; cashback results; Growth Ledger and Impact Statement; Arena report; audit chain verified | CHT-1/2, INS-1/3, FCT-1, OFR-9, GRW-13, IMP-1, ARN-1, GOV-2 | 0:40 |
| | | | | **Full** | **6:45** |
| | | | | **Cut** (without 2a, 2b, 4, 5c, 6a) | **5:00** |

---

## 7. Scene-by-scene workflow
Each scene lists its starting snapshot, then the beats. A beat is one action and its expected system response. **Bold** marks what judges should notice. "Assert" is what `make demo-check` verifies headless.

### Scene 1: Morning (Thu 7:45 am, Display, 0:30)
**Start:** `scene-0.db`. Night Shift ran at 22:00, and a growth snapshot was computed.

| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 1.1 | P2 | "Subah ka haal?" | Brief (grounded): yesterday ₹8,450 (+12%); 3 payments matched, ₹20 cash short; Diwali gap in dry fruits and diyas; "**5 purane regular grahak kaafi din se nahi aaye**". Then one batch: "Mehta ji ko 9 baje yaad dilaun, aur jawab na aaye to har hafte, teen baar tak? Diwali ki taiyari shuru karun? Aur in 5 ko wapas bulane ka message bhejun?" | Every number ∈ tool outputs; batch has 3 gates (R3 series, R1 start, R3) |
| 1.2 | P2 | "Haan, teeno." | **Three playbooks start:** Collections (Mehta, series approval), Festival Readiness (RFQs timed for after 9:00), Win-back (5 eligible → **4 messaged, 1 held out**, sends at 9:00 because of quiet hours) | 3 runs; `assignments` has 4 treated + 1 holdout *before* any send |

### Scene 2: Checkout with a counter hint (Thu 9:12 am, Display, 0:40)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 2.1 | P2 | "Priya ji ka bill." Scans Maggi ×2 | Bill opens for Priya Verma; Maggi ×2 ₹28. **Owner-only hint: "Priya: doodh (har guruvaar)"** | Hint in envelope with `audience: owner`; not on the customer display |
| 2.2 | P2 | "Aadha kilo cheeni, aur ek Parle-G." | Sugar 0.5 kg ₹24, Parle-G ₹10 (quantities and amounts computed by Counter) | Lines and total ₹62 |
| 2.3 | P2 → P3 | Ramesh asks Priya, "Doodh bhi?" P3 (as Priya): "haan". P2 scans Amul Taaza | Line ₹28 → **total ₹90**; hint marked accepted | `hints.accepted = true` |
| 2.4 | P2 | Taps "QR dikhao" | Exact-amount dynamic QR on the customer display | QR order_ref = bill id |
| 2.5 | P3 / judge | Pays on Priya's phone, or a judge scans the projector QR | Signed webhook → bill closes → receipt to Priya → reward stamp 4/10 → "Nabbe rupaye mil gaye. Bill band." **0 model calls, ₹0** | Bill Paid within 1.5 s; Σ payments = total |

### Scene 2a ✂: Scan-to-learn (Thu 9:14 am, 0:20)
P2 scans the Haldiram's pack → "Ye naya hai" → pack photo → "Haldiram's Aloo Bhujia 200 g, MRP ₹55. ₹55 rakhun?" → "haan" → item saved, barcode linked, line added. **Assert:** new item with GTIN; CTR-8 under 10 s.

### Scene 2b ✂: First-time customer (Thu 9:16 am, Display, 0:15)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 2b.1 | P2 | Scans Tata Salt and two more items for a walk-in (₹140); QR | Bill closes on payment. **First payment from this VPA** → receipt with "Bill aur offers WhatsApp pe chahiye? 'Haan' likhiye" | `patron_metrics.lifecycle = new` |
| 2b.2 | P3 | (as Rohit) replies "Haan" | Consent stored (receipts + marketing, source: receipt). **Welcome coupon: ₹20 off the next bill of ₹200+, 14 days**, with terms | One coupon per VPA hash (a second payment from the same VPA issues none); terms present (OFR-11) |

### Scene 3: Diwali quotes and negotiation (Thu 10:30 am, Display, 0:45)
**Start:** Agarwal's 10:21 reply is already in. The panel shows Festival Readiness at "Wait for quotes".

| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 3.1 | P3 | Sends Balaji's quote from the supplier phone | Wait resumes. **Two quotes are read in parallel** (AI-15), memory recall ("Balaji late twice"), and a deterministic compare | Both quotes extracted; scores computed in code |
| 3.2 | — | (automatic) | Quote comparison sheet with Arth's note: "Agarwal ₹240 mehenga, par Diwali se 7 din pehle aur 15 din udhaar; Balaji pichhle festive mein do baar late." Counter-offer drafted within the ₹45 limit; Critic passed; **amber gate: "Agarwal ko ₹45 kilo cheeni par mana lun?"** | Gate scope: counter ₹45 **and** "if accepted ≤ ₹45, place PO-118 ₹10,600" |
| 3.3 | P2 | "Haan, ₹45 bolo." | Message to Agarwal, "Sent by Arth for Ramesh" | Approval `scope_hash` stored |
| 3.4 | P3 | (as Agarwal) "Theek hai, 45." | AI-16: accept at 45 → condition met → **PO-118 placed without asking again**; PO sent to Agarwal | PO total ₹10,600; same approval id |

### Scene 4 ✂: Forged screenshot (Thu 11:05 am, Display, 0:25)
P3 forwards a ₹450 "payment successful" image from an unknown number → AI-11 extract → reconcile → "**Payment abhi tak nahi aaya.** UTR match nahi hua, payee alag." Evidence is listed, and nothing accuses anyone. **Assert:** verdict `not_received`; no ledger change; no string contains "fake".

### Scene 5: The growth plan (Thu 12:40 pm, Display, 0:45)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 5.1 | P2 | "Is Diwali bikri kaise badhayein? Do lakh tak le jaana hai." | Strategist runs a Growth Plan. **Diagnosis** (AI-20, grounded): "Pichhli Diwali ₹1,62,000. Grahak utne hi hain, par 11 regulars kam aa rahe hain. Dry fruits ka hissa aapke yahan 6%, aas-paas ki 40 jaisi dukano mein 11%. **Gift pack 9 baar maanga gaya, aapke paas nahi.**" | Decomposition sums exactly; peer cohort n = 40 ≥ 10; demand cluster cites 9 utterances |
| 5.2 | — | (automatic) | **Plan of 3 moves**, each sized as an *estimate*: (1) "Diwali Mewa Dabba" ₹549 (bundle builder: margin 23.7%, clears soan papdi), pre-orders to 64 consented regulars with ₹100 deposit, 20% held out; (2) **Diwali cashback: ₹25 back on the next ₹500+ bill, only for new and returning customers (regulars excluded: they come anyway), ₹1,000 budget, 20% held out**, alongside the win-back already running; (3) replenish reminders for 9 patrons due | Bundle ≥ margin floor and within stock; offer segments = [new, reactivated]; holdout share 0.2 |
| 5.3 | P2 | "Haan, ₹549 rakho." | Approves the bundle price (R2), the **plan scope** (R3: levers, templates, audience cap 64, end date 8 Nov) and the **cashback program with its ₹1,000 budget** (R3). Campaign scheduled for 6:00 pm; **51 to be messaged, 13 held out** | Plan scope hash; `assignments` 51/13 written before send; `offer_programs.budget_paise = 100000` |

### Scene 5b: Purpose-linked Capital (Thu 2:30 pm, Display, 0:20)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 5b.1 | — | Festival Readiness reaches "Order and cash check" | "2 Nov ko ₹18,200 kam pad sakte hain. Agarwal ke 15 din ke udhaar se ₹10,600 baad mein jayenge." Offer card shows the smallest offer that closes the gap: **₹20,000 / 60 days**, purpose: Diwali stock | Offer = smallest closing amount; all display fields present |
| 5b.2 | P2 | "Loan le lo." | "Loan ka faisla Console mein, OTP ke saath hota hai. Main apply nahi kar sakta." | No apply tool exists; R4 refusal logged |

### Scene 5c ✂: Console (Thu 2:31 pm, 0:15)
P3 opens the Console on the presenter phone: KFS, APR, repayment (EDI), cooling-off, OTP `123456`. **Assert:** CAP-4 fields present; disbursal scheduled for the next settlement.

### Scene 6a ✂: WhatsApp order (Thu 5:50 pm, Voice, 0:30)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 6a.1 | — | Device flips to the Voice edition | — | — |
| 6a.2 | P3 | Mehta family sends an order (voice note) | Concierge drafts 4 lines, ₹386, **takes the contact lock**; Collections logs "order open: no reminders until it closes". Earcon + "Naya order, Mehta ji, 4 cheezein, ₹386" | Lock held by Concierge |
| 6a.3 | P2 | Double tap | Order accepted (R3) → Mehta gets a confirmation and pay link → Kiran gets a pick list | Order Accepted; 2 messages sent |

### Scene 6b: A pre-order lands; credit by voice (Thu 6:41 pm, Voice, 0:35)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 6b.1 | P3 | (as Priya) replies to the 6:00 pm campaign: "2 dabbe chahiye", then pays the ₹200 deposit link | Within the plan scope, so no approval needed: pre-order created, deposit credited. Earcon + "**Priya ji ne do Mewa Dabbe book kiye, ₹200 advance mila.**" | `preorders` +1 (qty 2); Growth Ledger action recorded |
| 6b.2 | P2 | "Sharma ji ka aaj ka saamaan khate mein daal do, 450 ka." | Read-back "Sharma ji, chaar sau pachaas, khate mein?" → amber light | R2 gate open |
| 6b.3 | P2 | "Haan." | Entry saved; green; Sharma gets a copy | Owed ₹1,600; audit verifies |
| 6b.4 | P2 | "Sharma ji ka hisaab." | Discreet mode: "WhatsApp pe bhej diya" | Envelope `sensitivity: discreet` |

### Scene 7: A week later (Fri 6 Nov 8:10 am, Voice, 0:45)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 7.1 | P3 | Jump to Fri 6 Nov 08:10 | **The playbooks run the week**, night by night: win-back returns arrive (and earn cashback promises); pre-orders accumulate to 19; 4 cashback payouts happen on later ₹500+ bills; Agarwal delivers on 1 Nov and the delivery check finds sugar billed ₹46 vs ₹45 (₹50 claim gate); Mehta's touch 2 goes out Thu 5 Nov under the series approval; at 7:52 today Mehta replies "somvaar ko de dunga", which is classified as a promise, acknowledged, and put to sleep until Mon 9 Nov | Waits resumed in order; no send in quiet hours except the in-window reply |
| 7.2 | — | Brief | "**Is hafte: 3 purane grahak wapas aaye. 19 Mewa Dabbe book hue. Diwali goal ka 56%.** Mehta ji ne somvaar ka vaada kiya. Sharma ji ko yaad dilaun? Agarwal par ₹50 ka claim?" | Numbers match `growth_ledger` and tables |
| 7.3 | P2 | "Sharma ko haan." | Reminder with pay link to Sharma (Critic passed) | Scope hash = reminder:Sharma |
| 7.4 | P3 | Pays ₹1,000 on Sharma's phone | Oldest-first allocation: 21 Oct ₹700 cleared, ₹300 of 26 Oct. "**Sharma ji ne hazaar rupaye diye. Ab chhe sau baaki.**" | Owed ₹600; allocations correct |
| 7.5 | P2 | "Claim bhej do." | ₹50 claim message to Agarwal (R3, approved by this utterance) | Claim recorded against PO-118 |

### Scene 8: Ask Arth, and proof (Fri 6 Nov 8:20 am, Console, 0:40)
| Beat | Who | Action | Arth / system | Assert |
|---|---|---|---|---|
| 8.0 | P2 | Types in Console chat (or WhatsApp): "29 tareekh se bikri dikhao, aur kal kitni hogi?" | **Chart 1** (daily sales, 4 weeks, with the forecast band) and the answer: "29 Oct se ₹1,12,400, usse pehle ke 8 din se 31% zyada. UPI ₹84,300 (612 payments), cash ₹28,100. **Kal ₹21,500 se ₹27,800 ke beech, sabse zyada sambhavna ₹24,600.**" Two follow-ups offered | Numbers = analytics tools; forecast shown as a range; Grounding Guard v2 passed |
| 8.0b | P2 | Taps the follow-up "Cashback se fayda hua?" | **Chart 9 / 11:** 7 promises issued, 4 redeemed, ₹100 spent of ₹1,000; "pakka fayda mahine ke ant mein, holdout se tulna karke" | Liability = issued − redeemed − expired (₹75 open) |
| 8.1 | P4 | Opens the Growth Ledger | **This week, as counts:** win-back 3 of 4 returned (held-out 0 of 1); pre-orders 19 from 51 (held-out 1 of 13 bought in store); replenish 5 of 9; hints 17 of 41 accepted; cashback 4 of 7 redeemed; welcome coupons 2 of 6. Labelled "**measured monthly**". **October Impact Statement:** measured win-back uplift vs 20% holdout with a 90% CI; direct (fraud blocked, overcharge claimed, credit recovered); estimated (stock-outs avoided) | Every figure reproducible from tables |
| 8.2 | P4 | Opens the Arena report | pass^4 per playbook and persona, including the injection persona failing to change any balance and the "opts-out" persona never messaged again | Report from last run present |
| 8.3 | P4 | Clicks Audit → Verify | **Chain verified ✓.** Rail shows AI spend this week | `audit.verify = true` |

---

## 8. Correctness invariants
These are checked after every beat, in rehearsal and in CI.
- **Bills:** Σ payments + khata = total. No bill is both Paid and OnCredit.
- **Khata:** balance = Σ entries − Σ allocations, never negative unless it is an advance.
- **Stock:** on-hand = Σ moves.
- **Audit:** the chain verifies.
- **Messaging:** no outbound message without a matching consent purpose. No Arth-initiated message in quiet hours.
- **Grounding:** every narrated number is grounded.
- **Approvals:** every executed agent command has a matching `scope_hash`, or a tier that needs none.
- **Contact locks:** no outbound message to a subject whose lock is held by another run.
- **Waits and budgets:** every open wait has a deadline; no run exceeds its agent budget.
- **Holdouts:** they are never messaged. Assignments precede sends.
- **Marketing cap:** ≤ 1 marketing message per patron per week across all levers.
- **Hints:** never present on the customer display envelope.
- **Offers:**
  - a program's spend never exceeds its budget;
  - liability = issued − redeemed − expired;
  - at most one welcome coupon per VPA hash and phone;
  - cashback is always requested against a payment reference;
  - owner and staff VPAs are never rewarded.
- **Approvals:** every R2/R3 approval comes from an owner push-to-talk turn or an owner surface.
- **Cross-surface consistency:** numbers on the device, phones, chat and tables agree within each scene.

---

## 9. Scenario file and self-test
One YAML file per scene drives both the live Director and the headless test. Excerpt for scene 5:

```yaml
scene: 5
title: The growth plan
clock: "2026-10-29T12:40:00+05:30"
edition: display
restore_from: snapshots/scene-4.db
beats:
  - id: 5.1
    cue: "P2: Is Diwali bikri kaise badhayein? Do lakh tak le jaana hai."
    say_for_me: "Is Diwali bikri kaise badhayein? Do lakh tak le jaana hai."
    expect_turn:
      intent: growth_goal
      tools_called: [growth.diagnose, peers.compare, demand.top]
      envelope.speech.text~: "gift pack"
      grounding.passed: true
    expect:
      growth_plans.last.status: needs_you
      peer_cohorts[lucknow_kirana_m].n_shops: 40
      demand_clusters[gift_pack].count_3w: 9
    focus: { tab: growth, pin_playbook: "growth_plan:diwali" }
  - id: 5.3
    cue: "P2: Haan, ₹549 rakho."
    expect:
      bundles[mewa_dabba].price_paise: 54900
      bundles[mewa_dabba].margin_paise: 13000
      growth_levers[preorder].audience_cap: 64
      assignments[preorder]: { treated: 51, holdout: 13 }
      messages.sent_after: "2026-10-29T18:00:00+05:30"
      audit.verify: true
```

**Running it:**
- `make demo-check` runs every scene headless, using `say_for_me` text instead of the microphone, and asserts every `expect` plus the invariants in §8.
- It must pass **10 consecutive runs** before demo day.
- Cassettes let it run offline.

---

## 10. Rehearsal plan and checklists
**Rehearsal plan:**
| When | What |
|---|---|
| Day −3 | First full run with live AI; note every beat over its time |
| Day −2 | Cut-version run; failure drills (§11), each once |
| Day −1 | 3 timed full runs, 2 timed cuts; `make demo-check` × 10 green; cassettes refreshed |
| Demo day | One warm-up turn; no code changes after T−3 h |

**Day before:**
- Projector test at 1920×1080.
- Mic and speaker levels.
- Packs labelled in order.
- Phones charged.
- Sponsor credits confirmed.
- Cue list printed.

**T−60 min:**
- `make demo-reset`.
- Laptop on mains, notifications off.
- Hotspot ready.
- Browser zoom 100%, kiosk mode.
- Director on P3's phone.

**T−10 min:**
- Warm-up turn ("Test") to prime STT/TTS.
- Verify AI calls show **Live**.
- Restore `scene-0.db`.

**T−1 min:** Director on beat 1.1. P2 holding Maggi.

---

## 11. Failure recovery
Rehearse each once.

| Failure | Symptom | Recovery (owner) | Time |
|---|---|---|---|
| STT mishears or times out | Re-ask or wrong caption | P3 taps "Say it for me" (same beat text) | 3 s |
| Sarvam slow or down | Spans show fallback or "replay" | Automatic; P1 mentions fallback as a feature | 0 s |
| Venue network down | Many replay spans | Switch to hotspot; replay mode keeps the flow | 10 s |
| Wrong state after a mistake | Assertion warning on the Director | P4 restores the current scene snapshot | 3 s |
| Browser crash | Blank stage | Reload; state comes from the server | 5 s |
| Scanner not reading | No line added | P2 taps the item in Items | 3 s |
| Judge's phone can't reach the tunnel | Pay page doesn't load | P3 pays on the on-screen phone | 5 s |
| A playbook doesn't resume after a scripted reply | Step stays "waiting"; Director shows an unmatched event | P4 taps "Re-match" (replays the event through the Event Matcher), or restores the scene | 5 s |
| A supplier reply is mis-read | Quote line marked "confirm" | P2 says "haan, 44 hai"; P1 calls it the safety net working | 5 s |
| Hint doesn't appear in scene 2 | No hint line | P2 still asks "doodh bhi?"; P1 skips the hint line in the narration; the scene still works | 0 s |
| Growth plan narration fails grounding | Template narration appears instead | Expected behaviour; continue | 0 s |
| Arena report missing | Empty report page | Show the last committed report | 3 s |
| Chart image fails to render | Text answer without chart | Expected degradation; the numbers are still there; continue | 0 s |
| Cashback payout delayed by the simulator | Promise stays "due" | P4 retries the payout from the Director (idempotent on program + payment ref) | 3 s |

---

## 12. Narration script
P1's lines. Everything else is the product talking.

| Scene | Line |
|---|---|
| Open | "Ramesh runs a kirana in Lucknow. Quick commerce is taking his top-up customers. He doesn't need another dashboard; he needs a partner that does the work and grows the shop. This is Arth, on the Paytm Soundbox." |
| 1 | "Overnight, Arth closed his books. This morning it asks one question with three answers in it: chase a due, prepare for Diwali, and bring back five regulars who drifted. One of the five is held back on purpose, so we can measure whether messaging works." |
| 2 | "At the counter: scan and speak. See the quiet line only Ramesh sees: Priya buys milk every Thursday. Ramesh asks, she says yes, and the basket grows from ₹62 to ₹90. The bill closes itself when the money lands, with no AI call needed." |
| 3 | "While Ramesh served customers, Arth asked two suppliers for quotes. It read both replies at once, remembered which supplier was late last Diwali, and counter-offered within the limit Ramesh set. One yes covered the counter-offer and the order." |
| 5 | "Now growth. Arth compares this Diwali with last year's and with 40 similar shops: the street is asking for gift packs, and he has none. So it builds one from stock he's already ordering, at a margin above his floor, and offers it to customers who opted in. It adds cashback, but only for new and returning customers, because paying regulars to come back is just a discount. Every move has a holdout, so the result is real." |
| 5b | "The order creates a cash gap on 2 November. Arth shows the smallest loan that closes it and what it's for, and it cannot apply. That happens only in the app, with OTP." |
| 6b | "Evening, on the screenless edition. A customer books two gift boxes and pays the advance; Arth just tells him. Then credit by voice, read back before it's saved." |
| 7 | "A week later. Ramesh spoke to Arth for maybe a minute about money this week. In that time three lost regulars came back, 19 gift boxes were booked, a supplier overcharge was caught, and a customer promised to pay on Monday, so Arth will wait until then. Every message that left the shop, he approved." |
| 8 | "Ramesh can ask anything. This week's sales, by payment mode, with tomorrow as a range, not a guess. And it proves itself: growth and cashback against holdouts, measured monthly; every playbook tested against simulated customers before it ran; and an audit chain anyone can verify." |

---

## 13. Pitch frame
Five slides around the demo.
1. **The problem in Ramesh's words:**
   - five ledgers, one head;
   - customers drifting to apps;
   - no time to chase anyone.
2. **What Arth is:** the three jobs (run the shop, do the follow-through, grow the shop) and the two editions.
3. **Live demo** (§6–7).
4. **How it works and why it is safe:**
   - the three loops;
   - the growth equation and holdouts;
   - scope-bound approvals and the Critic;
   - Arena pass^4;
   - "no apply tool exists".
5. **Why Paytm wins:**
   - merchant retention;
   - UPI volume from re-engagement;
   - lending against visible demand;
   - peer benchmarks only Paytm can offer;
   - cost per merchant per day;
   - roadmap.

---

## 14. Judge Q&A preparation
| Likely question | Answer (short) |
|---|---|
| "Isn't this just a chatbot on a soundbox?" | It has a chatbot (owner chat with charts, customer chatbot on WhatsApp), but that's the smallest of three loops. Show scene 7: the week ran itself, with approvals |
| "Why not just give everyone cashback?" | Most of it would go to regulars who'd come anyway. Arth targets new and returning customers, holds out 20%, and reports ROI net of the cashback cost |
| "How do you stop cashback abuse?" | Owner and staff VPAs excluded; one welcome coupon per VPA and phone; payments within 10 minutes combined; refunds claw back; budgets reserved atomically |
| "Can a customer approve something by saying 'haan'?" | No. Approvals count only inside the owner's push-to-talk turn or on owner surfaces; staff have role limits |
| "How do you know growth isn't coincidence?" | Holdouts assigned before sending; uplift reported with a CI, monthly; this week's numbers are shown as counts only |
| "Won't customers find the messages spammy?" | 1 marketing message per patron per week across all levers; consent per purpose; replenish and "aa gaya" messages are useful by design; auto-stop on opt-outs; WhatsApp also caps marketing per user |
| "Where do peer benchmarks come from?" | In production, Paytm's merchant base: percentiles only, cohorts of ≥ 10, with noise. Here, a labelled synthetic cohort of 40 |
| "What if the LLM invents a number?" | The Grounding Guard replaces the narration with a template; numbers come from tools only |
| "Can an agent take a loan or send money?" | No apply tool exists; R4 is Console-only with OTP; agents' tier ceilings are below R4 |
| "What does it cost?" | Shown live on the rail; the back office runs under ₹1 per merchant per day at list prices; most counter actions use no model call |
| "What's real vs simulated?" | Real: Sarvam AI, agents, ledger, models. Simulated and labelled: Paytm rails, WhatsApp transport, lender, history, peer cohort |
| "Why will this survive outside a demo?" | Durable playbooks (restart mid-wait in front of you if asked), idempotent side effects, a self-testing scenario in CI |
| "Why Sarvam?" | Hinglish STT (Saaras codemix), fast Indic TTS (Bulbul v4 Flash), Sarvam-105B for tools and JSON, Vision and Document AI for bills and screenshots |
