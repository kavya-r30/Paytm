"""Spec L2 invariants, checked after scenario beats and on generated worlds; returns violations."""

from typing import Any

from arth.core.clock import SimClock
from arth.domains.commerce_tables import bill_payments, bills, invoices, offer_programs
from arth.domains.ledger_tables import (
    advance_applications,
    advances,
    credit_accounts,
    credit_allocations,
    credit_entries,
)
from arth.domains.offers import liability
from arth.domains.stock_tables import batches, stock_moves
from arth.governance.audit import verify_audit
from arth.governance.repository import Repository


async def check(repo: Repository, clock: SimClock) -> list[str]:
    problems: list[str] = []
    paid: dict[str, int] = {}
    for row in await repo.select(bill_payments):
        paid[row["bill_id"]] = paid.get(row["bill_id"], 0) + row["amount_paise"]
    for bill in await repo.select(bills, bills.c.status == "closed"):
        if paid.get(bill["id"], 0) != bill["total_paise"]:
            problems.append(
                f"bill {bill['id']}: payments + khata {paid.get(bill['id'], 0)} != {bill['total_paise']}"
            )
    invoiced = {r["bill_id"]: r for r in await repo.select(invoices)}
    for bill in await repo.select(bills, bills.c.status == "closed"):
        invoice = invoiced.get(bill["id"])
        if invoice is None or invoice["total_paise"] != bill["total_paise"]:
            problems.append(f"bill {bill['id']}: invoice missing or total differs")
        elif (
            invoice["taxable_paise"] + invoice["cgst_paise"] + invoice["sgst_paise"] != invoice["total_paise"]
        ):
            problems.append(f"invoice {invoice['id']}: tax lines do not reconcile")
    for batch in await repo.select(batches):
        moves = await repo.select(stock_moves, stock_moves.c.batch_id == batch["id"])
        if sum(m["delta_qty_milli"] for m in moves) < 0:
            problems.append(f"batch {batch['id']}: negative stock")
    for account in await repo.select(credit_accounts):
        rows = await repo.select(credit_entries, credit_entries.c.account_id == account["id"])
        charged = sum(r["amount_paise"] for r in rows if r["amount_paise"] > 0)
        allocated = sum(
            r["amount_paise"]
            for r in await repo.select(credit_allocations, credit_allocations.c.account_id == account["id"])
        )
        if allocated > charged:
            problems.append(f"account {account['id']}: allocations {allocated} exceed charges {charged}")
        deposits = sum(
            r["amount_paise"] for r in await repo.select(advances, advances.c.account_id == account["id"])
        )
        applied = sum(
            r["amount_paise"]
            for r in await repo.select(
                advance_applications, advance_applications.c.account_id == account["id"]
            )
        )
        if applied > deposits:
            problems.append(f"account {account['id']}: advances applied {applied} > deposits {deposits}")
    for program in await repo.select(offer_programs):
        owed = await liability(repo, program["id"])
        if owed["outstanding_paise"] < 0 or owed["issued_paise"] > program["budget_paise"]:
            problems.append(f"program {program['id']}: liability {owed} breaks budget or sign")
    audit = await verify_audit(repo)
    if not audit["valid"]:
        problems.append(f"audit chain broken at seq {audit['bad_seq']}")
    return problems


async def summary(repo: Repository, clock: SimClock) -> dict[str, Any]:
    problems = await check(repo, clock)
    return {"ok": not problems, "violations": problems}
