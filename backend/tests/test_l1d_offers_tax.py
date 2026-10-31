"""T1.18 Offers (OFR-1…11, PHAR-4) and T1.19 Tax/Books (TAX-1…3, BKS-1)."""

import asyncio
from datetime import timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from l1d_helpers import approve, new_bill, receive, release, run, shop, system, view

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.domains.patron_identity import identity_value
from arth.governance.commands import CommandError
from arth.governance.policy import Session

UTR = iter(range(430200000000, 430299999999))


def payer(s, name):
    return identity_value(s.mid, "vpa", name + "@upi")[1]


async def pay(s, ref, amount, **extra):
    payload = {
        "status": "success",
        "utr": str(next(UTR)),
        "amount_paise": amount,
        "mode": "upi_static",
        "payer_ref": ref,
        **extra,
    }
    return (
        await run(s, "treasury.rails_event", payload, actor=system(s), private={"payment_verified": True})
    )["data"]


async def program(s, kind, rules, *, budget=100000, holdout=2000, **extra):
    now = s.bus.clock.now()
    terms = {
        "amount_paise": rules["reward_paise"],
        "min_spend_paise": rules.get("min_spend_paise", 0),
        "expiry_days": rules.get("validity_days", 0),
    }
    payload = {
        "type": kind,
        "rules": rules,
        "terms": terms,
        "budget_paise": budget,
        "funding": "merchant",
        "holdout_bp": holdout,
        "valid_from": iso_utc(now - timedelta(days=1)),
        "valid_until": iso_utc(now + timedelta(days=30)),
        **extra,
    }
    gate = await run(s, "offers.create_program", payload)
    assert gate["tier"] == "R3" and gate["scope"]["payload"]["budget_paise"] == budget
    await approve(s, gate)
    await release(s)
    from arth.domains.commerce_tables import offer_programs
    from arth.governance.repository import Repository

    async with s.bus.db.read() as conn:
        rows = await Repository(conn, s.mid).select(offer_programs)
    return max(rows, key=lambda r: r["created_at"])["id"]


async def treated_payer(s, program_id, prefix="cust"):
    """A payer that the deterministic holdout assigns to the treated arm."""
    import hashlib

    for i in range(100):
        ref = payer(s, f"{prefix}{i}")
        if int(hashlib.sha256((program_id + "|" + ref).encode()).hexdigest()[:8], 16) % 10000 >= 2000:
            return ref
    raise AssertionError


def holdout_payer(s, program_id):
    import hashlib

    for i in range(200):
        ref = payer(s, f"hold{i}")
        if int(hashlib.sha256((program_id + "|" + ref).encode()).hexdigest()[:8], 16) % 10000 < 2000:
            return ref
    raise AssertionError


async def liability(s, program_id=None):
    from arth.domains.offers import liability as compute

    return await view(s, compute, program_id)


async def test_program_creation_validates_terms_holdout_and_margin(db):
    s = await shop(db)
    now = s.bus.clock.now()
    base = {
        "type": "instant_cashback",
        "rules": {"reward_paise": 2000, "min_spend_paise": 100000},
        "terms": {"amount_paise": 2000, "min_spend_paise": 100000, "expiry_days": 0},
        "budget_paise": 50000,
        "funding": "merchant",
        "holdout_bp": 2000,
        "valid_from": iso_utc(now),
        "valid_until": iso_utc(now + timedelta(days=7)),
    }
    with pytest.raises(CommandError, match="offers.terms_mismatch"):
        await run(s, "offers.create_program", {**base, "terms": {**base["terms"], "amount_paise": 2500}})
    with pytest.raises(CommandError, match="offers.holdout_required"):
        await run(s, "offers.create_program", {**base, "holdout_bp": 500})
    coupon = {
        **base,
        "type": "item_coupon",
        "rules": {"reward_paise": 900, "min_spend_paise": 0, "validity_days": 7, "item_id": s.items["SALT"]},
        "terms": {"amount_paise": 900, "min_spend_paise": 0, "expiry_days": 7},
    }
    with pytest.raises(CommandError, match="policy.margin_floor"):  # (2700 − 2000 − 900)/2700 < 15%
        await run(s, "offers.create_program", coupon)
    p = await shop(db, "pharmacy")
    rx = {
        **coupon,
        "rules": {**coupon["rules"], "item_id": p.items["AMOX"], "reward_paise": 100},
        "terms": {**coupon["terms"], "amount_paise": 100},
    }
    with pytest.raises(CommandError, match="policy.pack"):  # PHAR-4
        await run(p, "offers.create_program", rx)


async def test_next_transaction_cashback_paid_once_on_qualifying_payment(db):
    from arth.domains.commerce_tables import offer_events
    from arth.governance.repository import Repository

    s = await shop(db)
    pid = await program(
        s, "next_txn_cashback", {"reward_paise": 2500, "min_spend_paise": 50000, "validity_days": 14}
    )
    ref = await treated_payer(s, pid)
    first = await pay(s, ref, 60000)
    assert [o["kind"] for o in first["offers"]] == ["cashback_promise"]
    small = await pay(s, ref, 10000)
    assert small["offers"] == []  # below min spend: not paid
    s.bus.clock.set(s.bus.clock.now() + timedelta(days=1))
    second = await pay(s, ref, 55000)
    assert [o["kind"] for o in second["offers"]] == ["cashback_paid"]
    third = await pay(s, ref, 55000)
    assert all(o["kind"] != "cashback_paid" for o in third["offers"])
    async with db.read() as conn:
        paid = await Repository(conn, s.mid).select(offer_events, offer_events.c.kind == "redeemed")
    assert len(paid) == 1
    assert (await liability(s, pid))["redeemed_paise"] == 2500


async def test_abuse_owner_staff_payer_excluded(db):
    s = await shop(db)
    pid = await program(s, "instant_cashback", {"reward_paise": 2000, "min_spend_paise": 100000})
    owner_vpa = await treated_payer(s, pid, "owner")
    await run(s, "offers.exclude_payers", {"payer_refs": [owner_vpa]})
    assert (await pay(s, owner_vpa, 150000))["offers"] == []


async def test_abuse_one_welcome_coupon_per_payer_ever(db):
    s = await shop(db)
    pid = await program(
        s, "first_time_coupon", {"reward_paise": 2000, "min_spend_paise": 20000, "validity_days": 14}
    )
    ref = await treated_payer(s, pid)
    first = await pay(s, ref, 5000)
    assert [o["kind"] for o in first["offers"]] == ["coupon"] and first["offers"][0]["code"]
    s.bus.clock.set(s.bus.clock.now() + timedelta(days=2))
    assert (await pay(s, ref, 5000))["offers"] == []


async def test_abuse_split_payments_inside_window_are_combined(db):
    s = await shop(db)
    pid = await program(
        s, "instant_cashback", {"reward_paise": 2000, "min_spend_paise": 100000, "combine_minutes": 10}
    )
    ref = await treated_payer(s, pid)
    assert (await pay(s, ref, 60000))["offers"] == []
    second = await pay(s, ref, 60000)  # combined 1,200 ≥ 1,000 → one reward
    assert [o["kind"] for o in second["offers"]] == ["instant_cashback"]
    assert (await pay(s, ref, 100000))["offers"] == []  # never a second reward in the same window


async def test_abuse_velocity_limit_one_per_program_per_day(db):
    s = await shop(db)
    pid = await program(
        s, "instant_cashback", {"reward_paise": 1000, "min_spend_paise": 10000, "combine_minutes": 1}
    )
    ref = await treated_payer(s, pid)
    assert len((await pay(s, ref, 20000))["offers"]) == 1
    s.bus.clock.set(s.bus.clock.now() + timedelta(minutes=5))
    assert (await pay(s, ref, 20000))["offers"] == []


async def test_abuse_refund_claws_back_reward(db):
    s = await shop(db)
    pid = await program(
        s, "next_txn_cashback", {"reward_paise": 2500, "min_spend_paise": 50000, "validity_days": 14}
    )
    ref = await treated_payer(s, pid)
    paid = await pay(s, ref, 60000)
    console = Session(s.mid, s.owner.actor_id, "owner", channel="console", step_up=True)
    refund = await run(
        s,
        "treasury.refund",
        {"payment_id": paid["payment_id"], "amount_paise": 60000, "reason_key": "refund.customer"},
        actor=console,
    )
    assert refund["data"]["clawed_back"] == [paid["offers"][0]["issuance_id"]]
    owed = await liability(s, pid)
    assert owed["outstanding_paise"] == 0 and owed["issued_paise"] == 2500 and owed["expired_paise"] == 2500


async def test_abuse_holdout_and_regulars_never_rewarded(db):
    s = await shop(db)
    pid = await program(
        s, "instant_cashback", {"reward_paise": 1000, "min_spend_paise": 10000, "combine_minutes": 1}
    )
    assert (await pay(s, holdout_payer(s, pid), 50000))["offers"] == []
    regular = await treated_payer(s, pid, "regular")
    other = await program(
        s, "instant_cashback", {"reward_paise": 1000, "min_spend_paise": 10000, "combine_minutes": 1}
    )
    for _ in range(4):
        s.bus.clock.set(s.bus.clock.now() + timedelta(days=1))
        await pay(s, regular, 5000)
    s.bus.clock.set(s.bus.clock.now() + timedelta(days=1))
    result = await pay(s, regular, 50000)
    assert [o for o in result["offers"] if o["kind"] == "instant_cashback"] == []
    assert other


async def test_budget_is_never_exceeded_under_concurrent_payments(db):
    s = await shop(db)
    pid = await program(
        s, "instant_cashback", {"reward_paise": 1000, "min_spend_paise": 10000}, budget=3000, holdout=2000
    )
    refs = []
    for i in range(30):
        ref = payer(s, f"burst{i}")
        refs.append(ref)
    await asyncio.gather(*(pay(s, ref, 20000) for ref in refs))
    owed = await liability(s, pid)
    assert owed["issued_paise"] <= 3000
    assert owed["issued_paise"] == 3000  # enough treated payers to exhaust it exactly


async def test_payment_count_counts_only_received_non_refunded(db):
    s = await shop(db)
    pid = await program(s, "payment_count", {"reward_paise": 1500, "count": 3}, holdout=2000)
    ref = await treated_payer(s, pid)
    console = Session(s.mid, s.owner.actor_id, "owner", channel="console", step_up=True)
    first = await pay(s, ref, 1000)
    await run(
        s,
        "treasury.refund",
        {"payment_id": first["payment_id"], "amount_paise": 1000, "reason_key": "refund.customer"},
        actor=console,
    )
    s.bus.clock.set(s.bus.clock.now() + timedelta(hours=1))
    await pay(s, ref, 1000)
    s.bus.clock.set(s.bus.clock.now() + timedelta(days=1))
    assert (await pay(s, ref, 1000))["offers"] == []  # only 2 counted
    s.bus.clock.set(s.bus.clock.now() + timedelta(days=1))
    assert [o["kind"] for o in (await pay(s, ref, 1000))["offers"]] == ["count_reward"]


async def test_coupon_redeemed_at_counter_and_expiry_releases_liability(db):
    s = await shop(db)
    pid = await program(
        s, "first_time_coupon", {"reward_paise": 2000, "min_spend_paise": 20000, "validity_days": 14}
    )
    ref = await treated_payer(s, pid)
    code = (await pay(s, ref, 5000))["offers"][0]["code"]
    small = await new_bill(s, [{"item_id": s.items["PARLE"], "qty_milli": 1000, "added_via": "tap"}])
    with pytest.raises(CommandError, match="offers.min_spend_not_met"):
        await run(
            s,
            "counter.checkout",
            {"bill_id": small, "payments": [{"mode": "cash", "amount_paise": 0 + 1}], "coupon_code": code},
        )
    bill = await new_bill(s, [{"item_id": s.items["PARLE"], "qty_milli": 25000, "added_via": "tap"}])
    closed = await run(
        s,
        "counter.checkout",
        {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 23000}], "coupon_code": code},
    )
    assert closed["data"]["total_paise"] == 25000
    with pytest.raises(CommandError, match="offers.coupon_not_redeemable"):
        await run(
            s,
            "counter.checkout",
            {"bill_id": small, "payments": [{"mode": "cash", "amount_paise": 1}], "coupon_code": code},
        )
    await run(s, "offers.pause_program", {"program_id": pid})
    second = await program(
        s, "first_time_coupon", {"reward_paise": 1000, "min_spend_paise": 0, "validity_days": 1}
    )
    fresh = await treated_payer(s, second, "fresh")
    await pay(s, fresh, 5000)
    s.bus.clock.set(s.bus.clock.now() + timedelta(days=2))
    assert len((await run(s, "offers.expire_due", {}))["data"]["expired"]) >= 1
    owed = await liability(s)
    assert (
        owed["outstanding_paise"]
        == owed["issued_paise"] - owed["redeemed_paise"] - owed["expired_paise"]
        == 0
    )


async def test_pharmacy_rx_bill_earns_no_reward(db):
    s = await shop(db, "pharmacy")
    pid = await program(s, "instant_cashback", {"reward_paise": 1000, "min_spend_paise": 1000})
    ref = await treated_payer(s, pid)
    await receive(
        s, "AMOX", 5000, {"batch_no": "B", "expires_on": "2027-06-30", "mrp_paise": 9000, "cost_paise": 6000}
    )
    bill = await new_bill(
        s, [{"item_id": s.items["AMOX"], "qty_milli": 1000, "added_via": "scan", "rx_seen": True}]
    )
    intent = (await run(s, "counter.request_upi", {"bill_id": bill}))["data"]
    result = await pay(s, ref, 9000, mode="upi_qr", order_ref=intent["order_ref"])
    assert result["bill"]["status"] == "closed" and result["offers"] == []


# Tax and books


def cases(strategy, n=30):
    found = []

    @settings(max_examples=n, deadline=None, database=None)
    @given(strategy)
    def collect(case):
        found.append(case)

    collect()
    return found


async def test_tax_split_reconciles_to_the_paisa_property():
    from arth.domains.tax import split_line

    for amount, rate in cases(st.tuples(st.integers(0, 10**9), st.sampled_from([0, 500, 1200, 1800, 2800]))):
        taxable, cgst, sgst = split_line(amount, rate, "regular")
        assert taxable + cgst + sgst == amount
        assert abs(cgst - sgst) <= 1
        assert split_line(amount, rate, "composition") == (amount, 0, 0)


async def test_invoice_per_profile_gst_summary_and_month_close(db):
    from arth.domains.tax import gst_summary, invoice_view, profit_and_loss

    s = await shop(db)
    gate = await run(s, "merchant.update_settings", {"tax_profile": "regular", "gstin": "09ABCDE1234F1Z5"})
    if gate.get("status") == "needs_approval":
        await approve(s, gate)
    await receive(s, "PARLE", 50000, None)
    bills = []
    for qty in (3000, 7000):
        bill = await new_bill(
            s,
            [
                {"item_id": s.items["PARLE"], "qty_milli": qty, "added_via": "scan"},
                {"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"},
            ],
        )
        state_total = qty + 2700
        await run(
            s,
            "counter.checkout",
            {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": state_total}]},
        )
        bills.append(bill)
    invoice = await view(s, invoice_view, bills[0])
    assert invoice["kind"] == "tax_invoice" and invoice["number"].endswith("/000001")
    assert (
        invoice["taxable_paise"] + invoice["cgst_paise"] + invoice["sgst_paise"]
        == invoice["total_paise"]
        == 5700
    )
    month = (s.bus.clock.now() + timedelta(hours=5, minutes=30)).strftime("%Y-%m")
    summary = await view(s, gst_summary, month)
    assert summary["invoices"] == 2
    assert summary["totals"]["total_paise"] == 5700 + 9700
    assert [r["rate_bp"] for r in summary["rates"]] == [0, 1800]
    await approve(
        s,
        await run(
            s, "treasury.expense", {"category": "electricity", "amount_paise": 1000, "paid_from": "cash"}
        ),
    )
    pnl = await view(s, profit_and_loss, month)
    assert pnl["cogs_paise"] == 10 * 800  # salt has no stock record, so only Parle-G is costed
    assert pnl["net_paise"] == pnl["sales_paise"] - pnl["cogs_paise"] - 1000
    with pytest.raises(CommandError, match="books.month_not_over"):
        await run(s, "books.close_month", {"month": month})
    s.bus.clock.set(s.bus.clock.now() + timedelta(days=40))
    closed = await run(s, "books.close_month", {"month": month})
    assert closed["data"]["pnl"] == pnl and closed["data"]["gst"] == summary
    other = await shop(db, key=new_id("seed"))
    bill = await new_bill(other, [{"item_id": other.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])
    await run(
        other, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 2700}]}
    )
    assert (await view(other, invoice_view, bill))["kind"] == "receipt"
