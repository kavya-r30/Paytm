"""Physical stock is a sum of moves; sellable stock additionally enforces batch safety."""

from datetime import date
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.core.packs import PackRegistry
from arth.core.schemas import schema
from arth.domains.catalog import get_item
from arth.domains.merchants import domain_event, owner_only
from arth.domains.stock_tables import batches, stock_counts, stock_moves, unmet_demand
from arth.domains.tables import items
from arth.governance.commands import CommandBus, CommandError
from arth.governance.events import emit_event
from arth.governance.repository import Repository
from arth.governance.tables import merchants


async def on_hand(
    repo: Repository, item_id: str, batch_id: str | None = None, *, all_batches: bool = True
) -> int:
    where = [stock_moves.c.item_id == item_id]
    if not all_batches or batch_id is not None:
        where.append(stock_moves.c.batch_id == batch_id)
    return sum(row["delta_qty_milli"] for row in await repo.select(stock_moves, *where))


async def stock_tracked(repo: Repository, item_id: str) -> bool:
    """An item is stock-tracked once it has any move or batch; untracked items are sold without issue."""
    return bool(
        await repo.select(stock_moves, stock_moves.c.item_id == item_id)
        or await repo.select(batches, batches.c.item_id == item_id)
    )


async def _move(
    repo: Repository,
    clock: SimClock,
    item_id: str,
    batch_id: str | None,
    delta: int,
    reason: str,
    ref_id: str,
    buyer_id: str | None = None,
) -> None:
    if repo.session is None or repo.command_id is None:
        raise CommandError("stock.bus_transaction_required")
    await repo.insert(
        stock_moves,
        {
            "id": new_id("move"),
            "item_id": item_id,
            "batch_id": batch_id,
            "delta_qty_milli": delta,
            "reason": reason,
            "ref_id": ref_id,
            "buyer_id": buyer_id,
            "occurred_at": iso_utc(clock.now()),
        },
    )


async def issue_stock(
    repo: Repository,
    clock: SimClock,
    item_id: str,
    qty_milli: int,
    ref_id: str,
    buyer_id: str | None = None,
    override_batch_id: str | None = None,
    reason: str | None = None,
) -> list[dict[str, Any]]:
    if type(qty_milli) is not int or qty_milli <= 0:
        raise CommandError("stock.invalid_quantity")
    await get_item(repo, item_id)
    rows = await repo.select(batches, batches.c.item_id == item_id)
    today = clock.now_ist().date().isoformat()
    eligible = [
        row
        for row in rows
        if not row["recalled"] and (row["expires_on"] is None or row["expires_on"] > today)
    ]
    eligible.sort(key=lambda row: (row["expires_on"] or "9999-12-31", row["received_at"], row["id"]))
    if override_batch_id:
        owner_only(repo)
        selected = next((row for row in eligible if row["id"] == override_batch_id), None)
        if selected is None or not reason:
            raise CommandError("stock.unsafe_override")
        eligible = [selected]
    slots = [(row["id"], await on_hand(repo, item_id, row["id"])) for row in eligible]
    if not override_batch_id:
        slots.append((None, await on_hand(repo, item_id, None, all_batches=False)))
    if sum(max(qty, 0) for _, qty in slots) < qty_milli:
        raise CommandError("stock.insufficient_sellable")
    assert repo.session is not None and repo.command_id is not None
    result = []
    remaining = qty_milli
    for batch_id, available in slots:
        take = min(max(available, 0), remaining)
        if not take:
            continue
        await _move(repo, clock, item_id, batch_id, -take, "stock.issue", ref_id, buyer_id)
        result.append({"batch_id": batch_id, "qty_milli": take})
        remaining -= take
        if not remaining:
            break
    if override_batch_id:
        await emit_event(
            repo,
            clock,
            repo.session,
            "stock.override_recorded",
            repo.command_id,
            {"item_id": item_id, "batch_id": override_batch_id, "reason": reason},
        )
    await emit_event(repo, clock, repo.session, "stock.changed", repo.command_id, {"item_id": item_id})
    return result


async def receive_stock(
    repo: Repository,
    clock: SimClock,
    pack: Any,
    item_id: str,
    qty_milli: int,
    batch: dict[str, Any] | None,
) -> dict[str, Any]:
    """Transaction-local receipt (stock.receive and Supply GRN); the pack decides batch/expiry rules."""
    if pack.stock.batches == "required" and not batch:
        raise CommandError("stock.batch_required")
    if batch and pack.stock.batches == "off":
        raise CommandError("stock.batches_disabled")
    if pack.stock.expiry == "required" and (not batch or not batch.get("expires_on")):
        raise CommandError("stock.expiry_required")
    batch_id = None
    if batch:
        existing = await repo.select(
            batches, batches.c.item_id == item_id, batches.c.batch_no == batch["batch_no"]
        )
        if existing:
            row = existing[0]
            if row["recalled"] or any(
                row[key] != batch.get(key) for key in ("expires_on", "mrp_paise", "cost_paise")
            ):
                raise CommandError("stock.batch_conflict")
            batch_id = row["id"]
        else:
            batch_id = new_id("batch")
            await repo.insert(
                batches, {"id": batch_id, "item_id": item_id, "received_at": iso_utc(clock.now()), **batch}
            )
    assert repo.session is not None and repo.command_id is not None
    await _move(repo, clock, item_id, batch_id, qty_milli, "stock.receipt", repo.command_id)
    await emit_event(repo, clock, repo.session, "stock.changed", repo.command_id, {"item_id": item_id})
    return {"batch_id": batch_id, "qty_milli": qty_milli}


async def stock_view(repo: Repository, clock: SimClock) -> dict[str, Any]:
    today = clock.now_ist().date().isoformat()
    result = []
    for item in await repo.select(items):
        batch_rows = []
        sellable = await on_hand(repo, item["id"], None, all_batches=False)
        for row in await repo.select(batches, batches.c.item_id == item["id"]):
            quantity = await on_hand(repo, item["id"], row["id"])
            safe = not row["recalled"] and (row["expires_on"] is None or row["expires_on"] > today)
            sellable += quantity if safe else 0
            batch_rows.append(
                {key: row[key] for key in ("id", "batch_no", "expires_on", "mrp_paise", "cost_paise")}
                | {"recalled": bool(row["recalled"]), "qty_milli": quantity}
            )
        result.append(
            {
                "item_id": item["id"],
                "on_hand_qty_milli": await on_hand(repo, item["id"]),
                "sellable_qty_milli": sellable,
                "batches": batch_rows,
            }
        )
    return {"items": result, "invalidate_on": ["stock.changed", "batch.recalled"]}


async def expiry_view(repo: Repository, clock: SimClock, within_days: int) -> dict[str, Any]:
    today = clock.now_ist().date()
    result = []
    for row in await repo.select(batches):
        days = (date.fromisoformat(row["expires_on"]) - today).days if row["expires_on"] else None
        if row["recalled"] or (days is not None and days <= within_days):
            result.append(
                {
                    "batch_id": row["id"],
                    "item_id": row["item_id"],
                    "days_to_expiry": days,
                    "recalled": bool(row["recalled"]),
                    "qty_milli": await on_hand(repo, row["item_id"], row["id"]),
                }
            )
    return {"batches": result, "invalidate_on": ["stock.changed", "batch.recalled", "clock.day"]}


def register_stock(bus: CommandBus, packs: PackRegistry) -> None:
    async def checked(repo: Repository, payload: dict[str, Any]) -> tuple[dict[str, Any], Any]:
        item = await get_item(repo, payload["item_id"])
        shop = (await repo.select(merchants))[0]
        pack = packs.get(shop["pack"])
        if "duration_minutes" in item["details"]:
            raise CommandError("stock.service_not_stocked")
        return item, pack

    async def receive(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        _, pack = await checked(repo, payload)
        return await receive_stock(
            repo, bus.clock, pack, payload["item_id"], payload["qty_milli"], payload.get("batch")
        )

    async def correction(repo: Repository, payload: dict[str, Any], count: bool) -> dict[str, Any]:
        _, pack = await checked(repo, payload)
        batch_id = payload.get("batch_id")
        existing = await repo.select(batches, batches.c.item_id == payload["item_id"])
        if batch_id is not None and not any(row["id"] == batch_id for row in existing):
            raise CommandError("stock.batch_not_found")
        if batch_id is None and (pack.stock.batches == "required" or existing):
            raise CommandError("stock.batch_required")
        previous = await on_hand(repo, payload["item_id"], batch_id, all_batches=False)
        delta = payload["counted_qty_milli"] - previous if count else payload["delta_qty_milli"]
        if previous + delta < 0:
            raise CommandError("stock.insufficient_quantity")
        assert repo.command_id is not None
        if count:
            await repo.insert(
                stock_counts,
                {
                    "id": new_id("count"),
                    "item_id": payload["item_id"],
                    "batch_id": batch_id,
                    "counted_qty_milli": payload["counted_qty_milli"],
                    "previous_qty_milli": previous,
                    "command_id": repo.command_id,
                    "occurred_at": iso_utc(bus.clock.now()),
                },
            )
        await _move(
            repo,
            bus.clock,
            payload["item_id"],
            batch_id,
            delta,
            "stock.count" if count else payload["reason"],
            repo.command_id,
        )
        await domain_event(bus, repo, "stock.changed", {"item_id": payload["item_id"]})
        return {"delta_qty_milli": delta, "on_hand_qty_milli": previous + delta}

    async def count(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return await correction(repo, payload, True)

    async def adjust(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        return await correction(repo, payload, False)

    async def recall(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        rows = await repo.select(batches, batches.c.id == payload["batch_id"])
        if not rows:
            raise CommandError("stock.batch_not_found")
        await repo.update(batches, {"recalled": 1}, batches.c.id == payload["batch_id"])
        buyers = sorted(
            {
                row["buyer_id"]
                for row in await repo.select(stock_moves, stock_moves.c.batch_id == payload["batch_id"])
                if row["buyer_id"]
            }
        )
        await domain_event(
            bus, repo, "batch.recalled", {"batch_id": payload["batch_id"], "buyer_ids": buyers}
        )
        return {"batch_id": payload["batch_id"], "buyer_ids": buyers}

    async def demand(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("item_id"):
            await get_item(repo, payload["item_id"])
        identity = new_id("demand")
        await repo.insert(
            unmet_demand,
            {
                "id": identity,
                "text": payload["text"],
                "item_id": payload.get("item_id"),
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(bus, repo, "stock.demand_logged", {"demand_id": identity})
        return {"demand_id": identity}

    for kind, handler in [
        ("stock.receive", receive),
        ("stock.count", count),
        ("stock.adjust", adjust),
        ("stock.recall_batch", recall),
        ("stock.log_unmet_demand", demand),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler)
