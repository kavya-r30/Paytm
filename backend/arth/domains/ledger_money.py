"""Transaction-local, immutable oldest-first payment and advance allocation."""

import json
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.domains.ledger_projection import account_ids, entry_status, statement
from arth.domains.ledger_tables import (
    advance_applications,
    advances,
    credit_allocations,
    credit_entries,
    ledger_payments,
)
from arth.governance.audit import canonical
from arth.governance.commands import CommandError
from arth.governance.repository import Repository


async def allocate_debt(
    repo: Repository, clock: SimClock, account_id: str, amount: int, ref: str
) -> list[dict[str, Any]]:
    ids = await account_ids(repo, account_id)
    entries = sorted(
        await repo.select(credit_entries, credit_entries.c.account_id.in_(ids)),
        key=lambda r: (r["occurred_at"], r["seq"]),
    )
    reversed_ids = {r["reversal_of"] for r in entries if r["reversal_of"]}
    existing = await repo.select(credit_allocations, credit_allocations.c.account_id.in_(ids))
    result = []
    for row in entries:
        if (
            row["amount_paise"] <= 0
            or row["id"] in reversed_ids
            or await entry_status(repo, row["id"]) == "disputed"
        ):
            continue
        due = row["amount_paise"] - sum(r["amount_paise"] for r in existing if r["entry_id"] == row["id"])
        paid = min(amount, due)
        if paid > 0:
            await repo.insert(
                credit_allocations,
                {
                    "id": new_id("alloc"),
                    "account_id": row["account_id"],
                    "entry_id": row["id"],
                    "payment_ref": ref,
                    "amount_paise": paid,
                    "occurred_at": iso_utc(clock.now()),
                },
            )
            result.append({"entry_id": row["id"], "amount_paise": paid})
            amount -= paid
        if amount == 0:
            break
    return result


async def allocate_payment(
    repo: Repository,
    clock: SimClock,
    account_id: str,
    amount_paise: int,
    payment_ref: str,
    mode: str,
    *,
    link_ref: str | None = None,
) -> dict[str, Any]:
    if not repo.command_id or amount_paise <= 0:
        raise CommandError("ledger.payment_requires_command")
    await account_ids(repo, account_id)
    prior = await repo.select(ledger_payments, ledger_payments.c.payment_ref == payment_ref)
    if prior:
        row = prior[0]
        if (row["account_id"], row["amount_paise"], row["mode"], row["link_ref"]) != (
            account_id,
            amount_paise,
            mode,
            link_ref,
        ):
            raise CommandError("ledger.payment_ref_conflict")
        return json.loads(row["result"])
    if await repo.select(advances, advances.c.source_ref == payment_ref):
        raise CommandError("ledger.payment_ref_conflict")
    allocated = await allocate_debt(repo, clock, account_id, amount_paise, payment_ref)
    excess = amount_paise - sum(r["amount_paise"] for r in allocated)
    if excess:
        await repo.insert(
            advances,
            {
                "id": new_id("advance"),
                "account_id": account_id,
                "amount_paise": excess,
                "source_ref": payment_ref,
                "purpose_ref": None,
                "occurred_at": iso_utc(clock.now()),
            },
        )
    view = await statement(repo, account_id, clock)
    result = {
        "account_id": account_id,
        "payment_ref": payment_ref,
        "allocations": allocated,
        "balance_paise": view["balance_paise"],
        "advance_paise": view["advance_paise"],
    }
    await repo.insert(
        ledger_payments,
        {
            "id": new_id("payment"),
            "account_id": account_id,
            "payment_ref": payment_ref,
            "amount_paise": amount_paise,
            "mode": mode,
            "link_ref": link_ref,
            "result": canonical(result),
            "occurred_at": iso_utc(clock.now()),
        },
    )
    return result


async def apply_advance(
    repo: Repository,
    clock: SimClock,
    account_id: str,
    amount_paise: int,
    ref_id: str,
    *,
    purpose_ref: str | None = None,
) -> dict[str, Any]:
    if not repo.command_id or amount_paise <= 0:
        raise CommandError("ledger.advance_requires_command")
    ids = await account_ids(repo, account_id)
    deposits = sorted(
        await repo.select(advances, advances.c.account_id.in_(ids), advances.c.purpose_ref == purpose_ref),
        key=lambda r: r["seq"],
    )
    used = await repo.select(advance_applications, advance_applications.c.account_id.in_(ids))
    if any(r["ref_id"] == ref_id for r in used):
        raise CommandError("ledger.advance_ref_conflict")
    available = {
        r["id"]: r["amount_paise"] - sum(u["amount_paise"] for u in used if u["advance_id"] == r["id"])
        for r in deposits
    }
    if amount_paise > sum(available.values()):
        raise CommandError("ledger.insufficient_advance")
    allocated = await allocate_debt(repo, clock, account_id, amount_paise, ref_id)
    if sum(r["amount_paise"] for r in allocated) != amount_paise:
        raise CommandError("ledger.advance_exceeds_payable_debt")
    remaining = amount_paise
    for row in deposits:
        used_amount = min(remaining, available[row["id"]])
        if used_amount:
            await repo.insert(
                advance_applications,
                {
                    "id": new_id("apply"),
                    "account_id": row["account_id"],
                    "advance_id": row["id"],
                    "amount_paise": used_amount,
                    "ref_id": ref_id,
                    "occurred_at": iso_utc(clock.now()),
                },
            )
            remaining -= used_amount
    return {"account_id": account_id, "allocations": allocated}
