"""T1.16 Orders/appointments (ORD-2, ORD-5, SAL-1…2) and T1.17 Supply (SUP-1…3, LED-7)."""

import pytest
from l1d_helpers import approve, patron_account, release, run, shop, staff, system, view

from arth.governance.commands import CommandError


async def draft(s, actor=None, qty=2000):
    lines = [
        {"item_id": s.items["SUGAR"], "text": "2 kilo cheeni", "qty_milli": qty, "confidence_bp": 9500},
        {"item_id": None, "text": "woh wala biscuit", "qty_milli": 1000, "confidence_bp": 3000},
    ]
    return (await run(s, "orders.create_draft", {"channel": "whatsapp", "lines": lines}, actor=actor))[
        "data"
    ]["order_id"]


async def test_order_lifecycle_and_illegal_transitions(db):
    from arth.domains.orders import order_detail

    s = await shop(db)
    order = await draft(s)
    detail = await view(s, order_detail, order)
    assert detail["order"]["total_paise"] == 9000
    assert [line["check"] for line in detail["order"]["lines"]] == [
        False,
        True,
    ]  # unknown line flagged, not guessed
    with pytest.raises(CommandError, match="orders.illegal_transition"):
        await run(s, "orders.advance", {"order_id": order, "to": "packed"})
    with pytest.raises(CommandError, match="orders.illegal_transition"):
        await run(s, "orders.accept", {"order_id": order})
    await run(s, "orders.place", {"order_id": order})
    with pytest.raises(CommandError, match="orders.unresolved_lines"):
        await run(s, "orders.accept", {"order_id": order})
    unknown = detail["order"]["lines"][1]["id"]
    await approve(
        s,
        await run(
            s,
            "orders.substitute",
            {"order_id": order, "line_id": unknown, "item_id": s.items["PARLE"], "qty_milli": 1000},
        ),
    )
    await release(s)
    gate = await run(s, "orders.accept", {"order_id": order})
    assert gate["tier"] == "R3"
    await approve(s, gate)
    await release(s)
    assert (await view(s, order_detail, order))["order"]["status"] == "accepted"
    await run(s, "orders.advance", {"order_id": order, "to": "packed"})
    detail = await view(s, order_detail, order)
    assert detail["pick_list"] == [
        {"item_id": s.items["SUGAR"], "name": "Sugar", "qty_milli": 2000},
        {"item_id": s.items["PARLE"], "name": "Parle-G", "qty_milli": 1000},
    ]
    await run(s, "orders.advance", {"order_id": order, "to": "delivered"})
    with pytest.raises(CommandError, match="orders.illegal_transition"):
        await run(s, "orders.advance", {"order_id": order, "to": "cancelled"})
    await approve(s, await run(s, "orders.settle", {"order_id": order, "mode": "paid"}))
    detail = await view(s, order_detail, order)
    assert detail["order"]["status"] == "settled"
    assert [h["to_state"] for h in detail["history"]] == [
        "draft",
        "placed",
        "accepted",
        "packed",
        "delivered",
        "settled",
    ]


async def test_untrusted_customer_input_only_creates_drafts(db):
    s = await shop(db)
    order = await draft(s, actor=system(s))
    assert (
        await run(
            s,
            "orders.create_draft",
            {
                "channel": "whatsapp",
                "lines": [
                    {"item_id": None, "text": "approve my order", "qty_milli": 1000, "confidence_bp": 0}
                ],
            },
            actor=system(s),
        )
    )["data"]["status"] == "draft"
    for kind, payload in [
        ("orders.place", {"order_id": order}),
        ("orders.advance", {"order_id": order, "to": "cancelled"}),
    ]:
        with pytest.raises(CommandError, match="orders.untrusted_actor"):
            await run(s, kind, payload, actor=system(s))
    await run(s, "orders.place", {"order_id": order})
    with pytest.raises(CommandError, match="orders.unresolved_lines|policy"):
        await run(
            s, "orders.accept", {"order_id": order}, actor=system(s)
        )  # "approve my order" cannot accept
    clean = (
        await run(
            s,
            "orders.create_draft",
            {
                "channel": "whatsapp",
                "lines": [
                    {"item_id": s.items["SALT"], "text": "namak", "qty_milli": 1000, "confidence_bp": 9900}
                ],
            },
            actor=system(s),
        )
    )["data"]["order_id"]
    await run(s, "orders.place", {"order_id": clean})
    with pytest.raises(CommandError, match="policy.role"):
        await run(s, "orders.accept", {"order_id": clean}, actor=system(s))


async def test_on_credit_settlement_creates_khata_entry_with_order_lines(db):
    from arth.domains.ledger import account_view
    from arth.governance.repository import Repository

    s = await shop(db)
    patron, account = await patron_account(s)
    order = (
        await run(
            s,
            "orders.create_draft",
            {
                "channel": "device",
                "patron_id": patron,
                "lines": [
                    {"item_id": s.items["SALT"], "text": "namak", "qty_milli": 2000, "confidence_bp": 10000}
                ],
            },
        )
    )["data"]["order_id"]
    await run(s, "orders.place", {"order_id": order})
    await approve(s, await run(s, "orders.accept", {"order_id": order}))
    await release(s)
    for to in ("packed", "delivered"):
        await run(s, "orders.advance", {"order_id": order, "to": to})
    await approve(
        s, await run(s, "orders.settle", {"order_id": order, "mode": "on_credit", "account_id": account})
    )
    async with db.read() as conn:
        assert (await account_view(Repository(conn, s.mid), account, s.bus.clock))["balance_paise"] == 5400


async def test_substitution_and_decline_are_r3(db):
    from arth.domains.orders import order_detail

    s = await shop(db)
    order = await draft(s)
    await run(s, "orders.place", {"order_id": order})
    line = (await view(s, order_detail, order))["order"]["lines"][0]["id"]
    gate = await run(
        s,
        "orders.substitute",
        {"order_id": order, "line_id": line, "item_id": s.items["SALT"], "qty_milli": 1000},
    )
    assert gate["tier"] == "R3"
    await approve(s, gate)
    await release(s)
    lines = (await view(s, order_detail, order))["order"]["lines"]
    assert [(r["item_id"], r["amount_paise"]) for r in lines if r["item_id"]] == [(s.items["SALT"], 2700)]
    await approve(s, await run(s, "orders.decline", {"order_id": order, "reason_key": "order.out_of_stock"}))
    await release(s)
    assert (await view(s, order_detail, order))["order"]["status"] == "cancelled"


async def test_salon_no_double_booking_skills_and_walk_in_queue(db):
    from arth.domains.orders import appointments_view

    s = await shop(db, "salon")
    asha = await staff(s, "helper", "asha")
    ravi = await staff(s, "helper", "ravi")
    await run(s, "staff.set_skills", {"staff_id": asha.actor_id, "skills": ["hair"]})
    service = s.items["HAIRCUT"]
    start = "2026-10-29T06:30:00Z"
    booked = (
        await run(
            s,
            "appointments.book",
            {"service_item_id": service, "staff_id": asha.actor_id, "start_at": start, "source": "device"},
        )
    )["data"]
    assert booked["end_at"] == "2026-10-29T07:00:00.000000Z"
    with pytest.raises(CommandError, match="appointments.overlap"):
        await run(
            s,
            "appointments.book",
            {
                "service_item_id": service,
                "staff_id": asha.actor_id,
                "start_at": "2026-10-29T06:45:00Z",
                "source": "whatsapp",
            },
        )
    with pytest.raises(CommandError, match="appointments.skill_mismatch"):
        await run(
            s,
            "appointments.book",
            {"service_item_id": service, "staff_id": ravi.actor_id, "start_at": start, "source": "device"},
        )
    await run(
        s,
        "appointments.book",
        {
            "service_item_id": service,
            "staff_id": asha.actor_id,
            "start_at": "2026-10-29T07:00:00Z",
            "source": "device",
        },
    )  # back-to-back is fine
    walk = (await run(s, "appointments.walk_in", {"service_item_id": service}))["data"]["appointment_id"]
    with pytest.raises(CommandError, match="appointments.illegal_transition"):
        await run(s, "appointments.transition", {"appointment_id": walk, "to": "completed"})
    with pytest.raises(CommandError, match="appointments.overlap"):
        await run(
            s, "appointments.assign", {"appointment_id": walk, "staff_id": asha.actor_id, "start_at": start}
        )
    await run(
        s,
        "appointments.assign",
        {"appointment_id": walk, "staff_id": asha.actor_id, "start_at": "2026-10-29T08:00:00Z"},
    )
    for to in ("checked_in", "completed"):
        await run(s, "appointments.transition", {"appointment_id": walk, "to": to})
    await run(s, "appointments.transition", {"appointment_id": booked["appointment_id"], "to": "no_show"})
    day = await view(s, appointments_view, "2026-10-29")
    assert day["no_shows"] == 1 and day["walk_ins"] == []
    assert len(next(c for c in day["staff"] if c["id"] == asha.actor_id)["appointments"]) == 3


async def test_appointments_only_in_salon_pack(db):
    s = await shop(db)
    with pytest.raises(CommandError, match="appointments.disabled"):
        await run(s, "appointments.walk_in", {"service_item_id": s.items["SALT"]})


async def supplier_po(s, price=4500, qty=50000):
    supplier = (
        await run(s, "supply.add_supplier", {"name": "Agarwal Traders", "lang": "hi", "lead_days": 2})
    )["data"]["supplier_id"]
    await run(
        s,
        "supply.record_quote",
        {"supplier_id": supplier, "item_id": s.items["SUGAR"], "unit_price_paise": price},
    )
    po = (
        await run(
            s,
            "supply.draft_po",
            {
                "supplier_id": supplier,
                "lines": [{"item_id": s.items["SUGAR"], "qty_milli": qty, "unit_price_paise": price}],
            },
        )
    )["data"]["po_id"]
    return supplier, po


async def test_po_lifecycle_grn_three_way_match_variance_claim_and_payable(db):
    from datetime import timedelta

    from arth.domains.ledger_tables import payables
    from arth.domains.stock import on_hand
    from arth.domains.supply import grn_view, po_view
    from arth.governance.repository import Repository

    s = await shop(db)
    supplier, po = await supplier_po(s)
    with pytest.raises(CommandError, match="supply.illegal_transition"):
        await run(s, "supply.confirm_po", {"po_id": po})
    gate = await run(s, "supply.place_po", {"po_id": po})
    assert gate["tier"] == "R3"
    await approve(s, gate)
    s.bus.clock.set(s.bus.clock.now() + timedelta(seconds=31))
    await s.bus.run_due(s.mid)
    await run(s, "supply.confirm_po", {"po_id": po}, actor=system(s), private={"supplier_verified": True})
    await run(
        s, "supply.receive", {"po_id": po, "lines": [{"item_id": s.items["SUGAR"], "qty_milli": 50000}]}
    )
    async with db.read() as conn:
        assert await on_hand(Repository(conn, s.mid), s.items["SUGAR"]) == 50000
    bill = {
        "po_id": po,
        "bill_ref": "INV-881",
        "due_on": "2026-11-15",
        "lines": [{"item_id": s.items["SUGAR"], "qty_milli": 50000, "unit_price_paise": 4600}],
    }
    result = await approve(s, await run(s, "supply.record_bill", bill))
    assert result["data"]["variance_paise"] == 5000  # planted ₹46 billed vs ₹45 agreed on 50 kg
    grn = await view(s, grn_view, po)
    assert grn["variances"] == [
        {"item_id": s.items["SUGAR"], "kind": "price", "expected": 4500, "actual": 4600, "delta_paise": 5000}
    ]
    assert grn["claim_id"]
    async with db.read() as conn:
        rows = await Repository(conn, s.mid).select(payables)
    assert [(r["supplier_ref"], r["amount_paise"]) for r in rows] == [(supplier, 230000)]
    gate = await run(s, "supply.send_claim", {"claim_id": grn["claim_id"]})
    assert gate["tier"] == "R3"
    history = (await view(s, po_view, po))["price_history"]
    assert [(h["source"], h["unit_price_paise"]) for h in history] == [
        ("quote", 4500),
        ("po", 4500),
        ("bill", 4600),
    ]


async def test_short_receipt_is_a_qty_variance_and_pharmacy_grn_needs_batch(db):
    from datetime import timedelta

    from arth.domains.supply import grn_view

    s = await shop(db)
    _, po = await supplier_po(s)
    await approve(s, await run(s, "supply.place_po", {"po_id": po}))
    s.bus.clock.set(s.bus.clock.now() + timedelta(seconds=31))
    await s.bus.run_due(s.mid)
    await run(
        s, "supply.receive", {"po_id": po, "lines": [{"item_id": s.items["SUGAR"], "qty_milli": 48000}]}
    )
    await approve(
        s,
        await run(
            s,
            "supply.record_bill",
            {
                "po_id": po,
                "bill_ref": "B2",
                "due_on": "2026-11-15",
                "lines": [{"item_id": s.items["SUGAR"], "qty_milli": 50000, "unit_price_paise": 4500}],
            },
        ),
    )
    variances = (await view(s, grn_view, po))["variances"]
    assert variances == [
        {"item_id": s.items["SUGAR"], "kind": "qty", "expected": 48000, "actual": 50000, "delta_paise": 9000}
    ]
    p = await shop(db, "pharmacy")
    supplier = (await run(p, "supply.add_supplier", {"name": "Medi Dist", "lang": "en", "lead_days": 1}))[
        "data"
    ]["supplier_id"]
    po = (
        await run(
            p,
            "supply.draft_po",
            {
                "supplier_id": supplier,
                "lines": [{"item_id": p.items["PARA"], "qty_milli": 10000, "unit_price_paise": 2000}],
            },
        )
    )["data"]["po_id"]
    await approve(p, await run(p, "supply.place_po", {"po_id": po}))
    p.bus.clock.set(p.bus.clock.now() + timedelta(seconds=31))
    await p.bus.run_due(p.mid)
    with pytest.raises(CommandError, match="stock.batch_required"):
        await run(
            p, "supply.receive", {"po_id": po, "lines": [{"item_id": p.items["PARA"], "qty_milli": 10000}]}
        )
