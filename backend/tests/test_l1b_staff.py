import json
from datetime import timedelta

import pytest
from l1b_helpers import make_bus


async def setup_staff(db):
    from arth.domains.merchants import provision_shop
    from arth.domains.staff import StaffService
    from arth.governance.policy import Session

    bus = make_bus(db)
    service = StaffService(bus, "synthetic-test-signing-key")
    shop = await provision_shop(bus, "Shop", "kirana", "Owner", "4826", "device-a", key="shop")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
    credential = service.device_credential(shop["merchant_id"], shop["device_id"])
    return bus, service, shop, owner, credential


async def test_pin_session_restart_logout_and_no_credential_leak(db):
    from arth.domains.staff import StaffService
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log, commands, outbox

    bus, service, shop, owner, device = await setup_staff(db)
    result = await service.login(device, shop["owner_id"], "4826", "console", "login")
    session = await service.resolve(result["token"])
    assert session.role == "owner" and not session.owner_ptt and not session.step_up
    restarted = StaffService(bus, "synthetic-test-signing-key")
    assert (await restarted.resolve(result["token"])).actor_id == owner.actor_id
    with pytest.raises(CommandError):
        await service.login(device, shop["owner_id"], "1111", "console", "login")
    with pytest.raises(CommandError):
        await service.resolve(result["token"] + "x")
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        history = json.dumps([await repo.select(t) for t in (commands, audit_log, outbox)])
        assert '"4826"' not in history and result["token"] not in history and "scrypt$" not in history
    await bus.submit(session, "staff.logout", {}, "logout")
    with pytest.raises(CommandError, match="session"):
        await restarted.resolve(result["token"])


async def test_lockout_expiry_helper_and_shift_variance(db):
    from arth.governance.commands import CommandError

    bus, service, shop, owner, device = await setup_staff(db)
    helper = (await service.add(owner, "Helper", "helper", "6194", "new-helper"))["data"]["staff_id"]
    for n in range(5):
        with pytest.raises(CommandError):
            await service.login(device, helper, "1111", "device", f"bad{n}")
    with pytest.raises(CommandError, match="locked"):
        await service.login(device, helper, "6194", "device", "locked")
    bus.clock.set(bus.clock.now() + timedelta(minutes=5))
    token = (await service.login(device, helper, "6194", "device", "helper-login"))["token"]
    session = await service.resolve(token)
    with pytest.raises(CommandError):
        await service.add(session, "Evil owner", "owner", "4826", "escalate")
    opened = await bus.submit(session, "shift.open", {"float_paise": 200000}, "open")
    shift_id = opened["data"]["shift_id"]
    with pytest.raises(CommandError, match="shift"):
        await bus.submit(owner, "shift.close", {"shift_id": shift_id, "counted_paise": 195000}, "other-close")
    closed = await bus.submit(
        session, "shift.close", {"shift_id": shift_id, "counted_paise": 195000}, "close"
    )
    assert closed["data"]["variance_paise"] == -5000
    assert closed["data"]["staff_id"] == helper
    bus.clock.set(bus.clock.now() + timedelta(hours=12))
    with pytest.raises(CommandError, match="session"):
        await service.resolve(token)
