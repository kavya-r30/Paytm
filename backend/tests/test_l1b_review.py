from datetime import timedelta

import pytest
from test_l1b_staff import setup_staff


def test_private_signing_key_persists_and_rejects_corruption(tmp_path):
    from arth.domains.security import load_signing_key

    path = tmp_path / "session-signing.key"
    first = load_signing_key(path)
    assert len(first.get_secret_value()) == 64
    assert load_signing_key(path).get_secret_value() == first.get_secret_value()
    assert first.get_secret_value() not in repr(first)
    path.write_text("invalid", encoding="utf-8")
    with pytest.raises(ValueError):
        load_signing_key(path)


async def test_wrong_pin_reusing_success_key_still_locks_out(db):
    from arth.governance.commands import CommandError

    bus, service, shop, owner, device = await setup_staff(db)
    await service.login(device, owner.actor_id, "4826", "device", "known-success")
    for _ in range(5):
        with pytest.raises(CommandError):
            await service.login(device, owner.actor_id, "1111", "device", "known-success")
    with pytest.raises(CommandError, match="locked"):
        await service.login(device, owner.actor_id, "4826", "device", "correct-new-key")


async def test_merchant_quiet_hours_apply_and_cannot_loosen_guardrails(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import PolicyContext

    bus, service, shop, owner, device = await setup_staff(db)
    await bus.submit(
        owner, "merchant.update_settings", {"quiet_hours": {"start": "20:00", "end": "09:00"}}, "quiet"
    )
    bus.clock.set(bus.clock.now() + timedelta(hours=12, minutes=30))

    async def handler(repo, payload):
        return {"draft": True}

    async def context(repo, payload):
        return PolicyContext(purpose="marketing", consent=True)

    bus.register(
        "outreach.send_campaign", {"type": "object", "additionalProperties": False}, handler, context
    )
    with pytest.raises(CommandError, match="quiet_hours"):
        await bus.submit(owner, "outreach.send_campaign", {}, "send")
    with pytest.raises(CommandError, match="quiet_hours"):
        await bus.submit(
            owner, "merchant.update_settings", {"quiet_hours": {"start": "22:00", "end": "07:00"}}, "loosen"
        )


async def test_queued_approval_rechecks_revoked_session(db):
    from arth.domains.tables import staff_sessions
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, service, shop, owner, device = await setup_staff(db)
    token = (await service.login(device, owner.actor_id, "4826", "console", "owner-login"))["token"]
    session = await service.resolve(token)

    async def handler(repo, payload):
        return {"saved": True}

    bus.register("supply.place_po", {"type": "object", "additionalProperties": False}, handler)
    gate = await bus.submit(session, "supply.place_po", {}, "po")
    await bus.decide(session, gate["thread_id"], "approve", "approve")
    async with db.write() as conn:
        await Repository(conn, owner.merchant_id).update(staff_sessions, {"revoked": 1})
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    with pytest.raises(CommandError, match="session"):
        await bus.run_due(owner.merchant_id)


async def test_authenticated_owner_device_can_bind_a_trusted_voice_turn(db):
    from dataclasses import replace

    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, service, shop, owner, device = await setup_staff(db)
    token = (await service.login(device, owner.actor_id, "4826", "device", "owner-device"))["token"]
    signed = await service.resolve(token)
    voice = replace(signed, channel="voice", owner_ptt=True)
    async with db.read() as conn:
        await service.validate(Repository(conn, owner.merchant_id), voice)
        with pytest.raises(CommandError):
            await service.validate(Repository(conn, owner.merchant_id), replace(voice, owner_ptt=False))
