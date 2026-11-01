"""Interest-free khata commands and trusted payment integration boundary."""

from datetime import date, timedelta
from typing import Any

from arth.core.clock import iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.qty import line_amount
from arth.core.schemas import schema
from arth.domains.ledger_money import allocate_payment, apply_advance
from arth.domains.ledger_projection import (
    STATEMENT_TEMPLATE,
    account_ids,
    account_row,
    account_view,
    entry_status,
    khata_view,
    promise_status,
    statement,
)
from arth.domains.ledger_tables import (
    advances,
    credit_accounts,
    credit_allocations,
    credit_entries,
    credit_entry_events,
    credit_entry_lines,
    ledger_payments,
    payable_allocations,
    payables,
    promises,
    reminders,
)
from arth.domains.merchants import domain_event, owner_only
from arth.domains.patron_identity import has_consent, patron_row, related_ids
from arth.domains.patron_tables import consents, household_members, patron_contacts, reward_ledger
from arth.domains.patrons import outbound_context
from arth.domains.tables import items
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import PolicyContext
from arth.governance.repository import Repository

__all__ = ["register_ledger", "allocate_payment", "apply_advance", "account_view", "statement", "khata_view"]


def register_ledger(bus: CommandBus) -> None:
    async def changed(repo: Repository, account_id: str) -> None:
        await domain_event(bus, repo, "credit.changed", {"account_id": account_id})

    async def group_promises(repo: Repository, account_id: str) -> list[dict[str, Any]]:
        return await repo.select(promises, promises.c.account_id.in_(await account_ids(repo, account_id)))

    async def entry_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        view = await account_view(repo, payload["account_id"], bus.clock)
        if payload["source"] == "import":
            owner_only(repo)
        elif "occurred_at" in payload:
            raise CommandError("ledger.timestamp_not_allowed")
        if payload.get("occurred_at") and parse_iso(payload["occurred_at"]) > bus.clock.now():
            raise CommandError("ledger.future_entry")
        total = 0
        for line in payload["lines"]:
            if line["item_id"]:
                if not await repo.select(items, items.c.id == line["item_id"]):
                    raise CommandError("ledger.item_not_found")
            elif payload["source"] != "import" or not line.get("description_key"):
                raise CommandError("ledger.item_required")
            total += line_amount(line["unit_price_paise"], line["qty_milli"])
        if total != payload["amount_paise"]:
            raise CommandError("ledger.lines_total_mismatch")
        if payload.get("member_id") and not await repo.select(
            household_members,
            household_members.c.id == payload["member_id"],
            household_members.c.active == 1,
            household_members.c.patron_id.in_(await related_ids(repo, view["patron_id"])),
        ):
            raise CommandError("ledger.unknown_household_member")
        if view["balance_paise"] + total > view["limit_paise"]:
            if not payload.get("limit_override") or not payload.get("reason_key"):
                raise CommandError("ledger.over_limit")
            owner_only(repo)
        return PolicyContext(sensitive=True)

    async def open_account(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        await patron_row(repo, payload["patron_id"])
        if await repo.select(
            credit_accounts, credit_accounts.c.patron_id.in_(await related_ids(repo, payload["patron_id"]))
        ):
            raise CommandError("ledger.account_exists")
        identity = new_id("account")
        await repo.insert(
            credit_accounts, {"id": identity, **payload, "created_at": iso_utc(bus.clock.now())}
        )
        await changed(repo, identity)
        return {"account_id": identity}

    async def set_limit(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        view = await account_view(repo, payload["account_id"], bus.clock)
        if payload["limit_paise"] > view["limit_paise"]:
            if any(r["status"] == "disputed" for r in view["entries"]):
                raise CommandError("ledger.dispute_freezes_limit")
            for promise in await group_promises(repo, payload["account_id"]):
                age = (bus.clock.now_ist().date() - date.fromisoformat(promise["due_on"])).days
                if age <= 60 and await promise_status(repo, promise, bus.clock) == "broken":
                    raise CommandError("ledger.broken_promise_freezes_limit")
        await repo.update(
            credit_accounts,
            {"limit_paise": payload["limit_paise"]},
            credit_accounts.c.id.in_(await account_ids(repo, payload["account_id"])),
        )
        await changed(repo, payload["account_id"])
        return payload

    async def add_entry(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        identity = new_id("entry")
        occurred = (
            iso_utc(parse_iso(payload["occurred_at"]))
            if payload.get("occurred_at")
            else iso_utc(bus.clock.now())
        )
        await repo.insert(
            credit_entries,
            {
                "id": identity,
                "account_id": payload["account_id"],
                "amount_paise": payload["amount_paise"],
                "source": payload["source"],
                "ref_id": payload.get("ref_id"),
                "member_id": payload.get("member_id"),
                "occurred_at": occurred,
            },
        )
        for line in payload["lines"]:
            await repo.insert(
                credit_entry_lines,
                {
                    "id": new_id("line"),
                    "entry_id": identity,
                    **line,
                    "amount_paise": line_amount(line["unit_price_paise"], line["qty_milli"]),
                },
            )
        await changed(repo, payload["account_id"])
        return {
            "account_id": payload["account_id"],
            "entry_id": identity,
            "amount_paise": payload["amount_paise"],
            "readback_key": "ledger.entry_readback",
        }

    async def payment(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        result = await allocate_payment(
            repo,
            bus.clock,
            payload["account_id"],
            payload["amount_paise"],
            payload["payment_ref"],
            payload["mode"],
        )
        await changed(repo, payload["account_id"])
        await receipt(repo, payload)
        return result

    async def verified_payment(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if not repo.private.get("payment_verified"):
            raise CommandError("ledger.verified_payment_required")
        links = await repo.select(
            reminders,
            reminders.c.link_id == payload["link_ref"],
            reminders.c.account_id == payload["account_id"],
        )
        if not links:
            raise CommandError("ledger.invalid_payment_link")
        result = await allocate_payment(
            repo,
            bus.clock,
            payload["account_id"],
            payload["amount_paise"],
            payload["payment_ref"],
            "upi_link",
            link_ref=payload["link_ref"],
        )
        await changed(repo, payload["account_id"])
        await receipt(repo, payload)
        return result

    async def receipt(repo: Repository, payload: dict[str, Any]) -> None:
        account = await account_row(repo, payload["account_id"])
        if not await has_consent(repo, account["patron_id"], "receipts"):
            return
        if await repo.select(
            patron_contacts,
            patron_contacts.c.command_id == payload["payment_ref"],
            patron_contacts.c.purpose == "receipts",
        ):
            return
        await repo.insert(
            patron_contacts,
            {
                "id": new_id("contact"),
                "patron_id": account["patron_id"],
                "purpose": "receipts",
                "command_id": payload["payment_ref"],
                "status": "reserved",
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )
        await domain_event(
            bus,
            repo,
            "credit.receipt_requested",
            {"account_id": account["id"], "payment_ref": payload["payment_ref"]},
        )

    async def deposit(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        await account_row(repo, payload["account_id"])
        existing = await repo.select(advances, advances.c.source_ref == payload["payment_ref"])
        if existing:
            row = existing[0]
            if (row["account_id"], row["amount_paise"], row["purpose_ref"]) != (
                payload["account_id"],
                payload["amount_paise"],
                payload.get("purpose_ref"),
            ):
                raise CommandError("ledger.payment_ref_conflict")
            return {"advance_id": row["id"]}
        if await repo.select(ledger_payments, ledger_payments.c.payment_ref == payload["payment_ref"]):
            raise CommandError("ledger.payment_ref_conflict")
        identity = new_id("advance")
        await repo.insert(
            advances,
            {
                "id": identity,
                "account_id": payload["account_id"],
                "amount_paise": payload["amount_paise"],
                "source_ref": payload["payment_ref"],
                "purpose_ref": payload.get("purpose_ref"),
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )
        await changed(repo, payload["account_id"])
        return {"advance_id": identity}

    async def use_advance(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        result = await apply_advance(
            repo,
            bus.clock,
            payload["account_id"],
            payload["amount_paise"],
            str(repo.command_id),
            purpose_ref=payload.get("purpose_ref"),
        )
        await changed(repo, payload["account_id"])
        return result

    async def transition(repo: Repository, payload: dict[str, Any], status: str) -> dict[str, Any]:
        rows = await repo.select(credit_entries, credit_entries.c.id == payload["entry_id"])
        if not rows or rows[0]["amount_paise"] <= 0:
            raise CommandError("ledger.entry_not_found")
        if status == "acknowledged" or status == "disputed" and repo.private.get("customer_patron_id"):
            account = await account_row(repo, rows[0]["account_id"])
            if repo.private.get("customer_patron_id") not in await related_ids(repo, account["patron_id"]):
                raise CommandError("ledger.customer_verification_required")
            if status == "acknowledged" and await entry_status(repo, payload["entry_id"]) == "disputed":
                raise CommandError("ledger.owner_resolution_required")
        else:
            owner_only(repo)
        await repo.insert(
            credit_entry_events,
            {
                "id": new_id("evt"),
                "entry_id": payload["entry_id"],
                "status": status,
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )
        await changed(repo, rows[0]["account_id"])
        return {"entry_id": payload["entry_id"], "status": status}

    async def dispute(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return await transition(repo, payload, "disputed")

    async def acknowledge(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return await transition(repo, payload, "acknowledged")

    async def resolve(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        return await transition(repo, payload, "resolved")

    async def reverse(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        rows = await repo.select(credit_entries, credit_entries.c.id == payload["entry_id"])
        if not rows or rows[0]["amount_paise"] <= 0:
            raise CommandError("ledger.entry_not_found")
        row = rows[0]
        if await repo.select(credit_allocations, credit_allocations.c.entry_id == row["id"]):
            raise CommandError("ledger.allocated_entry_requires_refund")
        if await repo.select(credit_entries, credit_entries.c.reversal_of == row["id"]):
            raise CommandError("ledger.already_reversed")
        identity = new_id("entry")
        await repo.insert(
            credit_entries,
            {
                "id": identity,
                "account_id": row["account_id"],
                "amount_paise": -row["amount_paise"],
                "source": "reversal",
                "ref_id": row["id"],
                "member_id": row["member_id"],
                "reversal_of": row["id"],
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )
        for line in await repo.select(credit_entry_lines, credit_entry_lines.c.entry_id == row["id"]):
            await repo.insert(
                credit_entry_lines,
                {
                    "id": new_id("line"),
                    "entry_id": identity,
                    **{k: line[k] for k in ("item_id", "description_key", "qty_milli", "unit_price_paise")},
                    "amount_paise": -line["amount_paise"],
                },
            )
        await changed(repo, row["account_id"])
        return {"entry_id": identity, "reversal_of": row["id"]}

    async def promise(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        report = await statement(repo, payload["account_id"], bus.clock)
        if (
            date.fromisoformat(payload["due_on"]) < bus.clock.now_ist().date()
            or payload["amount_paise"] > report["balance_paise"]
        ):
            raise CommandError("ledger.invalid_promise")
        identity = new_id("promise")
        await repo.insert(promises, {"id": identity, **payload, "occurred_at": iso_utc(bus.clock.now())})
        await changed(repo, payload["account_id"])
        return {"promise_id": identity}

    async def reminder_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        # The owner may send a dues reminder by hand at any time ("manual"): quiet hours, the weekly cap, the
        # minimum age, purchase day, an open promise and spacing guard Arth's own Collections, not the owner.
        # Consent, a due balance and no dispute always apply; agents never send manual reminders.
        manual = bool(payload.get("manual"))
        if manual and (
            repo.session is None or repo.session.role != "owner" or repo.session.actor_kind == "agent"
        ):
            raise CommandError("ledger.manual_owner_only")
        view = await account_view(repo, payload["account_id"], bus.clock)
        context = await outbound_context(repo, bus.clock, view["patron_id"], "reminders")
        if not context.consent or (
            not manual and context.weekly_contacts >= bus.policy.policies.reminders.per_patron_per_week
        ):
            return context
        if view["balance_paise"] <= 0 or any(r["status"] == "disputed" for r in view["entries"]):
            raise CommandError("ledger.reminder_frozen")
        today = bus.clock.now_ist().date()
        if manual:
            return await reminder_policy(repo, view, context, flags=("owner_manual",))
        purchases = [r for r in view["entries"] if r["amount_paise"] > r["allocated_paise"]]
        if not purchases or min(
            parse_iso(r["occurred_at"]).astimezone(bus.clock.now_ist().tzinfo).date() for r in purchases
        ) > today - timedelta(days=7):
            raise CommandError("ledger.reminder_too_early")
        if any(
            parse_iso(r["occurred_at"]).astimezone(bus.clock.now_ist().tzinfo).date() == today
            for r in view["entries"]
            if r["amount_paise"] > 0
        ):
            raise CommandError("ledger.purchase_day")
        ids = await related_ids(repo, view["patron_id"])
        visits = await repo.select(
            reward_ledger, reward_ledger.c.patron_id.in_(ids), reward_ledger.c.kind == "visit"
        )
        if any(
            parse_iso(r["occurred_at"]).astimezone(bus.clock.now_ist().tzinfo).date() == today for r in visits
        ):
            raise CommandError("ledger.purchase_day")
        for row in await group_promises(repo, payload["account_id"]):
            if await promise_status(repo, row, bus.clock) == "active":
                raise CommandError("ledger.promise_active")
        recent = sorted(
            await repo.select(
                reminders,
                reminders.c.patron_id.in_(ids),
                reminders.c.template_key != STATEMENT_TEMPLATE,
                reminders.c.occurred_at > iso_utc(bus.clock.now() - timedelta(days=30)),
            ),
            key=lambda r: r["occurred_at"],
        )
        cadence = bus.policy.policies.reminders.cadence_days
        if (
            len(recent) >= len(cadence)
            or recent
            and (bus.clock.now() - parse_iso(recent[0]["occurred_at"])).days < cadence[len(recent)]
        ):
            raise CommandError("ledger.reminder_cadence")
        return await reminder_policy(repo, view, context)

    async def reminder_policy(
        repo: Repository, view: dict[str, Any], context: PolicyContext, flags: tuple[str, ...] = ()
    ) -> PolicyContext:
        """The R3 gate's facts: the approval re-checks the balance and the customer's latest instruction."""
        ids = await related_ids(repo, view["patron_id"])
        instructions = await repo.select(
            consents, consents.c.patron_id.in_(ids), consents.c.purpose == "reminders"
        )
        facts = {
            "balance_paise": view["balance_paise"],
            "instruction_seq": max((r["seq"] for r in instructions), default=0),
        }
        repo.approval_conditions = {
            "balance_paise": {"lte": view["balance_paise"]},
            "instruction_seq": {"eq": facts["instruction_seq"]},
        }
        return PolicyContext(
            facts=facts,
            purpose="reminders",
            consent=True,
            weekly_contacts=context.weekly_contacts,
            sensitive=True,
            flags=flags,
        )

    async def mint_link(repo: Repository, account: dict[str, Any], template_key: str) -> dict[str, Any]:
        """Outbound credit request with a unique pay-link reference; delivery belongs to L2."""
        report = await statement(repo, account["id"], bus.clock)
        row = {
            "id": new_id("reminder"),
            "account_id": account["id"],
            "template_key": template_key,
            "patron_id": account["patron_id"],
            "link_id": new_id("link"),
            "balance_paise": report["balance_paise"],
            "command_id": repo.command_id,
            "occurred_at": iso_utc(bus.clock.now()),
        }
        await repo.insert(reminders, row)
        return row

    async def reminder(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        account = await account_row(repo, payload["account_id"])
        row = await mint_link(repo, account, payload["template_key"])  # `manual` only shaped the policy
        identity, link = row["id"], row["link_id"]
        report = {"balance_paise": row["balance_paise"]}
        await reserve(repo, account["patron_id"], "reminders")
        await domain_event(bus, repo, "credit.reminder_requested", {"reminder_id": identity})
        return {
            "reminder_id": identity,
            "link_ref": link,
            "account_id": account["id"],
            "balance_paise": report["balance_paise"],
        }

    async def reserve(repo: Repository, patron_id: str, purpose: str) -> None:
        await repo.insert(
            patron_contacts,
            {
                "id": new_id("contact"),
                "patron_id": patron_id,
                "purpose": purpose,
                "command_id": repo.command_id,
                "status": "reserved",
                "occurred_at": iso_utc(bus.clock.now()),
            },
        )

    async def statement_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        account = await account_row(repo, payload["account_id"])
        return await outbound_context(repo, bus.clock, account["patron_id"], "receipts")

    async def send_statement(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        account = await account_row(repo, payload["account_id"])
        report = await statement(repo, account["id"], bus.clock)
        link = (
            (await mint_link(repo, account, STATEMENT_TEMPLATE))["link_id"]
            if report["balance_paise"] > 0
            else None
        )
        await reserve(repo, account["patron_id"], "receipts")
        await domain_event(bus, repo, "credit.statement_requested", payload)
        return {"account_id": account["id"], "link_ref": link}

    async def add_payable(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        date.fromisoformat(payload["due_on"])
        existing = await repo.select(payables, payables.c.source_ref == payload["source_ref"])
        if existing:
            if any(existing[0][k] != value for k, value in payload.items()):
                raise CommandError("ledger.payable_ref_conflict")
            return {"payable_id": existing[0]["id"]}
        identity = new_id("payable")
        await repo.insert(payables, {"id": identity, **payload, "occurred_at": iso_utc(bus.clock.now())})
        await domain_event(bus, repo, "credit.payable_changed", {"payable_id": identity})
        return {"payable_id": identity}

    async def pay_payable(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        rows = await repo.select(payables, payables.c.id == payload["payable_id"])
        if not rows:
            raise CommandError("ledger.payable_not_found")
        prior = await repo.select(
            payable_allocations, payable_allocations.c.payment_ref == payload["payment_ref"]
        )
        if prior:
            if any(prior[0][k] != value for k, value in payload.items()):
                raise CommandError("ledger.payment_ref_conflict")
            return {"payable_id": payload["payable_id"]}
        paid = await repo.select(
            payable_allocations, payable_allocations.c.payable_id == payload["payable_id"]
        )
        if payload["amount_paise"] > rows[0]["amount_paise"] - sum(r["amount_paise"] for r in paid):
            raise CommandError("ledger.payable_overpayment")
        await repo.insert(
            payable_allocations, {"id": new_id("alloc"), **payload, "occurred_at": iso_utc(bus.clock.now())}
        )
        await domain_event(bus, repo, "credit.payable_changed", {"payable_id": payload["payable_id"]})
        return {"payable_id": payload["payable_id"]}

    handlers = {
        "open_account": open_account,
        "set_limit": set_limit,
        "add_entry": add_entry,
        "record_payment": payment,
        "apply_verified_payment": verified_payment,
        "record_deposit": deposit,
        "apply_advance": use_advance,
        "dispute_entry": dispute,
        "acknowledge_entry": acknowledge,
        "resolve_dispute": resolve,
        "reverse_entry": reverse,
        "record_promise": promise,
        "send_reminder": reminder,
        "send_statement": send_statement,
        "add_payable": add_payable,
        "pay_payable": pay_payable,
    }

    async def sensitive_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        return PolicyContext(sensitive=True)

    for name, handler in handlers.items():
        context = (
            entry_context
            if name == "add_entry"
            else reminder_context
            if name == "send_reminder"
            else statement_context
            if name == "send_statement"
            else sensitive_context
        )
        bus.register("ledger." + name, schema("ledger_" + name), handler, context)
