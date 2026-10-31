"""Scoped credit projections shared by handlers and screen views."""

from datetime import date
from typing import Any

from arth.core.clock import SimClock, iso_utc, parse_iso
from arth.domains.ledger_tables import (
    advance_applications,
    advances,
    credit_accounts,
    credit_allocations,
    credit_entries,
    credit_entry_events,
    credit_entry_lines,
    ledger_payments,
    promises,
    reminders,
)
from arth.domains.patron_identity import patron_row, related_ids
from arth.governance.commands import CommandError
from arth.governance.repository import Repository

EVENTS = ["credit.changed", "credit.reminder_requested", "credit.statement_requested", "patron.merged"]
STATEMENT_TEMPLATE = "statement.balance"


async def account_row(repo: Repository, account_id: str) -> dict[str, Any]:
    rows = await repo.select(credit_accounts, credit_accounts.c.id == account_id)
    if not rows:
        raise CommandError("ledger.account_not_found")
    return rows[0]


async def account_ids(repo: Repository, account_id: str) -> list[str]:
    row = await account_row(repo, account_id)
    patrons = await related_ids(repo, row["patron_id"])
    return [r["id"] for r in await repo.select(credit_accounts, credit_accounts.c.patron_id.in_(patrons))]


async def entry_status(repo: Repository, entry_id: str) -> str:
    rows = await repo.select(credit_entry_events, credit_entry_events.c.entry_id == entry_id)
    return max(rows, key=lambda r: r["seq"])["status"] if rows else "open"


async def promise_paid(repo: Repository, promise: dict[str, Any]) -> int:
    """Payments made from the promise until the end of its IST due day (18:30 UTC)."""
    rows = await repo.select(
        ledger_payments,
        ledger_payments.c.account_id.in_(await account_ids(repo, promise["account_id"])),
        ledger_payments.c.occurred_at >= promise["occurred_at"],
        ledger_payments.c.occurred_at < iso_utc(parse_iso(promise["due_on"] + "T18:30:00Z")),
    )
    return sum(r["amount_paise"] for r in rows)


async def promise_status(repo: Repository, promise: dict[str, Any], clock: SimClock) -> str:
    if await promise_paid(repo, promise) >= promise["amount_paise"]:
        return "kept"
    return "broken" if date.fromisoformat(promise["due_on"]) < clock.now_ist().date() else "active"


async def pay_link_ref(repo: Repository, ids: list[str]) -> str | None:
    rows = await repo.select(reminders, reminders.c.account_id.in_(ids))
    return max(rows, key=lambda r: (r["occurred_at"], r["id"]))["link_id"] if rows else None


async def statement(repo: Repository, account_id: str, clock: SimClock) -> dict[str, Any]:
    ids = await account_ids(repo, account_id)
    entries = sorted(
        await repo.select(credit_entries, credit_entries.c.account_id.in_(ids)),
        key=lambda r: (r["occurred_at"], r["seq"]),
    )
    allocations = await repo.select(credit_allocations, credit_allocations.c.account_id.in_(ids))
    deposits = await repo.select(advances, advances.c.account_id.in_(ids))
    used = await repo.select(advance_applications, advance_applications.c.account_id.in_(ids))
    lines = await repo.select(
        credit_entry_lines, credit_entry_lines.c.entry_id.in_([r["id"] for r in entries])
    )
    entry_total = sum(r["amount_paise"] for r in entries)
    allocated = sum(r["amount_paise"] for r in allocations)
    rendered = []
    for row in entries:
        rendered.append(
            {
                **{
                    k: row[k]
                    for k in (
                        "id",
                        "account_id",
                        "amount_paise",
                        "source",
                        "ref_id",
                        "member_id",
                        "reversal_of",
                        "occurred_at",
                    )
                },
                "status": await entry_status(repo, row["id"]),
                "allocated_paise": sum(r["amount_paise"] for r in allocations if r["entry_id"] == row["id"]),
                "lines": [
                    {
                        k: r[k]
                        for k in (
                            "item_id",
                            "description_key",
                            "qty_milli",
                            "unit_price_paise",
                            "amount_paise",
                        )
                    }
                    for r in lines
                    if r["entry_id"] == row["id"]
                ],
            }
        )
    return {
        "account_id": account_id,
        "as_of": clock.now().isoformat(),
        "entries": rendered,
        "payments": [
            {k: r[k] for k in ("payment_ref", "amount_paise", "mode", "occurred_at")}
            for r in await repo.select(ledger_payments, ledger_payments.c.account_id.in_(ids))
        ],
        "entries_paise": entry_total,
        "allocated_paise": allocated,
        "balance_paise": entry_total - allocated,
        "advance_paise": sum(r["amount_paise"] for r in deposits) - sum(r["amount_paise"] for r in used),
        "pay_link_ref": await pay_link_ref(repo, ids) if entry_total > allocated else None,
        "invalidate_on": EVENTS,
    }


async def account_view(repo: Repository, account_id: str, clock: SimClock) -> dict[str, Any]:
    row = await account_row(repo, account_id)
    report = await statement(repo, account_id, clock)
    linked = await repo.select(credit_accounts, credit_accounts.c.id.in_(await account_ids(repo, account_id)))
    patron = await patron_row(repo, row["patron_id"])
    return {
        **report,
        "patron_id": row["patron_id"],
        "display_name": patron["display_name"],
        "limit_paise": min(r["limit_paise"] for r in linked),
        "promises": [
            {k: r[k] for k in ("id", "amount_paise", "due_on", "occurred_at")}
            | {"status": await promise_status(repo, r, clock)}
            for r in await repo.select(
                promises, promises.c.account_id.in_(await account_ids(repo, account_id))
            )
        ],
    }


async def khata_view(repo: Repository, clock: SimClock) -> dict[str, Any]:
    rows = await repo.select(credit_accounts)
    seen: set[tuple[str, ...]] = set()
    accounts = []
    for row in rows:
        group = tuple(sorted(await account_ids(repo, row["id"])))
        if group not in seen:
            seen.add(group)
            accounts.append(await account_view(repo, row["id"], clock))
    return {
        "accounts": accounts,
        "balance_paise": sum(r["balance_paise"] for r in accounts),
        "advance_paise": sum(r["advance_paise"] for r in accounts),
        "invalidate_on": EVENTS,
    }
