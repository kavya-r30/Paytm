"""T1.12 Counter: CTR-2…5, CTR-9…10, CAFE-1…3, PHAR-2, EXP-5."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from l1d_helpers import approve, new_bill, patron_account, receive, run, shop, staff, view

from arth.governance.commands import CommandError


async def state(s, bill):
    from arth.domains.counter import bill_state

    return await view(s, bill_state, bill)


async def test_loose_by_amount_and_cash_change_close_bill_and_issue_stock(db):
    from arth.domains.commerce_tables import bill_payments
    from arth.domains.stock import on_hand
    from arth.governance.repository import Repository

    s = await shop(db)
    await receive(s, "SUGAR", 10000)
    bill = await new_bill(
        s,
        [
            {"item_id": s.items["SUGAR"], "amount_paise": 3000, "added_via": "voice"},
            {"item_id": s.items["PARLE"], "qty_milli": 2000, "added_via": "scan"},
        ],
    )
    current = await state(s, bill)
    assert current["lines"][0]["qty_milli"] == 667  # Counter computes ₹30 / ₹45 per kg, half-even
    assert current["lines"][0]["amount_paise"] == 3000
    assert current["total_paise"] == 5000
    with pytest.raises(CommandError, match="counter.payment_mismatch"):
        await run(
            s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 4000}]}
        )
    with pytest.raises(CommandError, match="counter.tendered_short"):
        await run(
            s,
            "counter.checkout",
            {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 5000, "tendered_paise": 4000}]},
        )
    result = await run(
        s,
        "counter.checkout",
        {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 5000, "tendered_paise": 10000}]},
    )
    assert result["data"] == {"bill_id": bill, "status": "closed", "change_paise": 5000, "total_paise": 5000}
    async with db.read() as conn:
        repo = Repository(conn, s.mid)
        assert await on_hand(repo, s.items["SUGAR"]) == 10000 - 667
        rows = await repo.select(bill_payments, bill_payments.c.bill_id == bill)
        assert [(r["mode"], r["amount_paise"], r["change_paise"]) for r in rows] == [("cash", 5000, 5000)]
    with pytest.raises(CommandError, match="counter.bill_not_open"):
        await run(
            s,
            "counter.add_lines",
            {"bill_id": bill, "lines": [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}]},
        )


async def test_running_tab_edits_and_undo_restore_prior_state(db):
    s = await shop(db)
    bill = await new_bill(s, [{"item_id": s.items["PARLE"], "qty_milli": 1000, "added_via": "voice"}])
    line = (await state(s, bill))["lines"][0]["id"]
    await run(s, "counter.set_qty", {"bill_id": bill, "line_id": line, "qty_milli": 3000})  # "nahi, teen"
    assert [(r["qty_milli"], r["amount_paise"]) for r in (await state(s, bill))["lines"]] == [(3000, 3000)]
    await run(s, "counter.undo", {"bill_id": bill})
    restored = await state(s, bill)
    assert [(r["id"], r["qty_milli"]) for r in restored["lines"]] == [(line, 1000)]
    await run(s, "counter.remove_line", {"bill_id": bill, "line_id": line})  # "hatao"
    assert (await state(s, bill))["lines"] == []
    await run(s, "counter.undo", {"bill_id": bill})
    assert [r["id"] for r in (await state(s, bill))["lines"]] == [line]
    with pytest.raises(CommandError, match="counter.line_not_found"):
        await run(s, "counter.remove_line", {"bill_id": bill, "line_id": "bline_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"})


async def test_two_bills_park_and_resume_keep_lines(db):
    s = await shop(db)
    first = await new_bill(s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])
    await run(s, "counter.park", {"bill_id": first})
    second = await new_bill(s, [{"item_id": s.items["PARLE"], "qty_milli": 1000, "added_via": "tap"}])
    with pytest.raises(CommandError, match="counter.bill_not_open"):
        await run(
            s,
            "counter.add_lines",
            {
                "bill_id": first,
                "lines": [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}],
            },
        )
    await run(s, "counter.park", {"bill_id": second})
    await run(s, "counter.resume", {"bill_id": first})
    assert (await state(s, first))["total_paise"] == 2700
    assert (await state(s, second))["status"] == "parked"
    assert (await state(s, second))["total_paise"] == 1000


async def test_price_guard_requires_owner_or_manager_reason_and_logs(db):
    from arth.governance.repository import Repository
    from arth.governance.tables import outbox

    s = await shop(db)
    cashier = await staff(s, "cashier", "c1")
    bill = await new_bill(s, [], actor=cashier)
    cheap = {"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap", "unit_price_paise": 1500}
    with pytest.raises(CommandError, match="counter.price_guard"):
        await run(s, "counter.add_lines", {"bill_id": bill, "lines": [cheap]}, actor=cashier)
    with pytest.raises(CommandError, match="counter.price_guard"):
        await run(s, "counter.add_lines", {"bill_id": bill, "lines": [cheap]})  # owner but no reason
    await run(
        s, "counter.add_lines", {"bill_id": bill, "lines": [{**cheap, "reason_key": "price.old_stock"}]}
    )
    small = {"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap", "unit_price_paise": 2500}
    await run(s, "counter.add_lines", {"bill_id": bill, "lines": [small]}, actor=cashier)  # within 25%
    async with db.read() as conn:
        logged = await Repository(conn, s.mid).select(outbox, outbox.c.type == "bill.price_override")
    assert len(logged) == 2
    assert [line["price_override"] for line in (await state(s, bill))["lines"]] == [True, True]


async def test_khata_checkout_is_r2_keeps_bill_lines_and_reconciles(db):
    from arth.domains.ledger import account_view
    from arth.domains.ledger_tables import credit_entries, credit_entry_lines
    from arth.governance.repository import Repository

    s = await shop(db)
    patron, account = await patron_account(s, limit=10000)
    bill = await new_bill(
        s, [{"item_id": s.items["PARLE"], "qty_milli": 9000, "added_via": "tap"}], patron_id=patron
    )
    gate = await run(
        s,
        "counter.checkout_khata",
        {"bill_id": bill, "account_id": account, "khata_paise": 9000, "payments": []},
    )
    result = await approve(s, gate)
    assert result["data"]["status"] == "closed"
    async with db.read() as conn:
        repo = Repository(conn, s.mid)
        entry = (await repo.select(credit_entries, credit_entries.c.ref_id == bill))[0]
        lines = await repo.select(credit_entry_lines, credit_entry_lines.c.entry_id == entry["id"])
        assert entry["amount_paise"] == 9000 and entry["source"] == "counter"
        assert [(r["item_id"], r["qty_milli"], r["amount_paise"]) for r in lines] == [
            (s.items["PARLE"], 9000, 9000)
        ]
        assert (await account_view(repo, account, s.bus.clock))["balance_paise"] == 9000
    over = await new_bill(
        s, [{"item_id": s.items["PARLE"], "qty_milli": 2000, "added_via": "tap"}], patron_id=patron
    )
    with pytest.raises(CommandError, match="ledger.over_limit"):
        await run(
            s,
            "counter.checkout_khata",
            {
                "bill_id": over,
                "account_id": account,
                "khata_paise": 1500,
                "payments": [{"mode": "cash", "amount_paise": 500}],
            },
        )
    gate = await run(
        s,
        "counter.checkout_khata",
        {
            "bill_id": over,
            "account_id": account,
            "khata_paise": 1500,
            "payments": [{"mode": "cash", "amount_paise": 500}],
            "limit_override": True,
            "reason_key": "ledger.regular",
        },
    )
    assert (await approve(s, gate))["data"]["status"] == "closed"
    closed = await state(s, over)
    assert closed["paid_paise"] + closed["khata_paise"] == closed["total_paise"] == 2000


def cases(strategy, n=25):
    """Collect Hypothesis-generated cases once; the async body then checks each on one fixture shop."""
    found = []

    @settings(max_examples=n, deadline=None, database=None)
    @given(strategy)
    def collect(case):
        found.append(case)

    collect()
    return found


async def test_property_payments_plus_khata_equal_total(db):
    s = await shop(db)
    patron, account = await patron_account(s, limit=10**9)
    strategy = st.tuples(st.lists(st.integers(1, 9000), min_size=1, max_size=4), st.integers(0, 100))
    for qtys, split in cases(strategy):
        bill = await new_bill(
            s,
            [{"item_id": s.items["SUGAR"], "qty_milli": q, "added_via": "tap"} for q in qtys],
            patron_id=patron,
        )
        total = (await state(s, bill))["total_paise"]
        khata = total * split // 100
        payments = [{"mode": "card", "amount_paise": total - khata}] if total - khata else []
        if khata:
            await approve(
                s,
                await run(
                    s,
                    "counter.checkout_khata",
                    {"bill_id": bill, "account_id": account, "khata_paise": khata, "payments": payments},
                ),
            )
        else:
            await run(s, "counter.checkout", {"bill_id": bill, "payments": payments})
        closed = await state(s, bill)
        assert closed["status"] == "closed"
        assert closed["paid_paise"] + closed["khata_paise"] == closed["total_paise"] == total
        assert closed["due_paise"] == 0


async def test_returns_reverse_stock_and_money_with_new_rows_upi_needs_console(db):
    from arth.domains.commerce_tables import payment_exceptions, refunds
    from arth.domains.stock import on_hand
    from arth.governance.repository import Repository

    s = await shop(db)
    await receive(s, "SALT", 5000)
    bill = await new_bill(s, [{"item_id": s.items["SALT"], "qty_milli": 2000, "added_via": "tap"}])
    await run(s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 5400}]})
    line = (await state(s, bill))["lines"][0]["id"]
    payload = {
        "bill_id": bill,
        "lines": [{"line_id": line, "qty_milli": 1000}],
        "reason_key": "return.damaged",
        "refund_mode": "cash",
    }
    cashier = await staff(s, "cashier", "r")
    with pytest.raises(CommandError, match="policy.role"):
        await run(s, "counter.return", payload, actor=cashier)
    result = await approve(s, await run(s, "counter.return", payload))
    assert result["data"]["amount_paise"] == 2700
    with pytest.raises(CommandError, match="counter.return_exceeds_sold"):
        await approve(
            s, await run(s, "counter.return", {**payload, "lines": [{"line_id": line, "qty_milli": 1500}]})
        )
    upi = await approve(s, await run(s, "counter.return", {**payload, "refund_mode": "upi"}))
    assert upi["data"]["status"] == "refund_pending"
    async with db.read() as conn:
        repo = Repository(conn, s.mid)
        assert await on_hand(repo, s.items["SALT"]) == 5000
        assert [r["amount_paise"] for r in await repo.select(refunds)] == [2700]
        assert [r["kind"] for r in await repo.select(payment_exceptions)] == ["refund_due"]


async def test_void_requires_reason_permission_and_no_payment(db):
    s = await shop(db)
    helper = await staff(s, "helper", "h")
    bill = await new_bill(
        s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}], actor=helper
    )
    with pytest.raises(CommandError, match="policy.role"):
        await run(s, "counter.void_bill", {"bill_id": bill, "reason_key": "void.customer_left"}, actor=helper)
    await run(s, "counter.void_bill", {"bill_id": bill, "reason_key": "void.customer_left"})
    assert (await state(s, bill))["status"] == "voided"


async def test_cafe_modifiers_priced_by_code_recipe_consumes_ingredients_and_kot(db):
    from arth.domains.catalog import get_item
    from arth.domains.stock import on_hand
    from arth.governance.repository import Repository

    s = await shop(db, "cafe")
    await receive(s, "MILK", 1_000_000)
    chai = await view(s, get_item, s.items["CHAI"])
    size, sugar = chai["modifier_groups"]
    large = next(o["id"] for o in size["options"] if o["name"] == "Large")
    with pytest.raises(CommandError, match="catalog.invalid_modifier"):
        await new_bill(s, [{"item_id": s.items["CHAI"], "qty_milli": 1000, "added_via": "tap"}])
    bill = await new_bill(
        s,
        [
            {
                "item_id": s.items["CHAI"],
                "qty_milli": 2000,
                "added_via": "tap",
                "modifier_ids": [large, sugar["options"][0]["id"]],
            }
        ],
    )
    assert (await state(s, bill))["total_paise"] == 6000
    ticket = (await run(s, "counter.send_to_kitchen", {"bill_id": bill}))["data"]
    assert ticket["token"] == 1 and ticket["status"] == "new"
    with pytest.raises(CommandError, match="counter.illegal_ticket_transition"):
        await run(s, "counter.advance_ticket", {"ticket_id": ticket["ticket_id"], "to": "served"})
    for to in ("preparing", "ready", "served"):
        await run(s, "counter.advance_ticket", {"ticket_id": ticket["ticket_id"], "to": to})
    second = await new_bill(
        s, [{"item_id": s.items["CHAI"], "qty_milli": 1000, "added_via": "tap", "modifier_ids": [large]}]
    )
    assert (await run(s, "counter.send_to_kitchen", {"bill_id": second}))["data"]["token"] == 2
    await run(s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 6000}]})
    async with db.read() as conn:
        assert await on_hand(Repository(conn, s.mid), s.items["MILK"]) == 1_000_000 - 300_000


async def test_kirana_has_no_tickets(db):
    s = await shop(db)
    bill = await new_bill(s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])
    with pytest.raises(CommandError, match="counter.tickets_disabled"):
        await run(s, "counter.send_to_kitchen", {"bill_id": bill})


async def test_pharmacy_rx_seen_required_and_recalled_batch_cannot_be_billed(db):
    from arth.domains.commerce_tables import rx_records
    from arth.governance.repository import Repository

    s = await shop(db, "pharmacy")
    batch = {"batch_no": "A1", "expires_on": "2027-06-30", "mrp_paise": 9000, "cost_paise": 6000}
    received = await receive(s, "AMOX", 2000, batch)
    line = {"item_id": s.items["AMOX"], "qty_milli": 1000, "added_via": "scan"}
    with pytest.raises(CommandError, match="counter.rx_required"):
        await new_bill(s, [line])
    bill = await new_bill(s, [{**line, "rx_seen": True}])
    async with db.read() as conn:
        rows = await Repository(conn, s.mid).select(rx_records)
    assert [(r["bill_id"], r["staff_id"]) for r in rows] == [(bill, s.owner.actor_id)]
    await run(
        s,
        "stock.recall_batch",
        {"batch_id": received["data"]["batch_id"], "reason": "stock.distributor_recall"},
    )
    with pytest.raises(CommandError, match="stock.insufficient_sellable"):
        await run(
            s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 9000}]}
        )


async def test_salon_services_bill_without_stock(db):
    s = await shop(db, "salon")
    bill = await new_bill(s, [{"item_id": s.items["HAIRCUT"], "qty_milli": 1000, "added_via": "tap"}])
    result = await run(
        s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "card", "amount_paise": 20000}]}
    )
    assert result["data"]["status"] == "closed"


async def test_bills_are_tenant_scoped(db):
    a = await shop(db, key="tenant-a")
    b = await shop(db, key="tenant-b")
    bill = await new_bill(a, [{"item_id": a.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])
    with pytest.raises(CommandError, match="counter.bill_not_found"):
        await run(b, "counter.park", {"bill_id": bill})
