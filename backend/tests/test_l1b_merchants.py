import json

import pytest
from l1b_helpers import make_bus


async def test_independent_languages_owner_permissions_and_tenancy(db):
    from arth.domains.merchants import provision_shop, settings_view
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    bus = make_bus(db)
    shop = await provision_shop(bus, "A", "kirana", "Owner", "4826", "device-a", key="setup-a")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
    result = await bus.submit(
        owner,
        "merchant.update_settings",
        {"screen_lang": "ta", "speech_lang": "hi-IN", "customer_lang": "en"},
        "languages",
    )
    assert result["envelope"]["lang"] == {"screen": "ta", "speech": "hi-IN"}
    async with db.read() as conn:
        settings = await settings_view(Repository(conn, owner.merchant_id))
        assert settings["customer_lang"] == "en"
        assert settings["marketing_consent_default"] is False
        with pytest.raises(CommandError):
            await settings_view(Repository(conn, "other"))
    with pytest.raises(CommandError):
        await bus.submit(
            Session(owner.merchant_id, "helper", "helper"),
            "merchant.update_settings",
            {"screen_lang": "en"},
            "bad",
        )
    with pytest.raises(CommandError):
        await bus.submit(owner, "merchant.update_settings", {"merchant_id": "other"}, "tenant")


async def test_ordered_onboarding_and_bootstrap_no_secret_persistence(db):
    from arth.domains.merchants import onboarding_view, provision_shop
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log, commands, outbox

    bus = make_bus(db)
    shop = await provision_shop(bus, "A", "kirana", "Owner", "4826", "device-a", key="same")
    replay = await provision_shop(bus, "A", "kirana", "Owner", "4826", "device-a", key="same")
    assert replay == shop
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner")
    with pytest.raises(CommandError, match="step_order"):
        await bus.submit(owner, "onboarding.complete_step", {"step": "details"}, "wrong")
    await bus.submit(owner, "onboarding.complete_step", {"step": "language"}, "first")
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        assert (await onboarding_view(repo))["completed"] == ["language"]
        dumped = json.dumps([await repo.select(t) for t in (commands, audit_log, outbox)])
        assert '"4826"' not in dumped and "scrypt$" not in dumped
        from arth.core.schemas import validator

        for row in await repo.select(outbox):
            event = json.loads(row["payload"])
            validator(event["type"].replace(".", "_")).validate(event)


async def test_details_step_requires_shop_payment_and_address_details(db):
    from arth.domains.merchants import provision_shop
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = make_bus(db)
    shop = await provision_shop(bus, "Shop", "kirana", "Owner", "4826", "device-a", key="details")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner")
    await bus.submit(owner, "onboarding.complete_step", {"step": "language"}, "language")
    await bus.submit(owner, "onboarding.complete_step", {"step": "pack"}, "pack")
    with pytest.raises(CommandError, match="details_required"):
        await bus.submit(owner, "onboarding.complete_step", {"step": "details"}, "complete-details")
