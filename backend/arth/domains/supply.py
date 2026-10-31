"""Supply: suppliers, quotes, purchase orders, goods receipt, supplier bills with a 3-way match,
variance claims and price history (SUP-1…3, LED-7).

PO: draft → sent (R3) → confirmed → received, or cancelled. A supplier bill (R2) creates the payable
and compares PO price, billed price and received quantity line by line.
"""

from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.packs import PackRegistry
from arth.core.qty import line_amount
from arth.core.schemas import schema
from arth.domains.catalog import get_item
from arth.domains.commerce_tables import (
    claims,
    grn_lines,
    grn_variances,
    grns,
    po_lines,
    price_history,
    purchase_orders,
    quotes,
    supplier_bill_lines,
    supplier_bills,
    suppliers,
)
from arth.domains.ledger_tables import payable_allocations, payables
from arth.domains.merchants import domain_event, owner_only
from arth.domains.stock import receive_stock
from arth.domains.summaries import item_name, supplier_name
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository
from arth.governance.tables import merchants

PO_FLOW = {
    "draft": {"sent", "cancelled"},
    "sent": {"confirmed", "received", "cancelled"},
    "confirmed": {"received", "cancelled"},
}


async def po_row(repo: Repository, po_id: str) -> dict[str, Any]:
    rows = await repo.select(purchase_orders, purchase_orders.c.id == po_id)
    if not rows:
        raise CommandError("supply.po_not_found")
    return rows[0]


async def suppliers_view(repo: Repository) -> dict[str, Any]:
    result = []
    for row in await repo.select(suppliers):
        pos = await repo.select(purchase_orders, purchase_orders.c.supplier_id == row["id"])
        owed = 0
        for payable in await repo.select(payables, payables.c.supplier_ref == row["id"]):
            paid = await repo.select(payable_allocations, payable_allocations.c.payable_id == payable["id"])
            owed += payable["amount_paise"] - sum(r["amount_paise"] for r in paid)
        result.append(
            {k: row[k] for k in ("id", "name", "lang", "lead_days")}
            | {
                "open_pos": len([p for p in pos if p["status"] in {"draft", "sent", "confirmed"}]),
                "payable_paise": owed,
            }
        )
    return {
        "suppliers": result,
        "invalidate_on": ["po.changed", "po.supplier_added", "credit.payable_changed"],
    }


async def po_view(repo: Repository, po_id: str) -> dict[str, Any]:
    po = await po_row(repo, po_id)
    history = sorted(
        await repo.select(price_history, price_history.c.supplier_id == po["supplier_id"]),
        key=lambda r: r["seq"],
    )
    lines = []
    for line in await repo.select(po_lines, po_lines.c.po_id == po_id):
        item = await get_item(repo, line["item_id"])
        earlier = [h for h in history if h["item_id"] == line["item_id"] and h["ref_id"] != po_id]
        lines.append(
            {k: line[k] for k in ("item_id", "qty_milli", "unit_price_paise", "amount_paise")}
            | {
                "name": item["names"].get("en") or next(iter(item["names"].values())),
                "last_price_paise": earlier[-1]["unit_price_paise"] if earlier else None,
            }
        )
    items = {line["item_id"] for line in lines}
    return {
        "po": {k: po[k] for k in ("id", "supplier_id", "status", "total_paise", "due_on", "created_at")}
        | {"lines": lines, "supplier_name": await supplier_name(repo, po["supplier_id"])},
        "price_history": [
            {k: h[k] for k in ("item_id", "unit_price_paise", "source", "occurred_at")}
            for h in history
            if h["item_id"] in items
        ],
        "invalidate_on": ["po.changed"],
    }


async def _variances(repo: Repository, po_id: str) -> list[dict[str, Any]]:
    rows = sorted(await repo.select(grn_variances, grn_variances.c.po_id == po_id), key=lambda r: r["seq"])
    return [
        {k: r[k] for k in ("item_id", "kind", "expected", "actual", "delta_paise")}
        | {"name": await item_name(repo, r["item_id"])}
        for r in rows
    ]


async def grn_view(repo: Repository, po_id: str) -> dict[str, Any]:
    await po_row(repo, po_id)
    received = []
    for grn in await repo.select(grns, grns.c.po_id == po_id):
        received = [
            {k: r[k] for k in ("item_id", "qty_milli", "batch_id")}
            for r in await repo.select(grn_lines, grn_lines.c.grn_id == grn["id"])
        ]
    billed = []
    for bill in await repo.select(supplier_bills, supplier_bills.c.po_id == po_id):
        billed = [
            {k: r[k] for k in ("item_id", "qty_milli", "unit_price_paise")}
            for r in await repo.select(supplier_bill_lines, supplier_bill_lines.c.bill_id == bill["id"])
        ]
    claim = await repo.select(claims, claims.c.po_id == po_id)
    return {
        "po_id": po_id,
        "supplier_name": await supplier_name(repo, (await po_row(repo, po_id))["supplier_id"]),
        "received": received,
        "billed": billed,
        "variances": await _variances(repo, po_id),
        "claim_id": claim[0]["id"] if claim else None,
        "invalidate_on": ["po.changed"],
    }


async def claim_view(repo: Repository, claim_id: str) -> dict[str, Any]:
    rows = await repo.select(claims, claims.c.id == claim_id)
    if not rows:
        raise CommandError("supply.claim_not_found")
    claim = rows[0]
    return {
        "claim": {
            k: claim[k]
            for k in ("id", "po_id", "supplier_id", "amount_paise", "status", "lang", "created_at")
        },
        "variances": await _variances(repo, claim["po_id"]),
        "supplier_name": await supplier_name(repo, claim["supplier_id"]),
        "invalidate_on": ["po.changed"],
    }


def register_supply(bus: CommandBus, packs: PackRegistry) -> None:
    clock = bus.clock

    async def history(
        repo: Repository, supplier_id: str, item_id: str, price: int, source: str, ref: str
    ) -> None:
        await repo.insert(
            price_history,
            {
                "id": new_id("price"),
                "supplier_id": supplier_id,
                "item_id": item_id,
                "unit_price_paise": price,
                "source": source,
                "ref_id": ref,
                "occurred_at": iso_utc(clock.now()),
            },
        )

    async def supplier(repo: Repository, supplier_id: str) -> dict[str, Any]:
        rows = await repo.select(suppliers, suppliers.c.id == supplier_id)
        if not rows:
            raise CommandError("supply.supplier_not_found")
        return rows[0]

    async def move(repo: Repository, po: dict[str, Any], to: str) -> None:
        if to not in PO_FLOW.get(po["status"], set()):
            raise CommandError("supply.illegal_transition")
        await repo.update(
            purchase_orders,
            {"status": to, "updated_at": iso_utc(clock.now())},
            purchase_orders.c.id == po["id"],
        )
        await domain_event(bus, repo, "po.changed", {"po_id": po["id"], "status": to})

    async def add_supplier(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        identity = new_id("supplier")
        await repo.insert(
            suppliers,
            {
                "id": identity,
                "name": payload["name"],
                "phone": payload.get("phone"),
                "lang": payload["lang"],
                "lead_days": payload["lead_days"],
                "created_at": iso_utc(clock.now()),
            },
        )
        await domain_event(bus, repo, "po.supplier_added", {"supplier_id": identity})
        return {"supplier_id": identity}

    async def record_quote(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await supplier(repo, payload["supplier_id"])
        await get_item(repo, payload["item_id"])
        identity = new_id("quote")
        await repo.insert(
            quotes,
            {
                "id": identity,
                **payload,
                "valid_until": payload.get("valid_until"),
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await history(
            repo, payload["supplier_id"], payload["item_id"], payload["unit_price_paise"], "quote", identity
        )
        await domain_event(bus, repo, "po.changed", {"po_id": identity, "status": "quoted"})
        return {"quote_id": identity}

    async def draft_po(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        await supplier(repo, payload["supplier_id"])
        if len({line["item_id"] for line in payload["lines"]}) != len(payload["lines"]):
            raise CommandError("supply.duplicate_item")
        identity, now = new_id("po"), iso_utc(clock.now())
        total = 0
        for line in payload["lines"]:
            await get_item(repo, line["item_id"])
            amount = line_amount(line["unit_price_paise"], line["qty_milli"])
            total += amount
            await repo.insert(
                po_lines, {"id": new_id("poline"), "po_id": identity, **line, "amount_paise": amount}
            )
            await history(
                repo, payload["supplier_id"], line["item_id"], line["unit_price_paise"], "po", identity
            )
        await repo.insert(
            purchase_orders,
            {
                "id": identity,
                "supplier_id": payload["supplier_id"],
                "status": "draft",
                "total_paise": total,
                "due_on": payload.get("due_on"),
                "created_at": now,
                "updated_at": now,
            },
        )
        await domain_event(bus, repo, "po.changed", {"po_id": identity, "status": "draft"})
        return {"po_id": identity, "total_paise": total}

    async def place(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        po = await po_row(repo, payload["po_id"])
        await move(repo, po, "sent")
        return {"po_id": po["id"], "status": "sent", "supplier_id": po["supplier_id"]}

    async def confirm(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        assert repo.session is not None
        if repo.session.role == "system" and not repo.private.get("supplier_verified"):
            raise CommandError("supply.verified_supplier_required")
        po = await po_row(repo, payload["po_id"])
        await move(repo, po, "confirmed")
        return {"po_id": po["id"], "status": "confirmed"}

    async def cancel(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        await move(repo, await po_row(repo, payload["po_id"]), "cancelled")
        return {"po_id": payload["po_id"], "status": "cancelled"}

    async def receive(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        po = await po_row(repo, payload["po_id"])
        if po["status"] not in {"sent", "confirmed"}:
            raise CommandError("supply.illegal_transition")
        ordered = {r["item_id"] for r in await repo.select(po_lines, po_lines.c.po_id == po["id"])}
        pack = packs.get((await repo.select(merchants))[0]["pack"])
        identity = new_id("grn")
        await repo.insert(grns, {"id": identity, "po_id": po["id"], "occurred_at": iso_utc(clock.now())})
        for line in payload["lines"]:
            if line["item_id"] not in ordered:
                raise CommandError("supply.item_not_on_po")
            received = await receive_stock(
                repo, clock, pack, line["item_id"], line["qty_milli"], line.get("batch")
            )
            await repo.insert(
                grn_lines,
                {
                    "id": new_id("grnline"),
                    "grn_id": identity,
                    "item_id": line["item_id"],
                    "qty_milli": line["qty_milli"],
                    "batch_id": received["batch_id"],
                },
            )
        await move(repo, po, "received")
        return {"grn_id": identity, "po_id": po["id"]}

    async def record_bill(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        po = await po_row(repo, payload["po_id"])
        if po["status"] != "received":
            raise CommandError("supply.not_received")
        if await repo.select(supplier_bills, supplier_bills.c.po_id == po["id"]):
            raise CommandError("supply.bill_exists")
        agreed = {r["item_id"]: r for r in await repo.select(po_lines, po_lines.c.po_id == po["id"])}
        grn = (await repo.select(grns, grns.c.po_id == po["id"]))[0]
        got: dict[str, int] = {}
        for row in await repo.select(grn_lines, grn_lines.c.grn_id == grn["id"]):
            got[row["item_id"]] = got.get(row["item_id"], 0) + row["qty_milli"]
        identity, total, variance = new_id("sbill"), 0, 0
        for line in payload["lines"]:
            if line["item_id"] not in agreed:
                raise CommandError("supply.item_not_on_po")
            amount = line_amount(line["unit_price_paise"], line["qty_milli"])
            total += amount
            await repo.insert(
                supplier_bill_lines,
                {"id": new_id("sbline"), "bill_id": identity, **line, "amount_paise": amount},
            )
            await history(
                repo, po["supplier_id"], line["item_id"], line["unit_price_paise"], "bill", identity
            )
            expected_price = agreed[line["item_id"]]["unit_price_paise"]
            checks = [
                (
                    "price",
                    expected_price,
                    line["unit_price_paise"],
                    amount - line_amount(expected_price, line["qty_milli"]),
                ),
                (
                    "qty",
                    got.get(line["item_id"], 0),
                    line["qty_milli"],
                    amount - line_amount(line["unit_price_paise"], got.get(line["item_id"], 0)),
                ),
            ]
            for kind, expected, actual, delta in checks:
                if expected != actual:
                    await repo.insert(
                        grn_variances,
                        {
                            "id": new_id("variance"),
                            "po_id": po["id"],
                            "item_id": line["item_id"],
                            "kind": kind,
                            "expected": expected,
                            "actual": actual,
                            "delta_paise": delta,
                        },
                    )
                    variance += max(delta, 0)
        await repo.insert(
            supplier_bills,
            {
                "id": identity,
                "po_id": po["id"],
                "bill_ref": payload["bill_ref"],
                "total_paise": total,
                "occurred_at": iso_utc(clock.now()),
            },
        )
        payable = new_id("payable")
        await repo.insert(
            payables,
            {
                "id": payable,
                "supplier_ref": po["supplier_id"],
                "amount_paise": total,
                "due_on": payload["due_on"],
                "source_ref": identity,
                "occurred_at": iso_utc(clock.now()),
            },
        )
        await domain_event(bus, repo, "credit.payable_changed", {"payable_id": payable})
        claim_id = None
        if variance:
            claim_id = new_id("claim")
            lang = (await supplier(repo, po["supplier_id"]))["lang"]
            await repo.insert(
                claims,
                {
                    "id": claim_id,
                    "po_id": po["id"],
                    "supplier_id": po["supplier_id"],
                    "amount_paise": variance,
                    "status": "draft",
                    "lang": lang,
                    "created_at": iso_utc(clock.now()),
                },
            )
            await domain_event(
                bus,
                repo,
                "po.variance_found",
                {"po_id": po["id"], "claim_id": claim_id, "amount_paise": variance},
            )
        return {
            "bill_id": identity,
            "payable_id": payable,
            "total_paise": total,
            "variance_paise": variance,
            "claim_id": claim_id,
            "readback_key": "supply.bill_readback",
        }

    async def send_claim(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        rows = await repo.select(claims, claims.c.id == payload["claim_id"])
        if not rows or rows[0]["status"] != "draft":
            raise CommandError("supply.claim_not_found")
        await repo.update(claims, {"status": "sent"}, claims.c.id == payload["claim_id"])
        await domain_event(bus, repo, "po.changed", {"po_id": rows[0]["po_id"], "status": "claim_sent"})
        return {"claim_id": payload["claim_id"], "status": "sent"}

    for kind, handler in [
        ("supply.add_supplier", add_supplier),
        ("supply.record_quote", record_quote),
        ("supply.draft_po", draft_po),
        ("supply.place_po", place),
        ("supply.confirm_po", confirm),
        ("supply.cancel_po", cancel),
        ("supply.receive", receive),
        ("supply.record_bill", record_bill),
        ("supply.send_claim", send_claim),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler)
