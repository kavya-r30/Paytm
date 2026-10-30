import asyncio

from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.main import create_app


def test_startup_recovers_outbox_consumers_without_a_new_request(tmp_path):
    from arth.domains.merchants import provision_shop
    from arth.domains.tables import onboarding_progress
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    settings = Settings(_env_file=None, mode="test", data_dir=tmp_path, tick_interval_s=0.02)
    first = create_app(settings)
    with TestClient(first) as client:

        async def seed():
            shop = await provision_shop(
                first.state.commands, "Shop", "kirana", "Owner", "4826", "device", key="recovery"
            )
            await first.state.commands.submit(
                Session(shop["merchant_id"], shop["owner_id"], "owner"),
                "onboarding.complete_step",
                {"step": "language"},
                "language",
            )
            return shop

        shop = client.portal.call(seed)
    restarted = create_app(settings)
    with TestClient(restarted) as client:

        async def consume(repo, event):
            if event["type"] == "onboarding.updated":
                await repo.insert(
                    onboarding_progress, {"step": "recovery_probe", "completed_at": event["occurred_at"]}
                )

        restarted.state.events.on("recovery-probe", consume)

        async def observed():
            for _ in range(25):
                async with restarted.state.db.read() as conn:
                    rows = await Repository(conn, shop["merchant_id"]).select(
                        onboarding_progress, onboarding_progress.c.step == "recovery_probe"
                    )
                if rows:
                    return True
                await asyncio.sleep(0.02)
            return False

        assert client.portal.call(observed)
