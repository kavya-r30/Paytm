"""Tax invoices per merchant profile, GST summary and month-end books (TAX-1…3, BKS-1).

Prices are tax-inclusive. A regular-profile line splits as taxable = round_half_even(amount × 10000 /
(10000 + rate_bp)), tax = amount − taxable, CGST = round_half_even(tax / 2), SGST = tax − CGST, so every
invoice reconciles to the paisa. Arth reports figures; it never gives tax advice (TAX-4, L4).
"""

import json
from datetime import timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.money import div_round_half_even
from arth.core.schemas import schema
from arth.domains.commerce_tables import (
    bill_lines,
    expenses,
    invoice_lines,
    invoices,
    month_closes,
    offer_events,
    offer_issuances,
    returns,
)
from arth.domains.merchants import domain_event, owner_only, settings_view
from arth.domains.stock_tables import batches, stock_moves
from arth.domains.tables import item_tax, items
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository

KINDS = {"unregistered": "receipt", "composition": "bill_of_supply", "regular": "tax_invoice"}
IST = timedelta(hours=5, minutes=30)


def split_line(amount: int, rate_bp: int, profile: str) -> tuple[int, int, int]:
    """(taxable, cgst, sgst) for a tax-inclusive amount."""
    if profile != "regular" or rate_bp == 0:
        return amount, 0, 0
    taxable = div_round_half_even(amount * 10000, 10000 + rate_bp)
    tax = amount - taxable
    cgst = div_round_half_even(tax, 2)
    return taxable, cgst, tax - cgst


def ist_month(stamp: str) -> str:
    return (parse_iso(stamp) + IST).strftime("%Y-%m")


def financial_year(stamp: str) -> str:
    local = parse_iso(stamp) + IST
    start = local.year if local.month >= 4 else local.year - 1
    return f"{start}-{(start + 1) % 100:02d}"


async def issue_invoice(repo: Repository, clock: SimClock, bill_id: str) -> dict[str, Any]:
    """Transaction-local hook called by Counter when a bill closes (TAX-2)."""
    existing = await repo.select(invoices, invoices.c.bill_id == bill_id)
    if existing:
        return existing[0]
    profile = (await settings_view(repo))["tax_profile"]
    now = iso_utc(clock.now())
    year = financial_year(now)
    count = len([r for r in await repo.select(invoices) if r["number"].startswith(year + "/")])
    identity = new_id("invoice")
    totals = {"taxable_paise": 0, "cgst_paise": 0, "sgst_paise": 0, "total_paise": 0}
    rows = []
    for line in await repo.select(
        bill_lines, bill_lines.c.bill_id == bill_id, bill_lines.c.status == "active"
    ):
        tax = await repo.select(item_tax, item_tax.c.item_id == line["item_id"])
        rate = tax[0]["gst_rate_bp"] if tax else 0
        taxable, cgst, sgst = split_line(line["amount_paise"], rate, profile)
        rows.append(
            {
                "id": new_id("invline"),
                "invoice_id": identity,
                "item_id": line["item_id"],
                "hsn": tax[0]["hsn"] if tax else "",
                "rate_bp": rate,
                "amount_paise": line["amount_paise"],
                "taxable_paise": taxable,
                "cgst_paise": cgst,
                "sgst_paise": sgst,
            }
        )
        for key, value in zip(totals, (taxable, cgst, sgst, line["amount_paise"]), strict=True):
            totals[key] += value
    invoice = {
        "id": identity,
        "bill_id": bill_id,
        "number": f"{year}/{count + 1:06d}",
        "kind": KINDS[profile],
        "profile": profile,
        "month": ist_month(now),
        **totals,
        "issued_at": now,
    }
    await repo.insert(invoices, invoice)
    for row in rows:
        await repo.insert(invoice_lines, row)
    assert repo.session is not None and repo.command_id is not None
    from arth.governance.events import emit_event

    await emit_event(
        repo,
        clock,
        repo.session,
        "tax.invoice_issued",
        repo.command_id,
        {"invoice_id": identity, "bill_id": bill_id, "kind": invoice["kind"]},
    )
    return invoice


async def invoice_view(repo: Repository, bill_id: str) -> dict[str, Any] | None:
    rows = await repo.select(invoices, invoices.c.bill_id == bill_id)
    if not rows:
        return None
    row = rows[0]
    lines = await repo.select(invoice_lines, invoice_lines.c.invoice_id == row["id"])
    return {
        **{k: v for k, v in row.items() if k not in {"merchant_id", "seq"}},
        "lines": [
            {
                k: r[k]
                for k in (
                    "item_id",
                    "hsn",
                    "rate_bp",
                    "amount_paise",
                    "taxable_paise",
                    "cgst_paise",
                    "sgst_paise",
                )
            }
            for r in sorted(lines, key=lambda r: r["seq"])
        ],
    }


async def gst_summary(repo: Repository, month: str) -> dict[str, Any]:
    """TAX-3: outward supplies by rate; equals the sum of the month's invoices."""
    by_rate: dict[int, dict[str, int]] = {}
    count = 0
    for invoice in await repo.select(invoices, invoices.c.month == month):
        count += 1
        for line in await repo.select(invoice_lines, invoice_lines.c.invoice_id == invoice["id"]):
            bucket = by_rate.setdefault(
                line["rate_bp"], {"taxable_paise": 0, "cgst_paise": 0, "sgst_paise": 0, "total_paise": 0}
            )
            for key in ("taxable_paise", "cgst_paise", "sgst_paise"):
                bucket[key] += line[key]
            bucket["total_paise"] += line["amount_paise"]
    rates = [{"rate_bp": rate, **values} for rate, values in sorted(by_rate.items())]
    return {
        "month": month,
        "invoices": count,
        "rates": rates,
        "totals": {
            key: sum(r[key] for r in rates)
            for key in ("taxable_paise", "cgst_paise", "sgst_paise", "total_paise")
        },
    }


async def profit_and_loss(repo: Repository, month: str) -> dict[str, Any]:
    """BKS-1: reproducible from tables. Sales net of GST and returns; COGS from batch cost, else item cost."""
    month_invoices = await repo.select(invoices, invoices.c.month == month)
    sales = sum(r["taxable_paise"] for r in month_invoices)
    returned = sum(
        r["amount_paise"] for r in await repo.select(returns) if ist_month(r["occurred_at"]) == month
    )
    costs = {r["id"]: r["cost_paise"] for r in await repo.select(batches)}
    item_cost = {r["id"]: r["cost_paise"] for r in await repo.select(items)}
    cogs = 0
    for move in await repo.select(stock_moves, stock_moves.c.reason.in_(["stock.issue", "stock.return"])):
        if ist_month(move["occurred_at"]) == month:
            unit = costs.get(move["batch_id"], item_cost.get(move["item_id"], 0))
            cogs -= div_round_half_even(move["delta_qty_milli"] * unit, 1000)
    by_category: dict[str, int] = {}
    for row in await repo.select(expenses):
        if ist_month(row["occurred_at"]) == month:
            by_category[row["category"]] = by_category.get(row["category"], 0) + row["amount_paise"]
    merchant_funded = {
        r["id"] for r in await repo.select(offer_issuances, offer_issuances.c.funding == "merchant")
    }
    rewards = sum(
        r["amount_paise"]
        for r in await repo.select(offer_events, offer_events.c.kind == "redeemed")
        if r["issuance_id"] in merchant_funded and ist_month(r["occurred_at"]) == month
    )
    net_sales = sales - returned
    gross = net_sales - cogs
    spent = sum(by_category.values())
    return {
        "month": month,
        "sales_paise": net_sales,
        "returns_paise": returned,
        "cogs_paise": cogs,
        "gross_profit_paise": gross,
        "expenses": [{"category": k, "amount_paise": v} for k, v in sorted(by_category.items())],
        "expenses_paise": spent,
        "reward_cost_paise": rewards,
        "net_paise": gross - spent - rewards,
    }


def register_books(bus: CommandBus) -> None:
    async def close_month(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        month = payload["month"]
        if month >= (bus.clock.now() + IST).strftime("%Y-%m"):
            raise CommandError("books.month_not_over")
        if await repo.select(month_closes, month_closes.c.month == month):
            raise CommandError("books.month_closed")
        pnl, gst = await profit_and_loss(repo, month), await gst_summary(repo, month)
        await repo.insert(
            month_closes,
            {
                "id": new_id("mclose"),
                "month": month,
                "pnl": json.dumps(pnl),
                "gst": json.dumps(gst),
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(bus, repo, "books.month_closed", {"month": month, "net_paise": pnl["net_paise"]})
        return {"month": month, "pnl": pnl, "gst": gst}

    bus.register("books.close_month", schema("books_close_month"), close_month)
