from dataclasses import replace
from datetime import timedelta

import pytest
from l1c_helpers import fixture_shop
from test_l1c_ledger import charge, fixture_ledger
from test_l1c_review import approved

from arth.core.ids import new_id
from arth.core.spans import SpanBus
from arth.domains.patrons import PatronService, has_consent
from arth.domains.stock import issue_stock, register_stock
from arth.governance.commands import CommandError
from arth.governance.repository import Repository
from arth.governance.tables import outbox


async def test_required_batches_expiry_day_unsafe_override_and_atomic_issue(db):
    bus, actor, item = await fixture_shop(db)
    pack = bus.packs.get("kirana").model_copy(deep=True)
    pack.stock.batches, pack.stock.expiry = "required", "required"
    bus.packs._manifests["kirana"] = pack
    register_stock(bus, bus.packs)
    with pytest.raises(CommandError, match="batch_required"):
        await bus.submit(actor, "stock.receive", {"item_id": item, "qty_milli": 5000}, "no-batch")
    batch = {"batch_no": "A", "mrp_paise": 3000, "cost_paise": 2000}
    with pytest.raises(CommandError, match="expiry_required"):
        await bus.submit(
            actor, "stock.receive", {"item_id": item, "qty_milli": 5000, "batch": batch}, "no-expiry"
        )
    batch["expires_on"] = bus.clock.now_ist().date().isoformat()
    receipt = await bus.submit(
        actor, "stock.receive", {"item_id": item, "qty_milli": 5000, "batch": batch}, "expired"
    )

    async def take(repo, payload):
        return {
            "moves": await issue_stock(
                repo,
                bus.clock,
                item,
                1000,
                repo.command_id,
                override_batch_id=receipt["data"]["batch_id"],
                reason="stock.owner_request",
            )
        }

    bus.policy.policies.tiers["test.take"] = "R1"
    bus.register("test.take", {"type": "object", "additionalProperties": False}, take)
    with pytest.raises(CommandError, match="unsafe"):
        await bus.submit(actor, "test.take", {}, "expiry-override")


async def test_merge_thresholds_consent_and_reward_redemption(db):
    bus, actor, _ = await fixture_shop(db)
    patrons = PatronService(bus, "synthetic-patron-proof-key")
    ids = []
    for n, name, vpa in [
        (0, "Same", "shared@bank"),
        (1, "Same", "other@bank"),
        (2, "Different", "shared@bank"),
        (3, "zzzzz", "last@bank"),
    ]:
        ids.append(
            (
                await patrons.submit(
                    actor,
                    "patrons.add",
                    {"display_name": name, "lang": "hi", "identities": [{"kind": "vpa", "value": vpa}]},
                    "p" + str(n),
                )
            )["data"]["patron_id"]
        )
    result = await bus.submit(
        actor, "patrons.propose_merge", {"source_id": ids[1], "target_id": ids[0]}, "name-only"
    )
    assert result["data"]["status"] == "needs_review" and result["data"]["confidence_bp"] == 8900
    result = await bus.submit(
        actor, "patrons.propose_merge", {"source_id": ids[3], "target_id": ids[0]}, "unrelated"
    )
    assert result["data"]["status"] == "rejected"
    await patrons.record_customer_instruction(actor.merchant_id, ids[0], "marketing", True, new_id("evt"))
    result = await bus.submit(
        actor, "patrons.propose_merge", {"source_id": ids[2], "target_id": ids[0]}, "strong"
    )
    assert result["data"]["status"] == "merged" and result["data"]["confidence_bp"] > 9000
    async with db.read() as conn:
        assert not await has_consent(Repository(conn, actor.merchant_id), ids[0], "marketing")
    bus.policy.policies.growth.monthly_incentive_budget_paise = 10000
    bus.packs._policies["kirana"].growth.monthly_incentive_budget_paise = 10000
    gate = await bus.submit(
        actor, "rewards.configure", {"threshold": 1, "value_paise": 500, "budget_paise": 500}, "rewards"
    )
    await bus.decide(actor, gate["thread_id"], "approve", "yes")
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    await bus.run_due(actor.merchant_id)
    await patrons.record_visit(actor.merchant_id, ids[0], new_id("payment"))
    bill = new_id("bill")
    payload = {"patron_id": ids[0], "bill_id": bill}
    for key in ["redeem", "replay-bill"]:
        result = await bus.submit(
            actor,
            "rewards.redeem",
            payload,
            key,
            private={"counter_verified": True, "bill_total_paise": 1000},
        )
        assert result["data"]["discount_paise"] == 500
    from arth.domains.patron_tables import offer_liability

    async with db.read() as conn:
        rows = await Repository(conn, actor.merchant_id).select(offer_liability)
        assert sum(r["issued_paise"] - r["redeemed_paise"] - r["expired_paise"] for r in rows) == 0


async def test_reminder_denial_trace_discreet_reply_customer_dispute_and_receipts(db):
    bus, actor, item, patrons, patron, account = await fixture_ledger(db)
    bus.spans = SpanBus(bus.clock)
    queue = bus.spans.subscribe()
    bus.clock.set(bus.clock.now() + timedelta(hours=2))
    entry = (await charge(bus, actor, item, account, 10000, "charge"))["data"]["entry_id"]
    with pytest.raises(CommandError, match="consent"):
        await bus.submit(
            actor,
            "ledger.send_reminder",
            {"account_id": account, "template_key": "reminder.gentle"},
            "no-consent",
        )
    traces = []
    while not queue.empty():
        traces.append(queue.get_nowait())
    assert any(s.kind == "policy" and s.attrs.get("code") == "policy.consent" for s in traces)
    await patrons.record_customer_instruction(actor.merchant_id, patron, "receipts", True, new_id("evt"))
    customer = patrons._system(actor.merchant_id)
    await bus.submit(
        customer,
        "ledger.dispute_entry",
        {"entry_id": entry},
        "customer-dispute",
        private={"customer_patron_id": patron},
    )
    await approved(bus, actor, "ledger.resolve_dispute", {"entry_id": entry}, "resolved")
    result = await approved(
        bus,
        actor,
        "ledger.record_payment",
        {"account_id": account, "amount_paise": 3000, "payment_ref": new_id("payment"), "mode": "cash"},
        "paid",
    )
    assert result["envelope"]["sensitivity"] == "discreet"
    async with db.read() as conn:
        rows = await Repository(conn, actor.merchant_id).select(
            outbox, outbox.c.type == "credit.receipt_requested"
        )
        assert len(rows) == 1
    with pytest.raises(CommandError):
        await bus.submit(
            replace(actor, role="helper"),
            "ledger.add_entry",
            {
                "account_id": account,
                "amount_paise": 1000,
                "source": "voice",
                "lines": [{"item_id": item, "qty_milli": 1000, "unit_price_paise": 1000}],
            },
            "helper",
        )
