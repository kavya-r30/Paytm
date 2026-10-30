"""Merchant settings, trusted initial provisioning and ordered onboarding."""

import hashlib
import json
from typing import Any

from arth.core.clock import iso_utc
from arth.core.packs import PackRegistry
from arth.core.schemas import schema
from arth.domains.security import hash_pin
from arth.domains.tables import devices, onboarding_progress, staff_credentials
from arth.governance.commands import CommandBus, CommandError
from arth.governance.events import emit_event
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import merchant_settings, merchants, staff

DEFAULTS = {
    "screen_lang": "hi-Latn",
    "speech_lang": "hi-IN",
    "customer_lang": "hi",
    "tax_profile": "unregistered",
    "hours": {"start": "08:00", "end": "21:00"},
    "quiet_hours": {"start": "21:30", "end": "08:00"},
    "marketing_consent_default": False,
    "receipts_consent_default": False,
}
STEPS = ("language", "pack", "details", "catalog", "people")


def stable_id(kind: str, key: str) -> str:
    value = int.from_bytes(hashlib.sha256((kind + ":" + key).encode()).digest()[:16])
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    chars = "".join(alphabet[(value >> shift) & 31] for shift in range(125, -1, -5))
    return kind + "_" + chars


def owner_only(repo: Repository) -> None:
    if repo.session is None or repo.session.role != "owner":
        raise CommandError("policy.owner_required")


async def settings_view(repo: Repository) -> dict[str, Any]:
    shops = await repo.select(merchants)
    if not shops:
        raise CommandError("merchant.not_found")
    settings = await repo.select(merchant_settings)
    return {
        **DEFAULTS,
        **(json.loads(settings[0]["settings"]) if settings else {}),
        "name": shops[0]["name"],
        "pack": shops[0]["pack"],
    }


async def onboarding_view(repo: Repository) -> dict[str, Any]:
    await settings_view(repo)
    completed = {row["step"] for row in await repo.select(onboarding_progress)}
    return {
        "steps": list(STEPS),
        "completed": [step for step in STEPS if step in completed],
        "next_step": next((step for step in STEPS if step not in completed), None),
        "invalidate_on": ["onboarding.updated"],
    }


async def domain_event(bus: CommandBus, repo: Repository, topic: str, payload: dict[str, Any]) -> None:
    assert repo.session is not None and repo.command_id is not None
    await emit_event(repo, bus.clock, repo.session, topic, repo.command_id, payload)


def register_merchants(bus: CommandBus, packs: PackRegistry) -> None:
    async def bootstrap(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if not repo.private.get("bootstrap"):
            raise CommandError("merchant.trusted_provisioning_required")
        packs.get(payload["pack"])
        await repo.insert(
            merchants, {"id": repo.merchant_id, "name": payload["name"], "pack": payload["pack"]}
        )
        await repo.insert(merchant_settings, {"settings": json.dumps(DEFAULTS)})
        await repo.insert(staff, {"id": payload["owner_id"], "role": "owner", "name": payload["owner_name"]})
        await repo.insert(
            staff_credentials, {"staff_id": payload["owner_id"], "pin_hash": hash_pin(repo.private["pin"])}
        )
        await repo.insert(devices, {"id": payload["device_id"], "edition": "display", "capabilities": "{}"})
        result = {
            "merchant_id": repo.merchant_id,
            "owner_id": payload["owner_id"],
            "device_id": payload["device_id"],
        }
        await domain_event(bus, repo, "onboarding.started", {"device_id": payload["device_id"]})
        return result

    async def update_settings(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        old = await settings_view(repo)
        settings = {k: v for k, v in {**old, **payload}.items() if k not in {"name", "pack"}}
        if settings.get("tax_profile") == "regular" and not settings.get("gstin"):
            raise CommandError("merchant.gstin_required")
        if "quiet_hours" in payload:

            def minutes(window: dict[str, str]) -> set[int]:
                start, end = (
                    int(h) * 60 + int(m) for h, m in (window["start"].split(":"), window["end"].split(":"))
                )
                return set(range(start, end)) if start < end else set(range(start, 1440)) | set(range(0, end))

            core = bus.policy.policies.quiet_hours.model_dump()
            if not minutes(core) <= minutes(payload["quiet_hours"]):
                raise CommandError("merchant.quiet_hours_cannot_loosen")
        await repo.update(merchant_settings, {"settings": json.dumps(settings)})
        if "name" in payload:
            await repo.update(merchants, {"name": payload["name"]})
        await domain_event(
            bus,
            repo,
            "i18n.changed",
            {
                "screen_lang": settings["screen_lang"],
                "speech_lang": settings["speech_lang"],
                "customer_lang": settings["customer_lang"],
            },
        )
        return await settings_view(repo)

    async def complete(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        view = await onboarding_view(repo)
        step = payload["step"]
        if step in view["completed"]:
            return view
        if step != view["next_step"]:
            raise CommandError("onboarding.step_order")
        if step == "details":
            settings = await settings_view(repo)
            if not all(settings.get(key, "").strip() for key in ("name", "vpa", "address")):
                raise CommandError("onboarding.details_required")
        if step == "catalog":
            from arth.domains.catalog import catalog_rows

            if not await catalog_rows(repo):
                raise CommandError("onboarding.catalog_required")
        await repo.insert(onboarding_progress, {"step": step, "completed_at": iso_utc(bus.clock.now())})
        await domain_event(bus, repo, "onboarding.updated", {"step": step})
        return await onboarding_view(repo)

    bus.register("merchant.bootstrap", schema("merchant_bootstrap"), bootstrap)
    bus.register("merchant.update_settings", schema("merchant_update_settings"), update_settings)
    bus.register("onboarding.complete_step", schema("onboarding_complete_step"), complete)


async def provision_shop(
    bus: CommandBus, name: str, pack: str, owner_name: str, pin: str, device_id: str, *, key: str
) -> dict[str, Any]:
    mid, owner_id = stable_id("merchant", key), stable_id("staff", key)
    device_id = stable_id("device", device_id)
    result = await bus.submit(
        Session(mid, owner_id, "owner", channel="console"),
        "merchant.bootstrap",
        {"name": name, "pack": pack, "owner_id": owner_id, "owner_name": owner_name, "device_id": device_id},
        key,
        private={"bootstrap": True, "pin": pin},
    )
    return result["data"]
