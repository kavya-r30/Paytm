"""Storefront, feedback, privacy (export, erase, sharing), device telemetry (STO-1, FBK-1, TRU-5, HLT-1)."""

import json
from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.packs import PackRegistry
from arth.core.schemas import schema
from arth.domains.catalog import catalog_rows
from arth.domains.commerce_tables import (
    bills,
    data_requests,
    data_sharing,
    device_health,
    offer_programs,
    orders,
    ratings,
    storefront_settings,
)
from arth.domains.ledger_projection import statement
from arth.domains.ledger_tables import credit_accounts
from arth.domains.merchants import domain_event, owner_only, settings_view
from arth.domains.patron_identity import patron_row, related_ids
from arth.domains.patron_tables import consents, household_members, patron_identities, patrons
from arth.domains.stock import stock_tracked, stock_view
from arth.domains.tables import devices
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository

LOW_RATING = 2
ERASED = "erased"


async def public_storefront(repo: Repository, clock: Any, packs: PackRegistry) -> dict[str, Any]:
    """STO-1: live catalog (pack-filtered, nothing personal); price = catalog price."""
    rows = await repo.select(storefront_settings)
    if not rows or not rows[0]["published"]:
        raise CommandError("storefront.not_published")
    settings = await settings_view(repo)
    flags = set(packs.policies_for(settings["pack"]).forbid_offers_on_flags)
    stock = {r["item_id"]: r for r in (await stock_view(repo, clock))["items"]}
    items = []
    for item in await catalog_rows(repo):
        if item["category"] == "ingredient" or any(
            item["details"].get(flag) for flag in flags | {"rx_required"}
        ):
            continue  # pharmacy shows OTC only; ingredients are not for sale
        tracked = await stock_tracked(repo, item["id"])
        in_stock = (
            "duration_minutes" in item["details"]
            or not tracked
            or stock[item["id"]]["sellable_qty_milli"] > 0
        )
        items.append(
            {
                "item_id": item["id"],
                "names": item["names"],
                "unit": item["unit"],
                "price_paise": item["price_paise"],
                "in_stock": bool(in_stock),
                "category": item["category"],
            }
        )
    offers = []
    if rows[0]["show_offers"]:
        now = iso_utc(clock.now())
        for program in await repo.select(offer_programs, offer_programs.c.status == "active"):
            if (
                program["valid_from"] <= now < program["valid_until"]
                and program["type"] == "first_time_coupon"
            ):
                offers.append(
                    {
                        "program_id": program["id"],
                        "type": program["type"],
                        "terms": json.loads(program["terms"]),
                    }
                )
    return {
        "name": settings["name"],
        "slug": rows[0]["slug"],
        "hours": settings["hours"],
        "items": items,
        "offers": offers,
    }


async def storefront_view(repo: Repository) -> dict[str, Any]:
    rows = await repo.select(storefront_settings)
    row = rows[0] if rows else None
    return {
        "slug": row["slug"] if row else None,
        "published": bool(row and row["published"]),
        "show_offers": bool(row and row["show_offers"]),
        "items": len(await catalog_rows(repo)),
        "url": "/s/" + row["slug"] if row and row["published"] else None,
        "invalidate_on": ["storefront.published", "catalog.item_added", "catalog.price_changed"],
    }


async def feedback_view(repo: Repository) -> dict[str, Any]:
    rows = sorted(await repo.select(ratings), key=lambda r: r["occurred_at"], reverse=True)
    keys = ("id", "target_kind", "target_id", "rating", "complaint_key", "occurred_at")
    return {
        "average_bp": sum(r["rating"] for r in rows) * 100 // len(rows) if rows else None,
        "count": len(rows),
        "ratings": [{k: r[k] for k in keys} for r in rows],
        "complaints": len([r for r in rows if r["complaint_key"] or r["rating"] <= LOW_RATING]),
        "invalidate_on": ["feedback.recorded"],
    }


async def patron_export(repo: Repository, clock: Any, patron_id: str) -> dict[str, Any]:
    """TRU-5: everything the shop holds about one customer (owner-only read)."""
    row = await patron_row(repo, patron_id)
    ids = await related_ids(repo, patron_id)
    accounts = await repo.select(credit_accounts, credit_accounts.c.patron_id.in_(ids))
    return {
        "patron": {k: row[k] for k in ("id", "display_name", "lang", "created_at")},
        "identities": [
            {"kind": r["kind"], "value": r["value"]}
            for r in await repo.select(patron_identities, patron_identities.c.patron_id.in_(ids))
        ],
        "consents": [
            {"purpose": r["purpose"], "granted": bool(r["granted"]), "occurred_at": r["occurred_at"]}
            for r in sorted(
                await repo.select(consents, consents.c.patron_id.in_(ids)), key=lambda r: r["seq"]
            )
        ],
        "khata": await statement(repo, accounts[0]["id"], clock) if accounts else None,
        "bills": [
            {"id": r["id"], "total_paise": r["total_paise"] or 0, "closed_at": r["closed_at"]}
            for r in await repo.select(bills, bills.c.patron_id.in_(ids))
        ],
    }


async def latest_health(repo: Repository) -> dict[str, Any] | None:
    rows = await repo.select(device_health)
    if not rows:
        return None
    row = max(rows, key=lambda r: r["seq"])
    return {
        k: (bool(row[k]) if k in {"connected", "mic_muted"} else row[k])
        for k in (
            "device_id",
            "connected",
            "battery_pct",
            "mic_muted",
            "volume_pct",
            "queue_size",
            "last_sync_at",
            "occurred_at",
        )
    }


def register_trust(bus: CommandBus, packs: PackRegistry) -> None:
    clock = bus.clock

    async def publish(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        owner = await Repository.storefront_slug_owner(repo.conn, payload["slug"])
        if owner and owner != repo.merchant_id:
            raise CommandError("storefront.slug_taken")
        values = {
            "slug": payload["slug"],
            "published": int(payload["published"]),
            "show_offers": int(payload["show_offers"]),
            "updated_at": iso_utc(clock.now()),
        }
        if await repo.select(storefront_settings):
            await repo.update(storefront_settings, values)
        else:
            await repo.insert(storefront_settings, values)
        await domain_event(
            bus, repo, "storefront.published", {"slug": payload["slug"], "published": payload["published"]}
        )
        return payload

    async def feedback(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        table = orders if payload["target_kind"] == "order" else bills
        rows = await repo.select(table, table.c.id == payload["target_id"])
        if not rows:
            raise CommandError("feedback.target_not_found")
        if payload["target_kind"] == "order" and rows[0]["status"] not in {
            "delivered",
            "settled",
            "on_credit",
        }:
            raise CommandError("feedback.not_delivered")
        if await repo.select(
            ratings,
            ratings.c.target_kind == payload["target_kind"],
            ratings.c.target_id == payload["target_id"],
        ):
            raise CommandError("feedback.already_rated")
        identity = new_id("rating")
        await repo.insert(
            ratings,
            {
                "id": identity,
                "target_kind": payload["target_kind"],
                "target_id": payload["target_id"],
                "rating": payload["rating"],
                "patron_id": rows[0]["patron_id"],
                "complaint_key": payload.get("complaint_key"),
                "occurred_at": iso_utc(clock.now()),
            },
        )
        low = payload["rating"] <= LOW_RATING or bool(payload.get("complaint_key"))
        await domain_event(
            bus, repo, "feedback.recorded", {"rating_id": identity, "rating": payload["rating"], "low": low}
        )
        return {"rating_id": identity, "low": low}

    async def request(repo: Repository, kind: str, patron_id: str) -> None:
        assert repo.command_id is not None
        await repo.insert(
            data_requests,
            {
                "id": new_id("datareq"),
                "kind": kind,
                "patron_id": patron_id,
                "command_id": repo.command_id,
                "occurred_at": iso_utc(clock.now()),
            },
        )

    async def export(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        await patron_row(repo, payload["patron_id"])
        await request(repo, "export", payload["patron_id"])
        await domain_event(bus, repo, "privacy.exported", payload)
        return {
            "patron_id": payload["patron_id"],
            "read": "/v1/privacy/patrons/" + payload["patron_id"] + "/export",
        }

    async def erase(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        """R4: scrub identifying fields; ledger rows keep their totals under the opaque patron ID."""
        owner_only(repo)
        ids = await related_ids(repo, payload["patron_id"])
        for identity in ids:
            await repo.update(patrons, {"display_name": ERASED, "erased": 1}, patrons.c.id == identity)
            for row in await repo.select(patron_identities, patron_identities.c.patron_id == identity):
                await repo.update(
                    patron_identities,
                    {"value": ERASED + ":" + row["id"]},
                    patron_identities.c.id == row["id"],
                )
            await repo.update(
                household_members,
                {"display_name": ERASED, "active": 0},
                household_members.c.patron_id == identity,
            )
        await request(repo, "erase", payload["patron_id"])
        await domain_event(bus, repo, "privacy.erased", {"patron_id": payload["patron_id"]})
        return {"patron_id": payload["patron_id"], "erased": len(ids)}

    async def sharing(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        values = {"peer_benchmarks": int(payload["peer_benchmarks"]), "updated_at": iso_utc(clock.now())}
        if await repo.select(data_sharing):
            await repo.update(data_sharing, values)
        else:
            await repo.insert(data_sharing, values)
        await domain_event(bus, repo, "privacy.sharing_changed", payload)
        return payload

    async def health(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if not await repo.select(devices, devices.c.id == payload["device_id"]):
            raise CommandError("device.not_found")
        await repo.insert(
            device_health,
            {
                "id": new_id("health"),
                **{k: payload[k] for k in ("device_id", "queue_size", "battery_pct", "volume_pct")},
                "connected": int(payload["connected"]),
                "mic_muted": int(payload["mic_muted"]),
                "last_sync_at": payload.get("last_sync_at"),
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await domain_event(
            bus,
            repo,
            "device.health_reported",
            {"device_id": payload["device_id"], "connected": payload["connected"]},
        )
        return {"device_id": payload["device_id"]}

    for kind, handler in [
        ("storefront.publish", publish),
        ("feedback.record", feedback),
        ("privacy.export_patron", export),
        ("privacy.erase_patron", erase),
        ("privacy.set_data_sharing", sharing),
        ("device.report_health", health),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler)


__all__ = ["register_trust", "public_storefront", "patron_export"]
