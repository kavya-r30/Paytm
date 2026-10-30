import json
from datetime import timedelta

import pytest
from l1c_helpers import fixture_shop

from arth.core.ids import new_id


async def test_identity_privacy_ambiguity_consent_stop_and_household(db):
    from arth.domains.patrons import PatronService, has_consent, resolve_identity
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log, commands, outbox

    bus, actor, _ = await fixture_shop(db)
    service = PatronService(bus, "synthetic-patron-proof-key")
    first = (
        await service.submit(
            actor,
            "patrons.add",
            {
                "display_name": "Sharma One",
                "lang": "hi",
                "identities": [
                    {"kind": "vpa", "value": "first@bank"},
                    {"kind": "spoken_name", "value": "Sharma"},
                ],
            },
            "first",
        )
    )["data"]["patron_id"]
    second = (
        await service.submit(
            actor,
            "patrons.add",
            {
                "display_name": "Sharma Two",
                "lang": "en",
                "identities": [{"kind": "spoken_name", "value": "Sharma"}],
            },
            "second",
        )
    )["data"]["patron_id"]
    assert second != first
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        assert (await resolve_identity(repo, "vpa", "FIRST@BANK"))["selected"] == first
        assert (await resolve_identity(repo, "spoken_name", "Sharma"))["selected"] is None
        assert not await has_consent(repo, first, "marketing")
        data = json.dumps([await repo.select(t) for t in (commands, audit_log, outbox)])
        assert "Sharma One" not in data and "first@bank" not in data
    with pytest.raises(CommandError, match="instruction"):
        await bus.submit(
            actor,
            "consent.grant",
            {"patron_id": first, "purpose": "marketing", "source_ref": new_id("evt")},
            "forged",
        )
    await service.record_customer_instruction(actor.merchant_id, first, "marketing", True, new_id("evt"))
    async with db.read() as conn:
        assert await has_consent(Repository(conn, actor.merchant_id), first, "marketing")
        assert not await has_consent(Repository(conn, actor.merchant_id), first, "reminders")
    await service.stop(actor.merchant_id, first, new_id("evt"))
    member = (await service.add_member(actor, first, "Family Member", "member"))["data"]["member_id"]
    assert member.startswith("member_")
    async with db.read() as conn:
        assert not await has_consent(Repository(conn, actor.merchant_id), first, "marketing")
        assert (await resolve_identity(Repository(conn, "other"), "vpa", "first@bank"))["selected"] is None


async def test_verified_visit_rewards_are_idempotent_and_liability_reconciles(db):
    from arth.domains.patron_tables import offer_liability
    from arth.domains.patrons import PatronService, reward_view
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, actor, _ = await fixture_shop(db)
    service = PatronService(bus, "synthetic-patron-proof-key")
    patron = (await service.submit(actor, "patrons.add", {"display_name": "Customer", "lang": "hi"}, "p"))[
        "data"
    ]["patron_id"]
    bus.policy.policies.growth.monthly_incentive_budget_paise = 10000
    bus.packs._policies["kirana"].growth.monthly_incentive_budget_paise = 10000
    gate = await bus.submit(
        actor, "rewards.configure", {"threshold": 2, "value_paise": 500, "budget_paise": 1000}, "program"
    )
    await bus.decide(actor, gate["thread_id"], "approve", "yes")
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    await bus.run_due(actor.merchant_id)
    first = new_id("payment")
    await service.record_visit(actor.merchant_id, patron, first)
    await service.record_visit(actor.merchant_id, patron, first)
    await service.record_visit(actor.merchant_id, patron, new_id("payment"))
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        rewards = await reward_view(repo, patron)
        assert rewards["stamps"] == 2 and rewards["available_rewards"] == 1
        rows = await repo.select(offer_liability)
        assert sum(r["issued_paise"] - r["redeemed_paise"] - r["expired_paise"] for r in rows) == 500
    with pytest.raises(CommandError, match="verified"):
        await bus.submit(
            actor,
            "rewards.record_visit",
            {"patron_id": patron, "payment_ref": new_id("payment")},
            "fake-payment",
        )
