"""T1.13 Treasury: TRS-1…5, PEX-1…3, PEX-5, STF-3, CTR-6."""

import pytest
from l1d_helpers import approve, new_bill, patron_account, receive, run, shop, staff, system, view

from arth.domains.patron_identity import identity_value
from arth.governance.commands import CommandError
from arth.governance.policy import Session


async def rails(s, status, utr, amount, **extra):
    payload = {
        "status": status,
        "utr": utr,
        "amount_paise": amount,
        "mode": extra.pop("mode", "upi_qr"),
        **extra,
    }
    return (
        await run(s, "treasury.rails_event", payload, actor=system(s), private={"payment_verified": True})
    )["data"]


async def bill_with_upi(s, qty=2000):
    bill = await new_bill(s, [{"item_id": s.items["PARLE"], "qty_milli": qty, "added_via": "scan"}])
    intent = (await run(s, "counter.request_upi", {"bill_id": bill}))["data"]
    return bill, intent


async def test_rails_events_require_verified_system_actor(db):
    s = await shop(db)
    payload = {"status": "success", "utr": "430100000001", "amount_paise": 100, "mode": "upi_static"}
    with pytest.raises(CommandError, match="treasury.verified_callback_required"):
        await run(s, "treasury.rails_event", payload)
    with pytest.raises(CommandError, match="treasury.verified_callback_required"):
        await run(s, "treasury.rails_event", payload, actor=system(s))


async def test_dynamic_qr_pending_then_success_closes_bill(db):
    from arth.domains.counter import bill_state

    s = await shop(db)
    bill, intent = await bill_with_upi(s)
    pending = await rails(s, "pending", "430100000002", intent["amount_paise"], order_ref=intent["order_ref"])
    assert pending["status"] == "pending"
    state = await view(s, bill_state, bill)
    assert state["status"] == "open" and state["upi"]["status"] == "pending"
    done = await rails(s, "success", "430100000002", intent["amount_paise"], order_ref=intent["order_ref"])
    assert done["bill"]["status"] == "closed"
    state = await view(s, bill_state, bill)
    assert state["status"] == "closed" and state["upi"]["status"] == "paid"
    assert state["payments"] == [
        {"mode": "upi", "amount_paise": 2000, "change_paise": None, "ref_id": done["payment_id"]}
    ]
    replay = await rails(s, "success", "430100000002", intent["amount_paise"], order_ref=intent["order_ref"])
    assert replay["replay"] is True


async def test_pending_then_failure_offers_alternatives_and_cash_still_works(db):
    from arth.domains.commerce_tables import payment_exceptions
    from arth.governance.repository import Repository

    s = await shop(db)
    bill, intent = await bill_with_upi(s)
    await rails(s, "pending", "430100000003", 2000, order_ref=intent["order_ref"])
    failed = await rails(s, "failed", "430100000003", 2000, order_ref=intent["order_ref"])
    assert failed["alternatives"] == ["cash", "khata", "regenerate"]
    async with db.read() as conn:
        rows = await Repository(conn, s.mid).select(payment_exceptions)
    assert sorted((r["kind"], r["status"]) for r in rows) == [("failed", "open"), ("pending", "resolved")]
    closed = await run(
        s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 2000}]}
    )
    assert closed["data"]["status"] == "closed"


async def test_planted_duplicate_is_flagged_with_r4_refund_suggestion(db):
    from arth.domains.commerce_tables import payment_exceptions
    from arth.governance.repository import Repository

    s = await shop(db)
    bill, intent = await bill_with_upi(s)
    payer = identity_value(s.mid, "vpa", "sharma@paytm")[1]
    await rails(s, "success", "430100000004", 2000, order_ref=intent["order_ref"], payer_ref=payer)
    dup = await rails(s, "success", "430100000005", 2000, mode="upi_static", payer_ref=payer)
    assert dup["duplicate_of_bill"] == bill
    async with db.read() as conn:
        rows = await Repository(conn, s.mid).select(
            payment_exceptions, payment_exceptions.c.kind == "duplicate"
        )
    assert len(rows) == 1 and '"tier": "R4"' in rows[0]["detail"]
    with pytest.raises(CommandError, match="policy.console_required"):
        await run(
            s,
            "treasury.refund",
            {"payment_id": dup["payment_id"], "amount_paise": 2000, "reason_key": "refund.duplicate"},
        )
    console = Session(s.mid, s.owner.actor_id, "owner", channel="console", step_up=True)
    refund = await run(
        s,
        "treasury.refund",
        {"payment_id": dup["payment_id"], "amount_paise": 2000, "reason_key": "refund.duplicate"},
        actor=console,
    )
    assert refund["data"]["amount_paise"] == 2000
    async with db.read() as conn:
        rows = await Repository(conn, s.mid).select(
            payment_exceptions, payment_exceptions.c.kind == "duplicate"
        )
    assert rows[0]["status"] == "resolved"
    with pytest.raises(CommandError, match="treasury.refund_exceeds_payment"):
        await run(
            s,
            "treasury.refund",
            {"payment_id": dup["payment_id"], "amount_paise": 1, "reason_key": "refund.duplicate"},
            actor=console,
        )


async def test_unmatched_queue_ranks_bills_and_hints_khata_repayment(db):
    from arth.domains.treasury import unmatched

    s = await shop(db)
    patron, account = await patron_account(s, "Sharma ji", vpa="sharma@paytm")
    payer = identity_value(s.mid, "vpa", "sharma@paytm")[1]
    gate = await run(
        s,
        "ledger.add_entry",
        {
            "account_id": account,
            "amount_paise": 5000,
            "source": "voice",
            "lines": [{"item_id": s.items["PARLE"], "qty_milli": 5000, "unit_price_paise": 1000}],
        },
    )
    await approve(s, gate)
    near = await new_bill(s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])  # 2700
    far = await new_bill(s, [{"item_id": s.items["PARLE"], "qty_milli": 9000, "added_via": "tap"}])  # 9000
    paid = await rails(s, "success", "430100000006", 2700, mode="upi_static", payer_ref=payer)
    queue = await view(s, unmatched, s.bus.clock)
    assert [q["payment_id"] for q in queue] == [paid["payment_id"]]
    assert [x["bill_id"] for x in queue[0]["suggestions"]][:2] == [near, far]
    assert queue[0]["khata_patron_id"] == patron
    gate = await run(s, "treasury.match_khata", {"payment_id": paid["payment_id"], "account_id": account})
    allocated = await approve(s, gate)
    assert allocated["data"]["balance_paise"] == 2300
    assert await view(s, unmatched, s.bus.clock) == []
    with pytest.raises(CommandError, match="treasury.payment_not_matchable"):
        await run(s, "treasury.match_bill", {"payment_id": paid["payment_id"], "bill_id": near})


async def test_match_bill_closes_it(db):
    from arth.domains.counter import bill_state

    s = await shop(db)
    bill = await new_bill(s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])
    paid = await rails(s, "success", "430100000007", 2700, mode="upi_static")
    await run(s, "treasury.match_bill", {"payment_id": paid["payment_id"], "bill_id": bill})
    assert (await view(s, bill_state, bill))["status"] == "closed"


async def test_settlement_explainer_equals_record_to_the_paisa_and_flags_mismatch(db):
    from arth.domains.treasury import settlement_rows

    s = await shop(db)
    await rails(s, "success", "430100000008", 100000, mode="upi_static")
    good = {
        "external_ref": "stl-1",
        "date": "2026-10-29",
        "gross_paise": 100000,
        "net_paise": 98700,
        "lines": [{"kind": "fee", "amount_paise": 300}, {"kind": "edi", "amount_paise": 1000}],
        "utrs": ["430100000008"],
    }
    assert (
        await run(s, "treasury.record_settlement", good, actor=system(s), private={"payment_verified": True})
    )["data"]["matches"] is True
    bad = {**good, "external_ref": "stl-2", "net_paise": 98000}
    assert (
        await run(s, "treasury.record_settlement", bad, actor=system(s), private={"payment_verified": True})
    )["data"]["matches"] is False
    rows = await view(s, settlement_rows)
    assert rows[0]["deductions"] == [
        {"kind": "fee", "amount_paise": 300},
        {"kind": "edi", "amount_paise": 1000},
    ]
    assert [r["explained"] for r in rows] == [True, False]


async def test_expense_is_r2_and_shift_variance_attributed_to_staff(db):
    s = await shop(db)
    cashier = await staff(s, "cashier", "shift")
    with pytest.raises(CommandError, match="policy.role"):
        await run(
            s,
            "treasury.expense",
            {"category": "transport", "amount_paise": 500, "paid_from": "cash"},
            actor=cashier,
        )
    shift = (await run(s, "shift.open", {"float_paise": 100000}, actor=cashier))["data"]["shift_id"]
    await receive(s, "SALT", 5000)
    bill = await new_bill(
        s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}], actor=cashier
    )
    await run(
        s,
        "counter.checkout",
        {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 2700, "tendered_paise": 5000}]},
        actor=cashier,
    )
    closed = await run(s, "shift.close", {"shift_id": shift, "counted_paise": 102000}, actor=cashier)
    assert closed["data"]["expected_paise"] == 102700
    assert closed["data"]["variance_paise"] == -700
    gate = await run(
        s, "treasury.expense", {"category": "transport", "amount_paise": 15000, "paid_from": "cash"}
    )
    assert (await approve(s, gate))["data"]["readback_key"] == "treasury.expense_readback"


async def test_daily_close_summary_is_discreet_and_once_per_day(db):
    s = await shop(db)
    bill = await new_bill(s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])
    await run(s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "card", "amount_paise": 2700}]})
    day = s.bus.clock.now_ist().date().isoformat()
    result = await run(s, "treasury.daily_close", {"date": day})
    assert result["data"]["summary"]["by_mode"] == {"card": 2700}
    assert result["data"]["sensitivity"] == "discreet"
    with pytest.raises(CommandError, match="treasury.day_closed"):
        await run(s, "treasury.daily_close", {"date": day})
