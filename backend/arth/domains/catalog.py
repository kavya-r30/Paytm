"""Pack-schema catalog, append-only prices and deterministic modifier arithmetic."""

import csv
import json
from pathlib import Path
from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.packs import PackManifest, PackRegistry
from arth.core.schemas import schema
from arth.domains.merchants import domain_event, owner_only
from arth.domains.tables import (
    item_aliases,
    item_barcodes,
    item_prices,
    item_tax,
    items,
    modifier_groups,
    modifiers,
    recipes,
    services,
)
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository
from arth.governance.tables import merchants


def validate_pack_item(payload: dict[str, Any], pack: PackManifest) -> None:
    if payload["unit"] not in pack.catalog.units:
        raise CommandError("catalog.invalid_unit")
    details = payload.get("details", {})
    if pack.catalog.schema_ == "medicine" and not all(
        key in details for key in ("salt", "strength", "form", "pack_size", "schedule", "rx_required")
    ):
        raise CommandError("catalog.medicine_fields_required")
    if pack.catalog.schema_ == "service" and not all(
        key in details for key in ("duration_minutes", "required_skill")
    ):
        raise CommandError("catalog.service_fields_required")
    if pack.catalog.schema_ != "menu" and payload.get("modifier_groups"):
        raise CommandError("catalog.modifiers_not_supported")
    if not pack.stock.bom and payload.get("recipe"):
        raise CommandError("catalog.recipe_not_supported")


def public_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: json.loads(value) if key in {"names", "details"} else value
        for key, value in row.items()
        if key not in {"merchant_id", "search_text"}
    }


async def catalog_rows(repo: Repository) -> list[dict[str, Any]]:
    return [public_item(row) for row in await repo.select(items)]


async def get_item(repo: Repository, identity: str) -> dict[str, Any]:
    rows = await repo.select(items, items.c.id == identity)
    if not rows:
        raise CommandError("catalog.item_not_found")
    row = public_item(rows[0])
    row["aliases"] = [r["alias"] for r in await repo.select(item_aliases, item_aliases.c.item_id == identity)]
    row["barcodes"] = [
        r["barcode"] for r in await repo.select(item_barcodes, item_barcodes.c.item_id == identity)
    ]
    tax = await repo.select(item_tax, item_tax.c.item_id == identity)
    row.update({key: tax[0][key] for key in ("hsn", "gst_rate_bp")})
    groups = []
    for group in await repo.select(modifier_groups, modifier_groups.c.item_id == identity):
        options = await repo.select(modifiers, modifiers.c.group_id == group["id"])
        groups.append(
            {
                "id": group["id"],
                "name": group["name"],
                "required": bool(group["required"]),
                "options": [{k: r[k] for k in ("id", "name", "delta_paise")} for r in options],
            }
        )
    row["modifier_groups"] = groups
    row["recipe"] = [
        {"item_id": r["ingredient_id"], "qty_milli": r["qty_milli"]}
        for r in await repo.select(recipes, recipes.c.item_id == identity)
    ]
    return row


async def modifier_total(repo: Repository, identity: str, selections: dict[str, list[str]]) -> int:
    row = await get_item(repo, identity)
    groups = {group["id"]: group for group in row["modifier_groups"]}
    if set(selections) - set(groups):
        raise CommandError("catalog.invalid_modifier")
    total = row["price_paise"]
    for gid, group in groups.items():
        chosen = selections.get(gid, [])
        options = {option["id"]: option for option in group["options"]}
        if (
            (group["required"] and not chosen)
            or len(chosen) != len(set(chosen))
            or set(chosen) - set(options)
        ):
            raise CommandError("catalog.invalid_modifier")
        total += sum(options[identity]["delta_paise"] for identity in chosen)
    if total < 0:
        raise CommandError("catalog.invalid_modifier_total")
    return total


def read_starter(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            {
                "sku": r["sku"],
                "names": {"en": r["en"], "hi": r["hi"], "hi-Latn": r["hi_latn"]},
                "unit": r["unit"],
                "mrp_paise": int(r["mrp_paise"]),
                "price_paise": int(r["price_paise"]),
                "cost_paise": int(r["cost_paise"]),
                "category": r["category"],
                "aliases": r["aliases"].split("|") if r["aliases"] else [],
                "barcodes": [],
            }
            for r in csv.DictReader(handle)
        ]


def register_catalog(bus: CommandBus, packs: PackRegistry) -> None:
    async def add(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        shop = (await repo.select(merchants))[0]
        pack = packs.get(shop["pack"])
        validate_pack_item(payload, pack)
        if await repo.select(items, items.c.sku == payload["sku"]):
            raise CommandError("catalog.duplicate_sku")
        for barcode in payload.get("barcodes", []):
            if await repo.select(item_barcodes, item_barcodes.c.barcode == barcode):
                raise CommandError("catalog.duplicate_barcode")
        for ingredient in payload.get("recipe", []):
            if not await repo.select(items, items.c.id == ingredient["item_id"]):
                raise CommandError("catalog.ingredient_not_found")
        identity = new_id("item")
        search_text = " ".join(
            [*payload["names"].values(), *payload.get("aliases", []), payload["sku"]]
        ).lower()
        await repo.insert(
            items,
            {
                "id": identity,
                **{
                    key: payload[key]
                    for key in ("sku", "unit", "category", "mrp_paise", "price_paise", "cost_paise")
                },
                "names": json.dumps(payload["names"], ensure_ascii=False),
                "details": json.dumps(payload.get("details", {}), ensure_ascii=False),
                "search_text": search_text,
            },
        )
        for alias in payload.get("aliases", []):
            await repo.insert(item_aliases, {"id": new_id("alias"), "item_id": identity, "alias": alias})
        for barcode in payload.get("barcodes", []):
            await repo.insert(
                item_barcodes, {"id": new_id("barcode"), "item_id": identity, "barcode": barcode}
            )
        await repo.insert(
            item_prices,
            {
                "item_id": identity,
                "price_paise": payload["price_paise"],
                "effective_from": iso_utc(bus.clock.now()),
                "command_id": repo.command_id,
            },
        )
        await repo.insert(
            item_tax,
            {
                "item_id": identity,
                "hsn": payload.get("hsn", ""),
                "gst_rate_bp": payload.get("gst_rate_bp", 0),
            },
        )
        for group in payload.get("modifier_groups", []):
            gid = new_id("modgroup")
            await repo.insert(
                modifier_groups,
                {"id": gid, "item_id": identity, "name": group["name"], "required": int(group["required"])},
            )
            for option in group["options"]:
                await repo.insert(modifiers, {"id": new_id("modifier"), "group_id": gid, **option})
        for ingredient in payload.get("recipe", []):
            await repo.insert(
                recipes,
                {
                    "item_id": identity,
                    "ingredient_id": ingredient["item_id"],
                    "qty_milli": ingredient["qty_milli"],
                },
            )
        if pack.catalog.schema_ == "service":
            await repo.insert(
                services,
                {
                    "item_id": identity,
                    **{key: payload["details"][key] for key in ("duration_minutes", "required_skill")},
                },
            )
        await domain_event(bus, repo, "catalog.item_added", {"item_id": identity})
        return {"item_id": identity}

    async def import_items(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        return {"item_ids": [(await add(repo, entry))["item_id"] for entry in payload["items"]]}

    async def change_price(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if repo.session is None or repo.session.role not in {"owner", "manager"}:
            raise CommandError("policy.role")
        await get_item(repo, payload["item_id"])
        await repo.insert(
            item_prices,
            {
                "item_id": payload["item_id"],
                "price_paise": payload["price_paise"],
                "effective_from": iso_utc(bus.clock.now()),
                "command_id": repo.command_id,
            },
        )
        await repo.update(items, {"price_paise": payload["price_paise"]}, items.c.id == payload["item_id"])
        await domain_event(bus, repo, "catalog.price_changed", payload)
        return payload

    async def bulk(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if len({row["item_id"] for row in payload["prices"]}) != len(payload["prices"]):
            raise CommandError("catalog.duplicate_item")
        return {"prices": [await change_price(repo, row) for row in payload["prices"]]}

    for kind, handler in [
        ("catalog.add_item", add),
        ("catalog.import_items", import_items),
        ("catalog.change_price", change_price),
        ("catalog.bulk_price", bulk),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler)
