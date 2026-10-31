"""Display-ready names and summaries for read models (UI contract-change requests, issue #2)."""

import json
from typing import Any

from arth.domains.commerce_tables import bill_lines, bills, price_history, purchase_orders, suppliers
from arth.domains.ledger_tables import credit_accounts, credit_allocations, credit_entries
from arth.domains.patron_tables import patron_identities, patrons, reward_ledger
from arth.domains.tables import items
from arth.governance.repository import Repository


def label(names: dict[str, str] | str) -> str:
    data = json.loads(names) if isinstance(names, str) else names
    return str(data.get("en") or next(iter(data.values()), ""))


async def item_name(repo: Repository, item_id: str | None) -> str:
    rows = await repo.select(items, items.c.id == item_id) if item_id else []
    return label(rows[0]["names"]) if rows else ""


async def supplier_name(repo: Repository, supplier_id: str | None) -> str:
    rows = await repo.select(suppliers, suppliers.c.id == supplier_id) if supplier_id else []
    return str(rows[0]["name"]) if rows else ""


async def item_supplier(repo: Repository, item_id: str) -> str | None:
    rows = await repo.select(price_history, price_history.c.item_id == item_id)
    if not rows:
        return None
    return await supplier_name(repo, max(rows, key=lambda r: r["seq"])["supplier_id"]) or None


async def patron_name(repo: Repository, patron_id: str | None) -> str | None:
    rows = await repo.select(patrons, patrons.c.id == patron_id) if patron_id else []
    return str(rows[0]["display_name"]) if rows else None


async def khata_balance(repo: Repository, patron_id: str) -> int | None:
    accounts = await repo.select(credit_accounts, credit_accounts.c.patron_id == patron_id)
    if not accounts:
        return None
    ids = [a["id"] for a in accounts]
    charged = sum(
        r["amount_paise"] for r in await repo.select(credit_entries, credit_entries.c.account_id.in_(ids))
    )
    paid = sum(
        r["amount_paise"]
        for r in await repo.select(credit_allocations, credit_allocations.c.account_id.in_(ids))
    )
    return int(charged - paid)


async def stamps(repo: Repository, patron_id: str) -> int:
    return sum(
        r["delta_stamps"] for r in await repo.select(reward_ledger, reward_ledger.c.patron_id == patron_id)
    )


async def patron_summary(repo: Repository, patron_id: str | None) -> dict[str, Any] | None:
    rows = await repo.select(patrons, patrons.c.id == patron_id) if patron_id else []
    if not rows or not patron_id:
        return None
    return {
        "id": patron_id,
        "display_name": rows[0]["display_name"],
        "lang": rows[0]["lang"],
        "khata_balance_paise": await khata_balance(repo, patron_id),
        "reward_stamps": await stamps(repo, patron_id),
    }


async def masked_phone(repo: Repository, patron_id: str) -> str | None:
    rows = await repo.select(
        patron_identities, patron_identities.c.patron_id == patron_id, patron_identities.c.kind == "phone"
    )
    if not rows or not rows[0]["value"].isdigit():
        return None
    phone = rows[0]["value"]
    return phone[:2] + "x" * (len(phone) - 5) + phone[-3:]


async def recent_customers(repo: Repository, limit: int = 10) -> list[dict[str, Any]]:
    seen: list[str] = []
    for bill in sorted(await repo.select(bills), key=lambda r: r["opened_at"], reverse=True):
        if bill["patron_id"] and bill["patron_id"] not in seen:
            seen.append(bill["patron_id"])
        if len(seen) >= limit:
            break
    if len(seen) < limit:
        for row in sorted(
            await repo.select(patrons, patrons.c.erased == 0), key=lambda r: r["created_at"], reverse=True
        ):
            if row["id"] not in seen:
                seen.append(row["id"])
            if len(seen) >= limit:
                break
    result = []
    for patron_id in seen:
        summary = await patron_summary(repo, patron_id)
        if summary and summary["display_name"] != "erased":
            result.append(
                {
                    "patron_id": patron_id,
                    "display_name": summary["display_name"],
                    "phone_masked": await masked_phone(repo, patron_id),
                    "khata_balance_paise": summary["khata_balance_paise"],
                    "reward_stamps": summary["reward_stamps"],
                }
            )
    return result


async def quick_items(repo: Repository, limit: int = 12) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """The bill grid: the shop's most-sold items first ("Aksar"), then the rest of the catalog."""
    sold: dict[str, int] = {}
    for line in await repo.select(bill_lines, bill_lines.c.status == "active"):
        sold[line["item_id"]] = sold.get(line["item_id"], 0) + 1
    catalog = [r for r in await repo.select(items) if r["category"] != "ingredient"]
    catalog.sort(key=lambda r: (-sold.get(r["id"], 0), label(r["names"])))
    grid = [
        {
            "item_id": r["id"],
            "name": label(r["names"]),
            "price_paise": r["price_paise"],
            "unit": r["unit"],
            "category": r["category"],
        }
        for r in catalog[:limit]
    ]
    categories = [{"key": "frequent", "label": "Aksar"}] + [
        {"key": c, "label": c} for c in sorted({r["category"] for r in catalog})
    ]
    return grid, categories


async def gate_summary(repo: Repository, kind: str, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """J1 binding fix: gate rows are computed from the gate's scope, never written by hand."""
    params: dict[str, Any] = {}
    for key in ("amount_paise", "khata_paise", "budget_paise", "limit_paise", "price_paise"):
        if isinstance(payload.get(key), int):
            params["amount_paise"] = payload[key]
            break
    if payload.get("po_id"):
        po = await repo.select(purchase_orders, purchase_orders.c.id == payload["po_id"])
        if po:
            params["supplier"] = await supplier_name(repo, po[0]["supplier_id"])
            params["amount_paise"] = po[0]["total_paise"]
    if payload.get("account_id"):
        account = await repo.select(credit_accounts, credit_accounts.c.id == payload["account_id"])
        params["patron"] = await patron_name(repo, account[0]["patron_id"]) if account else None
    if payload.get("patron_id"):
        params["patron"] = await patron_name(repo, payload["patron_id"])
    if payload.get("item_id"):
        params["item"] = await item_name(repo, payload["item_id"])
    return "gate." + kind.replace(".", "_"), params
