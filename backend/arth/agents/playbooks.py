"""Playbooks (T5.7–T5.12). Each proposes through the bus; owners answer R2/R3 gates; nothing is sent twice.

Triggers: Night Shift runs at 22:00 IST; event triggers start Concierge (`message.in`), Feedback
recovery (`feedback.recorded` low), Batch recall (`batch.recalled`). Night Shift starts Reorder, Collections
for overdue khata, Expiry clearance, and the pack playbooks.
"""

import json
from datetime import timedelta
from statistics import median
from typing import Any

from arth.agents.runtime import Done, Fail, Next, Playbook, Run, Runtime, Wait
from arth.agents.tables import briefs
from arth.ai.guards import injection
from arth.ai.perception import extract_order
from arth.core.clock import iso_utc, parse_iso
from arth.core.ids import new_id
from arth.domains.commerce_tables import appointments, daily_closes, price_history, purchase_orders, suppliers
from arth.domains.ledger_projection import account_view, statement
from arth.domains.ledger_tables import credit_accounts
from arth.domains.patron_identity import has_consent
from arth.domains.stock import expiry_view, stock_view
from arth.domains.summaries import item_name, patron_name
from arth.domains.tables import items
from arth.governance.repository import Repository
from arth.intel.analytics import daily_sales, khata_aging, purchase_cycles, today
from arth.intel.insight import next_best_actions
from arth.sim.tables import messages_in

IST = timedelta(hours=5, minutes=30)


async def read(rt: Runtime, run: Run, fn: Any, *args: Any) -> Any:
    async with rt.db.read() as conn:
        return await fn(Repository(conn, run.merchant_id), *args)


# ---- Night Shift (Hisaab) -------------------------------------------------------------------------------
async def night_scan(rt: Runtime, run: Run) -> Next:
    await rt.command(run, "alerts.scan", {}, "alerts")
    day = rt.clock.now_ist().date().isoformat()
    closed = await read(rt, run, lambda repo: repo.select(daily_closes, daily_closes.c.date == day))
    if not closed:
        await rt.command(run, "treasury.daily_close", {"date": day}, "close")
    return Next("brief")


async def night_brief(rt: Runtime, run: Run) -> Next:
    """PUL-1: tomorrow morning's brief: yesterday vs typical, dues, orders, at most one suggestion."""
    clock = rt.clock
    now = today(clock)
    week = await read(rt, run, daily_sales, now - timedelta(days=28), now)
    typical_rows = [r["sales_paise"] for r in week[:-1] if r["date"][:10] and r["sales_paise"]]
    typical = sum(typical_rows) // len(typical_rows) if typical_rows else 0
    aging = await read(rt, run, khata_aging, clock)
    actions = await read(rt, run, next_best_actions, clock, set())
    content = {
        "date": now.isoformat(),
        "sales_paise": week[-1]["sales_paise"],
        "typical_paise": typical,
        "khata_due_paise": sum(r["amount_paise"] for r in aging),
        "suggestion": actions["proactive"][0] if actions["proactive"] else None,
    }
    async with rt.db.write() as conn:
        repo = Repository(conn, run.merchant_id)
        if not await repo.select(briefs, briefs.c.date == now.isoformat()):
            await repo.insert(
                briefs,
                {
                    "id": new_id("brief"),
                    "date": now.isoformat(),
                    "content": json.dumps(content),
                    "created_at": iso_utc(clock.now()),
                },
            )
    run.context["brief"] = content
    return Next("spawn")


async def night_spawn(rt: Runtime, run: Run) -> Next:
    clock = rt.clock
    stock = (await read(rt, run, stock_view, clock))["items"]
    for row in stock:
        if row["status"] in {"low", "out"}:
            await rt.start(run.merchant_id, "reorder", row["item_id"])
    for account in await read(rt, run, lambda repo: repo.select(credit_accounts)):
        if await read(rt, run, collections_due, account, clock):
            await rt.start(run.merchant_id, "collections", account["id"])
    for batch in (await read(rt, run, expiry_view, clock, 30))["batches"]:
        if batch["qty_milli"] > 0 and not batch["recalled"]:
            await rt.start(run.merchant_id, "expiry_clearance", batch["batch_id"])
    pack = await rt.shop_pack(run.merchant_id)
    tomorrow = (clock.now_ist() + timedelta(days=1)).date().isoformat()
    if pack == "salon":
        await rt.start(run.merchant_id, "appointment_reminders", tomorrow)
    if pack == "pharmacy":
        await rt.start(run.merchant_id, "refill_run", tomorrow)
    return Next("memory")


async def night_memory(rt: Runtime, run: Run) -> Done:
    """Memory derivations: strong purchase cycles become facts with their evidence (trusted: derived)."""
    for cycle in (await read(rt, run, purchase_cycles, rt.clock))[:5]:
        await rt.command(
            run,
            "memory.propose",
            {
                "subject": cycle["patron_id"],
                "predicate": "cycle.days",
                "value": f"{cycle['item_id']}:{cycle['cycle_days']}",
                "evidence": [cycle["next_due"]],
            },
            f"mem-{cycle['patron_id']}-{cycle['item_id']}",
        )
    return Done({"brief": run.context.get("brief", {}).get("date")})


# ---- Reorder + Delivery Check + Claims (Kharid / Procurement) -----------------------------------------
async def reorder_start(rt: Runtime, run: Run) -> Next | Done:
    item_id = run.subject
    history = await read(rt, run, lambda repo: repo.select(price_history, price_history.c.item_id == item_id))
    options = await read(rt, run, lambda repo: repo.select(suppliers))
    if not options:
        await rt.work(run, "reorder_no_supplier", "work.reorder_no_supplier", {"item_id": item_id})
        return Done({"reason": "no_supplier"})
    best = min(history, key=lambda r: r["unit_price_paise"]) if history else None
    supplier = best["supplier_id"] if best else options[0]["id"]
    item = (await read(rt, run, lambda repo: repo.select(items, items.c.id == item_id)))[0]
    price = best["unit_price_paise"] if best else item["cost_paise"]
    po = await rt.command(
        run,
        "supply.draft_po",
        {
            "supplier_id": supplier,
            "lines": [{"item_id": item_id, "qty_milli": 50_000, "unit_price_paise": price}],
        },
        "draft",
    )
    run.context.update(po_id=po["data"]["po_id"], supplier_id=supplier)
    return Next("place")


async def reorder_place(rt: Runtime, run: Run) -> Wait:
    gate = await rt.command(
        run, "supply.place_po", {"po_id": run.context["po_id"]}, "place"
    )  # R3: owner decides
    run.context["gate"] = gate.get("gate_id")
    return Wait(
        "po.changed",
        {"po_id": run.context["po_id"], "status": "sent"},
        "await_variance",
        until_minutes=24 * 60,
        timeout_next="expired",
    )


async def reorder_await_variance(rt: Runtime, run: Run) -> Wait:
    # Delivery Check: after receipt and the supplier bill, a 3-way-match variance wakes the claim step.
    return Wait(
        "po.variance_found",
        {"po_id": run.context["po_id"]},
        "claim",
        until_minutes=7 * 24 * 60,
        timeout_next="closed",
    )


async def reorder_claim(rt: Runtime, run: Run) -> Done:
    claim = run.context.get("event", {}).get("claim_id")
    if claim:
        await rt.command(
            run, "supply.send_claim", {"claim_id": claim}, "claim"
        )  # R3 with the variance in scope
    return Done({"po_id": run.context["po_id"], "claim_id": claim})


async def reorder_expired(rt: Runtime, run: Run) -> Done:
    await rt.work(run, "reorder_waiting", "work.reorder_waiting", {"po_id": run.context["po_id"]})
    return Done({"po_id": run.context["po_id"], "status": "owner_did_not_answer"})


async def reorder_closed(rt: Runtime, run: Run) -> Done:
    return Done({"po_id": run.context["po_id"], "variance": False})


# ---- Collections (Khata) --------------------------------------------------------------------------------
async def collections_due(repo: Repository, account: dict[str, Any], clock: Any) -> bool:
    """E7.2 trigger: the oldest unpaid entry is older than max(the patron's pay cycle x 1.5, 7 days), the
    patron consented to reminders and nothing on the account is disputed. Others get no run at all."""
    view = await account_view(repo, account["id"], clock)
    if view["balance_paise"] <= 0 or any(e["status"] == "disputed" for e in view["entries"]):
        return False
    if not await has_consent(repo, account["patron_id"], "reminders"):
        return False
    unpaid = [e for e in view["entries"] if e["amount_paise"] > e["allocated_paise"]]
    if not unpaid:
        return False
    paid_on = sorted({parse_iso(p["occurred_at"]).date() for p in view["payments"]})
    gaps = [(b - a).days for a, b in zip(paid_on, paid_on[1:], strict=False)]
    threshold = max(7, int(median(gaps) * 1.5) if gaps else 0)
    oldest = min(parse_iso(e["occurred_at"]) for e in unpaid)
    return (clock.now() - oldest).days >= threshold


async def collect_start(rt: Runtime, run: Run) -> Next | Done | Wait:
    account = (
        await read(rt, run, lambda repo: repo.select(credit_accounts, credit_accounts.c.id == run.subject))
    )[0]
    balance = (await read(rt, run, statement, run.subject, rt.clock))["balance_paise"]
    if balance <= 0:
        return Done({"balance_paise": 0})
    if not await rt.lock(run, account["patron_id"]):
        return Wait(
            "credit.changed",
            {"account_id": run.subject},
            "start",
            until_minutes=24 * 60,
            timeout_next="start",
        )  # deferred: another playbook is talking to this customer
    run.context["patron_id"] = account["patron_id"]
    return Next("remind")


async def collect_remind(rt: Runtime, run: Run) -> Wait:
    attempt = run.context.get("attempt", 0) + 1
    run.context["attempt"] = attempt
    gate = await rt.command(
        run,
        "ledger.send_reminder",
        {"account_id": run.subject, "template_key": "reminder.gentle"},
        f"remind-{attempt}",
    )
    run.context["gate"] = gate.get("gate_id")
    return Wait(
        "credit.changed",
        {"account_id": run.subject},
        "check",
        until_minutes=3 * 24 * 60,
        timeout_next="check",
    )


async def collect_check(rt: Runtime, run: Run) -> Next | Done | Wait:
    balance = (await read(rt, run, statement, run.subject, rt.clock))["balance_paise"]
    if balance <= 0:
        await rt.unlock(run, run.context["patron_id"])
        return Done({"collected": True})
    view = await read(rt, run, account_view, run.subject, rt.clock)
    promised = [p for p in view["promises"] if p["status"] == "active"]
    if promised:  # a promise sleeps until its date, then re-checks (WFL-9, E7.2)
        return Wait(
            "credit.changed",
            {"account_id": run.subject},
            "check",
            until_minutes=7 * 24 * 60,
            timeout_next="check",
        )
    if run.context["attempt"] >= 3:
        await rt.unlock(run, run.context["patron_id"])
        await rt.work(
            run,
            "collection_stuck",
            "work.collection_stuck",
            {"account_id": run.subject, "balance_paise": balance},
        )
        return Done({"collected": False})
    return Next("remind")


# ---- Concierge (Bikri) -------------------------------------------------------------------------------------
async def concierge_start(rt: Runtime, run: Run) -> Next | Done | Wait:
    message = (await read(rt, run, lambda repo: repo.select(messages_in, messages_in.c.id == run.subject)))[0]
    run.context["thread"] = message["thread_ref"]
    if injection(message["text"]):  # untrusted text can only create drafts; this one creates nothing
        await rt.work(run, "message_flagged", "work.message_flagged", {"message_id": run.subject})
        return Done({"flagged": True})
    if message["supplier_id"]:
        await rt.work(run, "supplier_message", "work.supplier_message", {"message_id": run.subject})
        return Done({"supplier": True})
    lowered = message["text"].lower()
    if any(w in lowered for w in ("baaki", "kitna dena", "balance", "hisaab", "kitna udhaar")):
        return Next("balance")
    if any(w in lowered for w in ("dawai", "medicine", "bukhar", "dose")):
        await rt.command(
            run,
            "messages.reply",
            {"message_id": run.subject, "template": "reply.ask_pharmacist", "params": {}},
            "medical",
        )
        return Done({"scope": "medical"})
    order = await read(rt, run, extract_order, None, message["text"])
    if not order["lines"]:
        await rt.work(run, "message_unclear", "work.message_unclear", {"message_id": run.subject})
        return Done({"unclear": True})
    payload: dict[str, Any] = {"channel": "whatsapp", "message_ref": run.subject, "lines": order["lines"]}
    if message["patron_id"]:
        payload["patron_id"] = message["patron_id"]
    created = await rt.command(run, "orders.create_draft", payload, "draft")
    run.context["order_id"] = created["data"]["order_id"]
    await rt.command(
        run,
        "messages.reply",
        {
            "message_id": run.subject,
            "template": "reply.order_received",
            "params": {"order_id": run.context["order_id"]},
        },
        "ack",
    )
    if any(line["item_id"] is None for line in order["lines"]):
        await rt.work(
            run, "order_check", "work.order_check", {"order_id": run.context["order_id"]}, urgency=2
        )
        return Done({"order_id": run.context["order_id"], "needs_check": True})
    await rt.command(run, "orders.place", {"order_id": run.context["order_id"]}, "place")
    await rt.command(
        run, "orders.accept", {"order_id": run.context["order_id"]}, "accept"
    )  # R3 gate for the owner
    return Wait(
        "order.changed",
        {"order_id": run.context["order_id"], "status": "accepted"},
        "accepted",
        until_minutes=12 * 60,
        timeout_next="unanswered",
    )


async def concierge_balance(rt: Runtime, run: Run) -> Done:
    """CHT-5: a customer may ask only about their own balance; others' data is never revealed."""
    message = (await read(rt, run, lambda repo: repo.select(messages_in, messages_in.c.id == run.subject)))[0]
    if not message["patron_id"]:
        await rt.command(
            run,
            "messages.reply",
            {"message_id": run.subject, "template": "reply.identify_first", "params": {}},
            "balance",
        )
        return Done({"revealed": False})
    accounts = await read(
        rt,
        run,
        lambda repo: repo.select(credit_accounts, credit_accounts.c.patron_id == message["patron_id"]),
    )
    balance = (
        (await read(rt, run, statement, accounts[0]["id"], rt.clock))["balance_paise"] if accounts else 0
    )
    await rt.command(
        run,
        "messages.reply",
        {"message_id": run.subject, "template": "reply.own_balance", "params": {"balance_paise": balance}},
        "balance",
    )
    return Done({"revealed": True, "balance_paise": balance})


async def concierge_accepted(rt: Runtime, run: Run) -> Done:
    return Done({"order_id": run.context["order_id"], "accepted": True})


async def concierge_unanswered(rt: Runtime, run: Run) -> Done:
    await rt.work(
        run, "order_waiting", "work.order_waiting", {"order_id": run.context["order_id"]}, urgency=2
    )
    return Done({"order_id": run.context["order_id"], "accepted": False})


# ---- Feedback recovery, expiry clearance, analyst -------------------------------------------------------
async def feedback_start(rt: Runtime, run: Run) -> Done:
    await rt.work(
        run,
        "feedback_recovery",
        "work.feedback_recovery",
        {"rating_id": run.subject, "draft_key": "recovery.apology_and_fix"},
        urgency=3,
    )
    return Done({"work": True})


async def expiry_start(rt: Runtime, run: Run) -> Done:
    """EXP-4: clearance stays above cost; restricted items get return-to-distributor instead of a discount."""
    from arth.domains.stock_tables import batches

    batch = (await read(rt, run, lambda repo: repo.select(batches, batches.c.id == run.subject)))[0]
    item = (await read(rt, run, lambda repo: repo.select(items, items.c.id == batch["item_id"])))[0]
    details = json.loads(item["details"])
    if details.get("rx_required"):
        await rt.work(run, "return_to_distributor", "work.return_to_distributor", {"batch_id": batch["id"]})
        return Done({"action": "return"})
    room = item["price_paise"] - batch["cost_paise"]
    if room <= 0:
        await rt.work(run, "return_to_distributor", "work.return_to_distributor", {"batch_id": batch["id"]})
        return Done({"action": "return"})
    await rt.work(
        run,
        "clearance",
        "work.clearance",
        {
            "batch_id": batch["id"],
            "item_id": item["id"],
            "name": await read(rt, run, item_name, item["id"]),
            "max_discount_paise": room // 2,
        },
    )
    return Done({"action": "clearance", "max_discount_paise": room // 2})


async def analyst_start(rt: Runtime, run: Run) -> Done:
    week = await read(rt, run, daily_sales, today(rt.clock) - timedelta(days=6), today(rt.clock))
    await rt.work(
        run,
        "weekly_review",
        "work.weekly_review",
        {"sales_paise": sum(r["sales_paise"] for r in week), "bills": sum(r["bills"] for r in week)},
        0,
    )
    return Done({})


# ---- Pack playbooks (T5.12) ------------------------------------------------------------------------------
async def appointment_reminders(rt: Runtime, run: Run) -> Done:
    """SAL-2: utility reminders for tomorrow's appointments, only with reminder consent."""
    sent = 0
    for row in await read(rt, run, lambda repo: repo.select(appointments, appointments.c.status == "booked")):
        if row["patron_id"] and row["start_at"] and (row["start_at"][:10] == run.subject):
            if await read(rt, run, has_consent, row["patron_id"], "reminders"):
                await rt.work(
                    run, "reminder_sent", "work.appointment_reminder", {"appointment_id": row["id"]}, 0
                )
                sent += 1
    return Done({"sent": sent})


async def refill_run(rt: Runtime, run: Run) -> Done:
    """PHAR-3: refill nudges from purchase cycles, under reminder consent only, never as marketing."""
    due = []
    for cycle in await read(rt, run, purchase_cycles, rt.clock):
        if cycle["next_due"] <= run.subject and await read(
            rt, run, has_consent, cycle["patron_id"], "reminders"
        ):
            due.append(
                {
                    "patron_id": cycle["patron_id"],
                    "item_id": cycle["item_id"],
                    "name": await read(rt, run, patron_name, cycle["patron_id"]),
                }
            )
    if due:
        await rt.work(run, "refills_due", "work.refills_due", {"count": len(due)}, 1)
    return Done({"due": len(due)})


async def batch_recall(rt: Runtime, run: Run) -> Done:
    """EXP-5: list every buyer of a recalled batch; notify only those with consent."""
    from arth.domains.stock_tables import stock_moves

    buyers = sorted(
        {
            m["buyer_id"]
            for m in await read(
                rt, run, lambda repo: repo.select(stock_moves, stock_moves.c.batch_id == run.subject)
            )
            if m["buyer_id"]
        }
    )
    consenting = [b for b in buyers if await read(rt, run, has_consent, b, "receipts")]
    await rt.work(
        run,
        "recall",
        "work.batch_recall",
        {"batch_id": run.subject, "buyers": len(buyers), "notifiable": len(consenting)},
        3,
    )
    return Done({"buyers": buyers, "notified": consenting})


PLAYBOOKS = [
    Playbook(
        "night_shift",
        "night_shift",
        {"start": night_scan, "brief": night_brief, "spawn": night_spawn, "memory": night_memory},
    ),
    Playbook(
        "reorder",
        "procurement",
        {
            "start": reorder_start,
            "place": reorder_place,
            "await_variance": reorder_await_variance,
            "claim": reorder_claim,
            "expired": reorder_expired,
            "closed": reorder_closed,
        },
    ),
    Playbook(
        "collections",
        "collections",
        {"start": collect_start, "remind": collect_remind, "check": collect_check},
    ),
    Playbook(
        "concierge",
        "concierge",
        {
            "start": concierge_start,
            "balance": concierge_balance,
            "accepted": concierge_accepted,
            "unanswered": concierge_unanswered,
        },
    ),
    Playbook("feedback_recovery", "strategist", {"start": feedback_start}),
    Playbook("expiry_clearance", "curator", {"start": expiry_start}),
    Playbook("analyst_weekly", "analyst", {"start": analyst_start}),
    Playbook("appointment_reminders", "concierge", {"start": appointment_reminders}),
    Playbook("refill_run", "curator", {"start": refill_run}),
    Playbook("batch_recall", "curator", {"start": batch_recall}),
]
TRIGGERS = {
    "message.in": "concierge",
    "feedback.recorded": "feedback_recovery",
    "batch.recalled": "batch_recall",
}


def install(runtime: Runtime, dispatcher: Any) -> None:
    for playbook in PLAYBOOKS:
        runtime.register(playbook)

    async def trigger(repo: Repository, event: dict[str, Any]) -> None:
        name = TRIGGERS.get(event["type"])
        if not name:
            return
        payload = event["payload"]
        if name == "feedback_recovery" and not payload.get("low"):
            return
        subject = payload.get("message_id") or payload.get("rating_id") or payload.get("batch_id")
        if subject:
            await runtime.start_in(repo, name, subject)

    if dispatcher is not None:
        dispatcher.on("playbooks.triggers", trigger)


async def open_purchase_orders(repo: Repository) -> list[dict[str, Any]]:
    return await repo.select(purchase_orders, purchase_orders.c.status.in_(["sent", "confirmed"]))


__all__ = ["install", "PLAYBOOKS", "Fail", "open_purchase_orders", "patron_name"]
