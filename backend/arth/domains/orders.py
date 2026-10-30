"""Customer orders and salon appointments as explicit state machines (ORD-2, ORD-5, SAL-1…2).

Customer text is untrusted: a customer or system actor can only create drafts; every later transition
needs a shop actor, and accept/decline/substitute are R3 gates.
"""

from datetime import timedelta
from typing import Any

from arth.core.clock import iso_utc, parse_iso
from arth.core.ids import new_id
from arth.core.packs import PackRegistry
from arth.core.qty import line_amount
from arth.core.schemas import schema
from arth.domains.catalog import get_item
from arth.domains.commerce_tables import appointments, order_events, order_lines, orders, staff_skills
from arth.domains.ledger_projection import account_view
from arth.domains.ledger_tables import credit_entries, credit_entry_lines
from arth.domains.merchants import domain_event, owner_only
from arth.domains.patron_identity import patron_row, related_ids
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import PolicyContext
from arth.governance.repository import Repository
from arth.governance.tables import merchants, staff

ORDER_FLOW = {
    "draft": {"placed", "cancelled"},
    "placed": {"accepted", "cancelled"},
    "accepted": {"packed", "cancelled"},
    "packed": {"delivered", "cancelled"},
    "delivered": {"settled", "on_credit"},
}
APPOINTMENT_FLOW = {
    "booked": {"checked_in", "no_show", "cancelled"},
    "waiting": {"cancelled"},
    "checked_in": {"completed"},
}
CHECK_BELOW_BP = 8000  # lines below this confidence are flagged "check", never silently trusted


async def order_row(repo: Repository, order_id: str) -> dict[str, Any]:
    rows = await repo.select(orders, orders.c.id == order_id)
    if not rows:
        raise CommandError("orders.not_found")
    return rows[0]


async def _lines(repo: Repository, order_id: str) -> list[dict[str, Any]]:
    return await repo.select(
        order_lines, order_lines.c.order_id == order_id, order_lines.c.status == "active"
    )


def _name(item: dict[str, Any]) -> str:
    return str(item["names"].get("en") or next(iter(item["names"].values())))


async def order_detail(repo: Repository, order_id: str) -> dict[str, Any]:
    row = await order_row(repo, order_id)
    lines = await _lines(repo, order_id)
    pick = []
    for line in lines:
        if line["item_id"]:
            pick.append(
                {
                    "item_id": line["item_id"],
                    "name": _name(await get_item(repo, line["item_id"])),
                    "qty_milli": line["qty_milli"],
                }
            )
    history = sorted(
        await repo.select(order_events, order_events.c.order_id == order_id), key=lambda r: r["seq"]
    )
    return {
        "order": {
            **{k: row[k] for k in ("id", "status", "channel", "patron_id", "total_paise", "created_at")},
            "lines": [
                {
                    k: line[k]
                    for k in ("id", "item_id", "text", "qty_milli", "unit_price_paise", "amount_paise")
                }
                | {"check": line["item_id"] is None or line["confidence_bp"] < CHECK_BELOW_BP}
                for line in lines
            ],
        },
        "history": [
            {k: h[k] for k in ("from_state", "to_state", "actor_id", "occurred_at")} for h in history
        ],
        "pick_list": pick,
        "allowed": sorted(ORDER_FLOW.get(row["status"], set())),
        "invalidate_on": ["order.changed"],
    }


async def orders_list(repo: Repository) -> dict[str, Any]:
    rows = sorted(await repo.select(orders), key=lambda r: r["created_at"], reverse=True)
    by_status: dict[str, int] = {}
    result = []
    for row in rows:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
        result.append(
            {k: row[k] for k in ("id", "status", "channel", "patron_id", "total_paise", "created_at")}
            | {"lines": len(await _lines(repo, row["id"]))}
        )
    return {"orders": result, "by_status": by_status, "invalidate_on": ["order.changed"]}


async def appointments_view(repo: Repository, day: str) -> dict[str, Any]:
    start = iso_utc(parse_iso(day + "T00:00:00Z") - timedelta(hours=5, minutes=30))
    end = iso_utc(parse_iso(start) + timedelta(days=1))
    rows = await repo.select(appointments)
    keys = ("id", "service_item_id", "staff_id", "patron_id", "start_at", "end_at", "status", "source")
    today = [r for r in rows if r["start_at"] and start <= r["start_at"] < end]
    columns = []
    for member in await repo.select(staff):
        skills = [
            r["skill"] for r in await repo.select(staff_skills, staff_skills.c.staff_id == member["id"])
        ]
        mine = sorted((r for r in today if r["staff_id"] == member["id"]), key=lambda r: r["start_at"])
        if skills or mine:
            columns.append(
                {
                    "id": member["id"],
                    "name": member["name"],
                    "skills": skills,
                    "appointments": [{k: r[k] for k in keys} for r in mine],
                }
            )
    return {
        "date": day,
        "staff": columns,
        "walk_ins": [{k: r[k] for k in keys} for r in rows if r["status"] == "waiting"],
        "no_shows": len([r for r in today if r["status"] == "no_show"]),
        "invalidate_on": ["order.appointment_changed", "bill.changed"],
    }


def register_orders(bus: CommandBus, packs: PackRegistry) -> None:
    clock = bus.clock

    def trusted(repo: Repository) -> str:
        session = repo.session
        assert session is not None
        if session.role == "system" or session.actor_kind in {"customer", "system", "simulator"}:
            raise CommandError("orders.untrusted_actor")  # ORD-5
        return session.actor_id

    async def move(repo: Repository, order: dict[str, Any], to: str, actor: str) -> None:
        if to not in ORDER_FLOW.get(order["status"], set()):
            raise CommandError("orders.illegal_transition")
        now = iso_utc(clock.now())
        await repo.update(orders, {"status": to, "updated_at": now}, orders.c.id == order["id"])
        await repo.insert(
            order_events,
            {
                "id": new_id("oevent"),
                "order_id": order["id"],
                "from_state": order["status"],
                "to_state": to,
                "actor_id": actor,
                "occurred_at": now,
            },
        )
        await domain_event(bus, repo, "order.changed", {"order_id": order["id"], "status": to})

    async def total(repo: Repository, order_id: str) -> int:
        amount = sum(r["amount_paise"] for r in await _lines(repo, order_id))
        await repo.update(orders, {"total_paise": amount}, orders.c.id == order_id)
        return amount

    async def add_line(repo: Repository, order_id: str, spec: dict[str, Any]) -> None:
        price = (await get_item(repo, spec["item_id"]))["price_paise"] if spec.get("item_id") else 0
        await repo.insert(
            order_lines,
            {
                "id": new_id("oline"),
                "order_id": order_id,
                "item_id": spec.get("item_id"),
                "text": spec["text"],
                "qty_milli": spec["qty_milli"],
                "unit_price_paise": price,
                "amount_paise": line_amount(price, spec["qty_milli"]),
                "confidence_bp": spec["confidence_bp"],
            },
        )

    async def create_draft(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        assert repo.session is not None
        if payload.get("patron_id"):
            await patron_row(repo, payload["patron_id"])
        identity, now = new_id("order"), iso_utc(clock.now())
        await repo.insert(
            orders,
            {
                "id": identity,
                "status": "draft",
                "channel": payload["channel"],
                "patron_id": payload.get("patron_id"),
                "message_ref": payload.get("message_ref"),
                "total_paise": 0,
                "created_at": now,
                "updated_at": now,
            },
        )
        for spec in payload["lines"]:
            await add_line(repo, identity, spec)
        await total(repo, identity)
        await repo.insert(
            order_events,
            {
                "id": new_id("oevent"),
                "order_id": identity,
                "from_state": None,
                "to_state": "draft",
                "actor_id": repo.session.actor_id,
                "occurred_at": now,
            },
        )
        await domain_event(bus, repo, "order.changed", {"order_id": identity, "status": "draft"})
        return {"order_id": identity, "status": "draft"}

    async def place(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        actor = trusted(repo)
        order = await order_row(repo, payload["order_id"])
        if not [line for line in await _lines(repo, order["id"]) if line["item_id"]]:
            raise CommandError("orders.no_resolved_lines")
        await move(repo, order, "placed", actor)
        return {"order_id": order["id"], "status": "placed"}

    async def accept(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        actor = trusted(repo)
        order = await order_row(repo, payload["order_id"])
        if any(line["item_id"] is None for line in await _lines(repo, order["id"])):
            raise CommandError("orders.unresolved_lines")
        await move(repo, order, "accepted", actor)
        return {"order_id": order["id"], "status": "accepted", "total_paise": order["total_paise"]}

    async def decline(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        actor = trusted(repo)
        await move(repo, await order_row(repo, payload["order_id"]), "cancelled", actor)
        return {"order_id": payload["order_id"], "status": "cancelled", "reason_key": payload["reason_key"]}

    async def substitute(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        trusted(repo)
        order = await order_row(repo, payload["order_id"])
        if order["status"] not in {"draft", "placed", "accepted"}:
            raise CommandError("orders.illegal_transition")
        old = [r for r in await _lines(repo, order["id"]) if r["id"] == payload["line_id"]]
        if not old:
            raise CommandError("orders.line_not_found")
        await repo.update(order_lines, {"status": "replaced"}, order_lines.c.id == payload["line_id"])
        await add_line(
            repo,
            order["id"],
            {
                "item_id": payload["item_id"],
                "text": old[0]["text"],
                "qty_milli": payload["qty_milli"],
                "confidence_bp": 10000,
            },
        )
        amount = await total(repo, order["id"])
        await domain_event(bus, repo, "order.changed", {"order_id": order["id"], "status": order["status"]})
        return {"order_id": order["id"], "total_paise": amount}

    async def advance(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        actor = trusted(repo)
        await move(repo, await order_row(repo, payload["order_id"]), payload["to"], actor)
        return {"order_id": payload["order_id"], "status": payload["to"]}

    async def settle_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        if payload["mode"] == "on_credit":
            if not payload.get("account_id"):
                raise CommandError("orders.account_required")
            view = await account_view(repo, payload["account_id"], clock)
            order = await order_row(repo, payload["order_id"])
            if order["patron_id"] and order["patron_id"] not in await related_ids(repo, view["patron_id"]):
                raise CommandError("orders.account_patron_mismatch")
            if view["balance_paise"] + order["total_paise"] > view["limit_paise"]:
                raise CommandError("ledger.over_limit")
        return PolicyContext(sensitive=True)

    async def settle(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        actor = trusted(repo)
        await settle_context(repo, payload)
        order = await order_row(repo, payload["order_id"])
        result: dict[str, Any] = {"order_id": order["id"]}
        if payload["mode"] == "on_credit":
            await move(repo, order, "on_credit", actor)
            entry = new_id("entry")
            await repo.insert(
                credit_entries,
                {
                    "id": entry,
                    "account_id": payload["account_id"],
                    "amount_paise": order["total_paise"],
                    "source": "order",
                    "ref_id": order["id"],
                    "member_id": None,
                    "occurred_at": iso_utc(clock.now()),
                },
            )
            for line in await _lines(repo, order["id"]):
                await repo.insert(
                    credit_entry_lines,
                    {
                        "id": new_id("line"),
                        "entry_id": entry,
                        "item_id": line["item_id"],
                        "description_key": None,
                        "qty_milli": line["qty_milli"],
                        "unit_price_paise": line["unit_price_paise"],
                        "amount_paise": line["amount_paise"],
                    },
                )
            await domain_event(bus, repo, "credit.changed", {"account_id": payload["account_id"]})
            result.update(status="on_credit", entry_id=entry)
        else:
            await move(repo, order, "settled", actor)
            result["status"] = "settled"
        return result

    async def legal(repo: Repository, payload: dict[str, Any], target: str | None = None) -> PolicyContext:
        """Gate-time check: an illegal transition never becomes an approval request."""
        order = await order_row(repo, payload["order_id"])
        to = target or payload.get("to")
        if to and to not in ORDER_FLOW.get(order["status"], set()):
            raise CommandError("orders.illegal_transition")
        return PolicyContext(facts={"status": order["status"]})

    async def accept_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        context = await legal(repo, payload, "accepted")
        if any(line["item_id"] is None for line in await _lines(repo, payload["order_id"])):
            raise CommandError("orders.unresolved_lines")  # ORD-1: "check" lines are resolved, never guessed
        return context

    async def decline_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        return await legal(repo, payload, "cancelled")

    async def substitute_context(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
        order = await order_row(repo, payload["order_id"])
        if order["status"] not in {"draft", "placed", "accepted"}:
            raise CommandError("orders.illegal_transition")
        return PolicyContext(facts={"status": order["status"]})

    async def pack_check(repo: Repository) -> None:
        if not packs.get((await repo.select(merchants))[0]["pack"]).counter.appointments:
            raise CommandError("appointments.disabled")

    async def service(repo: Repository, item_id: str) -> dict[str, Any]:
        item = await get_item(repo, item_id)
        if "duration_minutes" not in item["details"]:
            raise CommandError("appointments.not_a_service")
        return item

    async def slot(
        repo: Repository, item: dict[str, Any], staff_id: str, start_at: str, ignore: str | None = None
    ) -> tuple[str, str]:
        if not await repo.select(staff, staff.c.id == staff_id):
            raise CommandError("appointments.staff_not_found")
        skills = {r["skill"] for r in await repo.select(staff_skills, staff_skills.c.staff_id == staff_id)}
        if item["details"]["required_skill"] not in skills:
            raise CommandError("appointments.skill_mismatch")
        start = iso_utc(parse_iso(start_at))
        end = iso_utc(parse_iso(start_at) + timedelta(minutes=item["details"]["duration_minutes"]))
        for row in await repo.select(
            appointments,
            appointments.c.staff_id == staff_id,
            appointments.c.status.in_(["booked", "checked_in"]),
        ):
            if row["id"] != ignore and row["start_at"] < end and start < row["end_at"]:
                raise CommandError("appointments.overlap")  # SAL-1/2: no double booking
        return start, end

    async def appointment_event(repo: Repository, identity: str, status: str) -> None:
        await domain_event(
            bus, repo, "order.appointment_changed", {"appointment_id": identity, "status": status}
        )

    async def book(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await pack_check(repo)
        item = await service(repo, payload["service_item_id"])
        start, end = await slot(repo, item, payload["staff_id"], payload["start_at"])
        if payload.get("patron_id"):
            await patron_row(repo, payload["patron_id"])
        identity = new_id("appt")
        await repo.insert(
            appointments,
            {
                "id": identity,
                "service_item_id": item["id"],
                "staff_id": payload["staff_id"],
                "patron_id": payload.get("patron_id"),
                "start_at": start,
                "end_at": end,
                "status": "booked",
                "source": payload["source"],
                "created_at": iso_utc(clock.now()),
            },
        )
        await appointment_event(repo, identity, "booked")
        return {"appointment_id": identity, "start_at": start, "end_at": end}

    async def walk_in(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        await pack_check(repo)
        item = await service(repo, payload["service_item_id"])
        identity = new_id("appt")
        await repo.insert(
            appointments,
            {
                "id": identity,
                "service_item_id": item["id"],
                "staff_id": None,
                "patron_id": payload.get("patron_id"),
                "start_at": None,
                "end_at": None,
                "status": "waiting",
                "source": "walk_in",
                "created_at": iso_utc(clock.now()),
            },
        )
        await appointment_event(repo, identity, "waiting")
        return {"appointment_id": identity, "status": "waiting"}

    async def appointment(repo: Repository, identity: str) -> dict[str, Any]:
        rows = await repo.select(appointments, appointments.c.id == identity)
        if not rows:
            raise CommandError("appointments.not_found")
        return rows[0]

    async def assign(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        row = await appointment(repo, payload["appointment_id"])
        if row["status"] not in {"waiting", "booked"}:
            raise CommandError("appointments.illegal_transition")
        item = await service(repo, row["service_item_id"])
        start, end = await slot(repo, item, payload["staff_id"], payload["start_at"], ignore=row["id"])
        await repo.update(
            appointments,
            {"staff_id": payload["staff_id"], "start_at": start, "end_at": end, "status": "booked"},
            appointments.c.id == row["id"],
        )
        await appointment_event(repo, row["id"], "booked")
        return {"appointment_id": row["id"], "start_at": start, "end_at": end}

    async def transition(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        row = await appointment(repo, payload["appointment_id"])
        if payload["to"] not in APPOINTMENT_FLOW.get(row["status"], set()):
            raise CommandError("appointments.illegal_transition")
        await repo.update(appointments, {"status": payload["to"]}, appointments.c.id == row["id"])
        await appointment_event(repo, row["id"], payload["to"])
        return {"appointment_id": row["id"], "status": payload["to"]}

    async def set_skills(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if not await repo.select(staff, staff.c.id == payload["staff_id"]):
            raise CommandError("staff.not_found")
        current = {
            r["skill"]
            for r in await repo.select(staff_skills, staff_skills.c.staff_id == payload["staff_id"])
        }
        for skill in sorted(set(payload["skills"]) - current):
            await repo.insert(staff_skills, {"staff_id": payload["staff_id"], "skill": skill})
        await domain_event(bus, repo, "staff.skills_set", payload)
        return payload

    for kind, handler, context in [
        ("orders.create_draft", create_draft, None),
        ("orders.place", place, None),
        ("orders.accept", accept, accept_context),
        ("orders.decline", decline, decline_context),
        ("orders.substitute", substitute, substitute_context),
        ("orders.advance", advance, None),
        ("orders.settle", settle, settle_context),
        ("appointments.book", book, None),
        ("appointments.walk_in", walk_in, None),
        ("appointments.assign", assign, None),
        ("appointments.transition", transition, None),
        ("staff.set_skills", set_skills, None),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler, context)
