"""T1.20 (STO-1, FBK-1, TRU-5, HLT-1), T1.21 (CAP-1…5) and T1.22 (SEN-1…3)."""

import json
from datetime import timedelta
from pathlib import Path

import pytest
from l1d_helpers import approve, new_bill, patron_account, run, shop, system, view

from arth.core.clock import iso_utc
from arth.core.paths import CONTRACTS_DIR, REPO_ROOT
from arth.governance.commands import CommandError
from arth.governance.policy import Session


def console(s):
    return Session(s.mid, s.owner.actor_id, "owner", channel="console", step_up=True)


async def test_storefront_price_equals_catalog_and_pharmacy_shows_otc_only(db):
    from arth.domains.catalog import catalog_rows
    from arth.domains.trust import public_storefront

    s = await shop(db, "pharmacy")
    with pytest.raises(CommandError, match="storefront.not_published"):
        await view(s, public_storefront, s.bus.clock, s.bus.packs)
    await run(s, "storefront.publish", {"slug": "city-medicals", "published": True, "show_offers": True})
    page = await view(s, public_storefront, s.bus.clock, s.bus.packs)
    assert [i["item_id"] for i in page["items"]] == [s.items["PARA"]]
    await approve(s, await run(s, "catalog.change_price", {"item_id": s.items["PARA"], "price_paise": 3200}))
    page = await view(s, public_storefront, s.bus.clock, s.bus.packs)
    catalog = {r["id"]: r["price_paise"] for r in await view(s, catalog_rows)}
    assert all(i["price_paise"] == catalog[i["item_id"]] for i in page["items"])  # STO-1 invariant
    assert page["items"][0]["in_stock"] is True  # untracked until received
    other = await shop(db, "kirana")
    with pytest.raises(CommandError, match="storefront.slug_taken"):
        await run(
            other, "storefront.publish", {"slug": "city-medicals", "published": True, "show_offers": False}
        )


async def test_feedback_one_rating_per_delivered_target(db):
    from arth.domains.trust import feedback_view

    s = await shop(db)
    bill = await new_bill(s, [{"item_id": s.items["SALT"], "qty_milli": 1000, "added_via": "tap"}])
    await run(s, "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": 2700}]})
    result = await run(
        s,
        "feedback.record",
        {"target_kind": "bill", "target_id": bill, "rating": 2, "complaint_key": "feedback.late"},
    )
    assert result["data"]["low"] is True
    with pytest.raises(CommandError, match="feedback.already_rated"):
        await run(s, "feedback.record", {"target_kind": "bill", "target_id": bill, "rating": 5})
    order = (
        await run(
            s,
            "orders.create_draft",
            {
                "channel": "whatsapp",
                "lines": [
                    {"item_id": s.items["SALT"], "text": "namak", "qty_milli": 1000, "confidence_bp": 9900}
                ],
            },
        )
    )["data"]["order_id"]
    with pytest.raises(CommandError, match="feedback.not_delivered"):
        await run(s, "feedback.record", {"target_kind": "order", "target_id": order, "rating": 4})
    assert (await view(s, feedback_view))["complaints"] == 1


async def test_erasure_removes_pii_keeps_ledger_totals_and_audit_verifies(db):
    from sqlalchemy import text

    from arth.domains.ledger_projection import statement
    from arth.domains.trust import patron_export
    from arth.governance.audit import verify_audit
    from arth.governance.repository import Repository

    s = await shop(db)
    patron, account = await patron_account(s, "Rohit Kumar", vpa="rohit.kumar@okbank")
    await s.services.patrons.add_member(s.owner, patron, "Mrs Kumarswamy", "member-1")
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
    await run(s, "privacy.export_patron", {"patron_id": patron})
    exported = await view(s, patron_export, s.bus.clock, patron)
    assert exported["patron"]["display_name"] == "Rohit Kumar" and exported["khata"]["balance_paise"] == 5000
    with pytest.raises(CommandError, match="policy.console_required"):
        await run(s, "privacy.erase_patron", {"patron_id": patron, "reason_key": "privacy.customer_request"})
    await run(
        s,
        "privacy.erase_patron",
        {"patron_id": patron, "reason_key": "privacy.customer_request"},
        actor=console(s),
    )
    async with db.read() as conn:
        tables = [
            r[0]
            for r in (await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))).all()
        ]
        for table in tables:
            for row in (await conn.execute(text(f'SELECT * FROM "{table}"'))).all():
                blob = json.dumps([str(v) for v in row]).lower()
                assert "rohit" not in blob and "kumarswamy" not in blob, table
        repo = Repository(conn, s.mid)
        assert (await statement(repo, account, s.bus.clock))[
            "balance_paise"
        ] == 5000  # tokenised totals remain
        assert (await verify_audit(repo))["valid"] is True


async def test_data_sharing_is_r2_and_device_health_recorded(db):
    from arth.domains.trust import latest_health

    s = await shop(db)
    gate = await run(s, "privacy.set_data_sharing", {"peer_benchmarks": True})
    assert gate["tier"] == "R2"
    await approve(s, gate)
    with pytest.raises(CommandError, match="device.not_found"):
        await run(
            s,
            "device.report_health",
            {
                "device_id": "device_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
                "connected": True,
                "battery_pct": 50,
                "mic_muted": False,
                "volume_pct": 40,
                "queue_size": 0,
            },
        )
    await run(
        s,
        "device.report_health",
        {
            "device_id": s.device_id,
            "connected": False,
            "battery_pct": 15,
            "mic_muted": True,
            "volume_pct": 40,
            "queue_size": 3,
        },
    )
    health = await view(s, latest_health)
    assert (health["connected"], health["battery_pct"], health["queue_size"]) == (False, 15, 3)


async def lender_offer(s, amount, edi, tenor=90):
    payload = {
        "lender": "Sandbox NBFC",
        "amount_paise": amount,
        "tenor_days": tenor,
        "apr_bp": 2400,
        "edi_paise": edi,
        "processing_fee_paise": 5000,
        "kfs_url": "https://lender.example/kfs",
        "cooling_off_days": 3,
        "expires_at": iso_utc(s.bus.clock.now() + timedelta(days=7)),
    }
    with pytest.raises(CommandError, match="capital.verified_lender_required"):
        await run(s, "capital.record_offer", payload)
    return (
        await run(s, "capital.record_offer", payload, actor=system(s), private={"lender_verified": True})
    )["data"]["offer_id"]


async def test_capital_need_affordability_offers_and_console_only_apply(db):
    from arth.domains.capital import AGENT_TOOLS, capital_view

    s = await shop(db)
    for day in range(28):  # ₹1,000 a day of verified UPI inflow
        s.bus.clock.set(s.bus.clock.now() + timedelta(days=1))
        await run(
            s,
            "treasury.rails_event",
            {
                "status": "success",
                "utr": f"4303000000{day:02d}",
                "amount_paise": 100000,
                "mode": "upi_static",
            },
            actor=system(s),
            private={"payment_verified": True},
        )
    supplier = (await run(s, "supply.add_supplier", {"name": "Agarwal", "lang": "hi", "lead_days": 3}))[
        "data"
    ]["supplier_id"]
    po = (
        await run(
            s,
            "supply.draft_po",
            {
                "supplier_id": supplier,
                "lines": [{"item_id": s.items["SUGAR"], "qty_milli": 200000, "unit_price_paise": 4500}],
            },
        )
    )["data"]["po_id"]
    await approve(s, await run(s, "supply.place_po", {"po_id": po}))
    s.bus.clock.set(s.bus.clock.now() + timedelta(seconds=31))
    await s.bus.run_due(s.mid)
    small = await lender_offer(s, 500000, 6000)
    fits = await lender_offer(s, 700000, 10000)
    await lender_offer(s, 2000000, 30000)  # EDI above the cap
    page = await view(s, capital_view, s.bus.clock)
    assert page["need"]["purpose_ref"] == po and page["need"]["shortfall_paise"] == 900000 - 3 * 100000
    assert page["affordability"]["max_edi_paise"] == 12000  # 15% of (₹1,000 × 0.8)
    assert [o["affordable"] for o in page["offers"]] == [True, True, False]
    assert page["recommended_offer_id"] == fits and small != fits
    assert all(
        len(o["kfs_url"]) and o["cooling_off_days"] >= 0 and o["apr_bp"] >= 0 for o in page["offers"]
    )  # CAP-4
    assert page["console_pointer"]["route"] == "/console/capital"
    assert not [name for name in AGENT_TOOLS if "apply" in name]  # CAP-5: no apply tool for agents
    for channel in ("device", "voice"):
        with pytest.raises(CommandError, match="policy.console_required"):
            await run(
                s,
                "capital.apply",
                {"offer_id": fits},
                actor=Session(s.mid, s.owner.actor_id, "owner", channel=channel, owner_ptt=True),
            )
    applied = await run(s, "capital.apply", {"offer_id": fits}, actor=console(s))
    assert applied["data"]["status"] == "submitted"


def sentinel_fixtures(utr_paid, utr_pending, now):
    """30 cases with extracted fields given (SEN-1). 15 must be 'not_received'."""
    received = [{"amount_paise": 50000, "utr": utr_paid, "paid_at": now}] * 5 + [
        {"amount_paise": 50000, "utr": utr_paid, "paid_at": now, "payee_ref": "x", "ela_score_bp": 9000}
    ] * 5
    not_received = [
        {"amount_paise": 50000 + i, "utr": f"99990000{i:04d}", "paid_at": now} for i in range(10)
    ] + [{"amount_paise": 777700 + i} for i in range(5)]
    other = [{"amount_paise": 20000, "utr": utr_pending}] * 3 + [{"amount_paise": 51000, "utr": utr_paid}] * 2
    return (
        [(c, "received") for c in received]
        + [(c, "not_received") for c in not_received]
        + [(c, "pending") for c in other[:3]]
        + [(c, "unclear") for c in other[3:]]
    )


async def test_sentinel_recall_on_thirty_fixtures_and_signals_never_decide(db):
    from arth.domains.sentinel import verdict_view

    s = await shop(db)
    now = iso_utc(s.bus.clock.now())
    for utr, status, amount in [("430400000001", "success", 50000), ("430400000002", "pending", 20000)]:
        await run(
            s,
            "treasury.rails_event",
            {"status": status, "utr": utr, "amount_paise": amount, "mode": "upi_static"},
            actor=system(s),
            private={"payment_verified": True},
        )
    cases = sentinel_fixtures("430400000001", "430400000002", now)
    assert len(cases) == 30
    results = []
    for fields, expected in cases:
        results.append(((await run(s, "sentinel.check", fields))["data"], expected))
    truly_not = [r for r, e in results if e == "not_received"]
    assert len(truly_not) == 15 and all(r["verdict"] == "not_received" for r in truly_not)  # recall 1.00
    assert all(r["verdict"] == e for r, e in results)
    noisy = results[5][0]
    assert {"kind": "edit_level", "state": "high"} in noisy["signals"] and noisy["verdict"] == "received"
    page = await view(s, verdict_view, truly_not[0]["check_id"])
    assert (
        page["headline_key"] == "sentinel.not_received_yet" and page["footnote_key"] == "sentinel.ledger_only"
    )


def test_no_user_facing_string_says_fake():
    roots = [
        CONTRACTS_DIR,
        REPO_ROOT / "backend" / "arth",
        REPO_ROOT / "backend" / "config",
        REPO_ROOT / "backend" / "packs",
    ]
    offenders = [
        str(p)
        for root in roots
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix in {".json", ".py", ".yaml", ".csv", ".ts"}
        and "fake" in p.read_text(encoding="utf-8", errors="ignore").lower()
    ]
    assert offenders == [], offenders  # SEN-3
    assert Path(__file__).exists()
