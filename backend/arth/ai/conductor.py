"""Conductor (T4.8, T4.15): one brain for device, console and WhatsApp turns.

Order: Injection Shield → scope → fast path → (model router if reachable) → tools/commands through the bus →
template narration → Grounding Guard → Critic → envelope v2. A turn can only *propose* writes: R1 runs, R2/R3
become approval cards, R4 returns the Console pointer. No apply/loan tool exists here.
"""

import json
from datetime import timedelta
from typing import Any

from arth.ai.fastpath import Intent, parse
from arth.ai.guards import Vault, critic, ground, injection, scope
from arth.ai.prompts import prompt
from arth.ai.router import ProviderRouter, ProviderUnavailable
from arth.ai.tables import turns
from arth.ai.templates import render
from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.domains.commerce_tables import bills
from arth.domains.counter import bill_state
from arth.domains.ledger import khata_view
from arth.domains.ledger_tables import credit_accounts
from arth.domains.merchants import settings_view
from arth.domains.patron_identity import related_ids, resolve_identity
from arth.domains.patron_tables import patrons
from arth.domains.resolution import resolve
from arth.domains.stock import stock_view
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import approvals
from arth.intel.analytics import daily_sales, today, top_items
from arth.intel.forecast import sales_forecast

SPEECH = {
    "hi-Latn": "hi-IN",
    "hi": "hi-IN",
    "en": "en-IN",
    "mr": "mr-IN",
    "ta": "ta-IN",
    "bn": "bn-IN",
    "gu": "gu-IN",
    "te": "te-IN",
}
FOLLOWUPS = [
    {"label_key": "chip.aaj_kitna_aaya", "turn_text": "Aaj kitna aaya?"},
    {"label_key": "chip.khata_kitna", "turn_text": "Khata kitna baaki hai?"},
    {"label_key": "chip.kya_pending", "turn_text": "Kya pending hai?"},
]


class Conductor:
    def __init__(self, bus: CommandBus, router: ProviderRouter | None, calendar: Any = None) -> None:
        self.bus, self.router, self.calendar = bus, router, calendar

    async def read(self, merchant_id: str, fn: Any, *args: Any) -> Any:
        async with self.bus.db.read() as conn:
            return await fn(Repository(conn, merchant_id), *args)

    def envelope(self, lang: str, heard: str, said: str, **extra: Any) -> dict[str, Any]:
        return {
            "turn_id": new_id("turn"),
            "lang": {"screen": lang, "speech": SPEECH.get(lang, "hi-IN")},
            "speech": {"text": said, "voice": "sarvam:bulbul", "ssml_ready": True},
            "caption": {"heard": heard, "said": said},
            "audience": "owner",
            "cards": [],
            "followups": FOLLOWUPS[:2],
            "provenance": [],
            "presence": {"state": "speaking"},
            "tier": None,
            "sensitivity": "normal",
            **extra,
        }

    async def handle(
        self, session: Session, text: str, surface: str, *, bill_id: str | None = None, key: str | None = None
    ) -> dict[str, Any]:
        settings = await self.read(session.merchant_id, settings_view)
        lang = settings.get("screen_lang", "hi-Latn")
        key = key or new_id("turn")
        if injection(text):
            env = self.envelope(lang, text, render("blocked", lang), presence={"state": "alert"})
            intent = "blocked"
        else:
            topic = scope(text, settings["pack"])
            parsed = parse(text)
            if topic in {"medical", "tax_advice"}:
                env, intent = self.envelope(lang, text, render(topic, lang)), topic
            elif parsed:
                env, intent = await self.run_intent(session, parsed, text, lang, bill_id, key)
            else:
                routed = await self.route_with_model(session, text)
                if routed:
                    env, intent = await self.run_intent(session, routed, text, lang, bill_id, key)
                else:
                    said = render("other" if topic == "other" else "not_understood", lang)
                    env, intent = self.envelope(lang, text, said, followups=FOLLOWUPS), "not_understood"
        if critic(env["speech"]["text"]):
            env = self.envelope(lang, text, render("not_understood", lang))  # never say a hard-rule violation
        await self.log(session, surface, text, intent, env)
        return env

    async def route_with_model(self, session: Session, text: str) -> Intent | None:
        if self.router is None:
            return None
        names = [
            r["display_name"] for r in await self.read(session.merchant_id, lambda repo: repo.select(patrons))
        ]
        vault = Vault(names=names)
        spec = prompt("router.v1")
        try:
            result = await self.router.chat(
                spec["role"],
                [
                    {"role": "system", "content": spec["system"]},
                    {"role": "user", "content": f"<user>{vault.mask(text)}</user>"},
                ],
                json_mode=True,
            )
            data = json.loads(result.text or "{}")
        except (ProviderUnavailable, json.JSONDecodeError):
            return None
        if data.get("screen"):
            return Intent("nav", {"screen": data["screen"]}, 0.7)
        if data.get("tool") and data["tool"] != "unknown":
            return Intent("read", {"tool": data["tool"]}, 0.7)
        return None

    async def submit(self, session: Session, kind: str, payload: dict[str, Any], key: str) -> dict[str, Any]:
        return await self.bus.submit(session, kind, payload, key)

    async def current_bill(self, session: Session, bill_id: str | None, key: str) -> str:
        if bill_id:
            return bill_id
        open_bills = await self.read(
            session.merchant_id,
            lambda repo: repo.select(bills, bills.c.status == "open", bills.c.staff_id == session.actor_id),
        )
        if open_bills:
            return str(max(open_bills, key=lambda r: r["opened_at"])["id"])
        return str((await self.submit(session, "counter.open_bill", {}, key + ":open"))["data"]["bill_id"])

    async def run_intent(
        self, session: Session, intent: Intent, heard: str, lang: str, bill_id: str | None, key: str
    ) -> tuple[dict[str, Any], str]:
        mid = session.merchant_id
        try:
            if intent.kind == "read":
                return await self.answer(mid, intent.params["tool"], heard, lang), "read:" + intent.params[
                    "tool"
                ]
            if intent.kind == "nav":
                return self.envelope(
                    lang, heard, render("nav", lang), nav={"screen": intent.params["screen"]}
                ), "nav"
            if intent.kind == "add_lines":
                lines = []
                for spec in intent.params["lines"]:
                    found = await self.read(mid, resolve, spec["text"])
                    if found["needs_clarification"]:
                        options = [
                            c["names"].get("hi-Latn") or c["names"].get("en") for c in found["candidates"][:2]
                        ]
                        said = " ya ".join(o for o in options if o) + "?"
                        chips = [{"label_key": "chip.choose_item", "turn_text": o} for o in options if o]
                        return self.envelope(lang, heard, said, followups=chips[:3]), "clarify"
                    if not found["selected"]:
                        return self.envelope(lang, heard, render("not_understood", lang)), "unknown_item"
                    line: dict[str, Any] = {"item_id": found["selected"]["id"], "added_via": "voice"}
                    line.update({k: spec[k] for k in ("qty_milli", "amount_paise") if k in spec})
                    lines.append(line)
                bill = await self.current_bill(session, bill_id, key)
                result = await self.submit(
                    session, "counter.add_lines", {"bill_id": bill, "lines": lines}, key
                )
                state = await self.read(mid, bill_state, bill)
                names = ", ".join(line["name"] for line in state["lines"][-len(lines) :])
                env = self.envelope(
                    lang,
                    heard,
                    render("added", lang, names=names, money=state["total_paise"]),
                    cards=[{"type": "bill", "id": bill, "audience": "all"}],
                    nav={"screen": "bill", "params": {"bill_id": bill}},
                    undo={
                        "command_id": result["command_id"],
                        "until": iso_utc(self.bus.clock.now() + timedelta(seconds=30)),
                    },
                    audience="all",
                )
                return env, "add_lines"
            if intent.kind in {"remove_last", "set_last_qty", "undo", "park", "pay_qr", "pay_cash"}:
                bill = await self.current_bill(session, bill_id, key)
                state = await self.read(mid, bill_state, bill)
                last = state["lines"][-1]["id"] if state["lines"] else None
                if intent.kind == "remove_last" and last:
                    await self.submit(session, "counter.remove_line", {"bill_id": bill, "line_id": last}, key)
                elif intent.kind == "set_last_qty" and last:
                    await self.submit(
                        session,
                        "counter.set_qty",
                        {"bill_id": bill, "line_id": last, "qty_milli": intent.params["qty_milli"]},
                        key,
                    )
                elif intent.kind == "undo":
                    await self.submit(session, "counter.undo", {"bill_id": bill}, key)
                elif intent.kind == "park":
                    await self.submit(session, "counter.park", {"bill_id": bill}, key)
                elif intent.kind == "pay_qr":
                    await self.submit(session, "counter.request_upi", {"bill_id": bill}, key)
                    return self.envelope(
                        lang,
                        heard,
                        render("done", lang),
                        nav={"screen": "bill/pay", "params": {"bill_id": bill}},
                    ), "pay_qr"
                elif intent.kind == "pay_cash":
                    await self.submit(
                        session,
                        "counter.checkout",
                        {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": state["due_paise"]}]},
                        key,
                    )
                state = await self.read(mid, bill_state, bill)
                said = render(
                    "removed"
                    if intent.kind == "remove_last"
                    else "added"
                    if intent.kind == "set_last_qty"
                    else "done",
                    lang,
                    names=state["lines"][-1]["name"] if state["lines"] else "",
                    money=state["total_paise"],
                )
                return self.envelope(
                    lang,
                    heard,
                    said,
                    cards=[{"type": "bill", "id": bill, "audience": "all"}],
                    nav={"screen": "bill", "params": {"bill_id": bill}},
                ), intent.kind
            if intent.kind == "khata_payment":
                found = await self.read(mid, resolve_identity, "spoken_name", intent.params["who"])
                if found["needs_clarification"] or not found["candidates"]:
                    return self.envelope(lang, heard, render("not_understood", lang)), "clarify_patron"
                patron = found["candidates"][0]["patron_id"]
                accounts = await self.read(mid, lambda repo: _accounts(repo, patron))
                if not accounts:
                    return self.envelope(lang, heard, render("not_understood", lang)), "no_account"
                gate = await self.submit(
                    session,
                    "ledger.record_payment",
                    {
                        "account_id": accounts[0],
                        "amount_paise": intent.params["amount_paise"],
                        "payment_ref": new_id("payment"),
                        "mode": "cash",
                    },
                    key,
                )
                card = {
                    "type": "approval",
                    "id": gate["gate_id"],
                    "audience": "owner",
                    "tier": gate["tier"],
                    "thread_id": gate["thread_id"],
                }
                return self.envelope(
                    lang,
                    heard,
                    render("gate", lang),
                    cards=[card],
                    tier=gate["tier"],
                    sensitivity="discreet",
                    presence={"state": "needs_you"},
                ), "khata_payment"
        except CommandError as exc:
            said = render("not_understood", lang)
            return self.envelope(lang, heard, said, presence={"state": "alert"}), "refused:" + str(exc)
        return self.envelope(lang, heard, render("not_understood", lang)), "unknown"

    async def answer(self, mid: str, tool: str, heard: str, lang: str) -> dict[str, Any]:
        clock = self.bus.clock
        facts: dict[str, Any]
        if tool == "today_sales":
            row = (await self.read(mid, daily_sales, today(clock), today(clock)))[0]
            facts = {"sales_paise": row["sales_paise"], "bills": row["bills"]}
            said = render("today_sales", lang, money=row["sales_paise"], bills=row["bills"])
            provenance = [{"kind": "bills", "count": row["bills"]}, {"kind": "upi_ledger"}]
        elif tool == "khata_total":
            view = await self.read(mid, khata_view, clock)
            facts = {"balance_paise": view["balance_paise"], "accounts": len(view["accounts"])}
            said = render("khata_total", lang, money=view["balance_paise"], accounts=len(view["accounts"]))
            provenance = [{"kind": "khata", "count": len(view["accounts"])}]
        elif tool == "pending":
            gates = await self.read(mid, lambda repo: repo.select(approvals, approvals.c.status == "pending"))
            facts = {"count": len(gates)}
            said, provenance = (
                render("pending", lang, count=len(gates)),
                [{"kind": "gates", "count": len(gates)}],
            )
        elif tool == "forecast":
            result = await self.read(mid, sales_forecast, clock, self.calendar)
            day = result["days"][1] if len(result["days"]) > 1 else result["days"][0]
            facts = day
            said = (
                render("forecast", lang, money=day["p50_paise"], low=day["p10_paise"], high=day["p90_paise"])
                if result["status"] == "ready"
                else render("forecast_unknown", lang)
            )
            provenance = [{"kind": "forecast"}]
        elif tool == "low_stock":
            rows = [
                r for r in (await self.read(mid, stock_view, clock))["items"] if r["status"] in {"low", "out"}
            ]
            facts = {"count": len(rows)}
            said = render(
                "low_stock", lang, count=len(rows), names=", ".join(r["name"] for r in rows[:3]) or "-"
            )
            provenance = [{"kind": "stock", "count": len(rows)}]
        else:
            rows = await self.read(mid, top_items, today(clock) - timedelta(days=6), today(clock), 3)
            facts = {"items": rows}
            said = render("top_items", lang, names=", ".join(r["name"] for r in rows) or "-")
            provenance = [{"kind": "bills"}]
        if ground(said, facts):  # Grounding Guard: an unsupported number never reaches the owner
            said = render("not_understood", lang)
        sensitive = tool == "khata_total"
        return self.envelope(
            lang, heard, said, provenance=provenance, sensitivity="discreet" if sensitive else "normal"
        )

    async def log(self, session: Session, surface: str, heard: str, intent: str, env: dict[str, Any]) -> None:
        names = [
            r["display_name"] for r in await self.read(session.merchant_id, lambda repo: repo.select(patrons))
        ]
        async with self.bus.db.write() as conn:
            repo = Repository(conn, session.merchant_id)
            await repo.insert(
                turns,
                {
                    "id": env["turn_id"],
                    "session_ref": session.session_id or session.actor_id,
                    "surface": surface,
                    "heard": Vault(names=names).mask(heard),
                    "intent": intent,
                    "envelope": json.dumps(env, ensure_ascii=False),
                    "created_at": iso_utc(self.bus.clock.now()),
                },
            )


async def _accounts(repo: Repository, patron_id: str) -> list[str]:
    rows = await repo.select(
        credit_accounts, credit_accounts.c.patron_id.in_(await related_ids(repo, patron_id))
    )
    return [r["id"] for r in rows]
