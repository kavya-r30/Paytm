"""Conductor (T4.8, T4.15): one brain for device, console and WhatsApp turns.

Order: Injection Shield → scope → fast path → (model router if reachable) → tools/commands through the bus →
template narration → Grounding Guard → Critic → envelope v2. A turn can only *propose* writes: R1 runs, R2/R3
become approval cards, R4 returns the Console pointer. No apply/loan tool exists here.
"""

import json
import re
from datetime import timedelta
from typing import Any

from arth.ai.agent import ShopAgent
from arth.ai.fastpath import Intent, parse
from arth.ai.guards import Vault, critic, ground, injection, scope
from arth.ai.prompts import prompt
from arth.ai.router import ProviderRouter, ProviderUnavailable
from arth.ai.tables import turns
from arth.ai.templates import render
from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.spans import span_context
from arth.domains.catalog import public_item
from arth.domains.commerce_tables import bills
from arth.domains.counter import bill_state
from arth.domains.ledger import account_view, khata_view
from arth.domains.ledger_tables import credit_accounts
from arth.domains.merchants import settings_view
from arth.domains.patron_identity import related_ids, resolve_identity
from arth.domains.patron_tables import patrons
from arth.domains.resolution import resolve
from arth.domains.stock import stock_view
from arth.domains.tables import items
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


COUNTER_KINDS = {"remove_last", "set_last_qty", "undo", "park", "pay_qr", "pay_cash"}


def counter_command(parsed: Intent, text: str, bill_id: str | None) -> bool:
    """The fast path keeps only what must be instant and unambiguous: "haan teeno", and at an open bill the
    counter commands and plain item lists ("aur ek Parle-G"). Anything naming a customer, khata or a
    question goes to the model with tools."""
    if parsed.kind == "approve_all":
        return True
    if not bill_id:
        return False
    if parsed.kind in COUNTER_KINDS:
        return True
    lowered = text.lower()
    return parsed.kind == "add_lines" and not re.search(
        r"\b(ka|ke|ki|bill|khata|khate|udhaar|liye|customer|grahak|mein|aaye|mangwa|rate)\b", lowered
    )


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
        with span_context(session.merchant_id):  # every LLM, tool and policy span of this turn
            return await self._handle(session, text, surface, bill_id=bill_id, key=key)

    async def _handle(
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
            agent = None
            if topic in {"medical", "tax_advice"}:
                env, intent = self.envelope(lang, text, render(topic, lang)), topic
            elif parsed and counter_command(parsed, text, bill_id):
                env, intent = await self.run_intent(session, parsed, text, lang, bill_id, key)
            elif (agent := await ShopAgent(self, session, lang).run(text, bill_id, key)) is not None:
                env, intent = agent  # the model with the shop's tools (G4); writes still go through the bus
            elif parsed:  # model unreachable: the fast path keeps the counter and khata working offline
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
        if data.get("tool") and data["tool"] != "unknown":  # a question gets an answer, not just a screen
            params = {"tool": data["tool"]}
            if data.get("item"):
                params["item"] = str(data["item"])
            if data.get("customer"):  # the model saw ⟦P1⟧ tokens; the vault puts the real name back
                params["who"] = vault.fill(str(data["customer"]))
            return Intent("read", params, 0.7)
        if data.get("screen"):
            return Intent("nav", {"screen": data["screen"]}, 0.7)
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
                tool = intent.params["tool"]
                return await self.answer(mid, tool, heard, lang, intent.params), "read:" + tool
            if intent.kind == "approve_all":
                return await self.approve_all(
                    session, intent.params["exclude"], heard, lang, key
                ), "approve_all"
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
                        # CAT-3: no confident match → search; one hit is used, several are asked about
                        hits = await self.read(mid, lambda repo, text=spec["text"]: repo.search_catalog(text))
                        if len(hits) > 1:
                            options = [
                                json.loads(h["names"]).get("hi-Latn") or json.loads(h["names"]).get("en")
                                for h in hits[:2]
                            ]
                            said = " ya ".join(o for o in options if o) + "?"
                            chips = [{"label_key": "chip.choose_item", "turn_text": o} for o in options if o]
                            return self.envelope(lang, heard, said, followups=chips), "clarify"
                        if not hits:
                            return self.envelope(lang, heard, render("not_understood", lang)), "unknown_item"
                        found["selected"] = {"id": hits[0]["id"]}
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
                patron = await self.read(mid, _patron_by_name, intent.params["who"])
                if patron is None:
                    return self.envelope(lang, heard, render("not_understood", lang)), "clarify_patron"
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

    async def approve_all(
        self, session: Session, exclude: str, heard: str, lang: str, key: str
    ) -> dict[str, Any]:
        """WFL-4: "Haan, Mehta ko chhod ke" approves every pending gate except the one naming Mehta."""
        from arth.domains.summaries import gate_summary

        async def pending(repo: Repository) -> list[tuple[dict[str, Any], dict[str, Any]]]:
            rows = await repo.select(approvals, approvals.c.status == "pending")
            result = []
            for row in rows:
                scope = json.loads(row["scope"])
                result.append((row, (await gate_summary(repo, scope["type"], scope["payload"]))[1]))
            return result

        approved, skipped = 0, 0
        word = exclude.replace(" ji", "").strip().lower()
        for row, params in await self.read(session.merchant_id, pending):
            named = " ".join(str(v) for v in params.values() if v).lower()
            decision = "snooze" if word and word in named else "approve"
            try:
                await self.bus.decide(session, row["thread_id"], decision, f"{key}:{row['id']}")
            except CommandError:
                continue
            approved, skipped = approved + (decision == "approve"), skipped + (decision == "snooze")
        said = render("pending", lang, count=skipped) if skipped else render("done", lang)
        return self.envelope(lang, heard, said, provenance=[{"kind": "gates", "count": approved + skipped}])

    async def answer(
        self, mid: str, tool: str, heard: str, lang: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        clock = self.bus.clock
        params = params or {}
        facts: dict[str, Any]
        provenance: list[dict[str, Any]]
        if tool in {"item_stock", "item_price"}:
            said_item = str(params.get("item", heard))
            found = await self.read(mid, resolve, said_item)
            item = found["selected"]
            if item is None:  # "surf excel" for "Surf Excel Detergent": every spoken word in one unique name
                words = said_item.lower().split()
                catalog = [public_item(r) for r in await self.read(mid, lambda repo: repo.select(items))]
                named = [c for c in catalog if all(w in " ".join(c["names"].values()).lower() for w in words)]
                item = named[0] if len(named) == 1 else None
            if item is None:
                return self.envelope(
                    lang, heard, render("item_unknown", lang, text=params.get("item", heard))
                )
            name = item["names"].get("en") or next(iter(item["names"].values()))
            if tool == "item_price":
                facts = {"price_paise": item["price_paise"]}
                said = render("item_price", lang, name=name, money=item["price_paise"], unit=item["unit"])
                provenance = [{"kind": "catalog"}]
            else:
                rows = [
                    r
                    for r in (await self.read(mid, stock_view, clock))["items"]
                    if r["item_id"] == item["id"]
                ]
                qty_milli = rows[0]["on_hand_qty_milli"] if rows else 0
                qty = qty_milli // 1000 if qty_milli % 1000 == 0 else round(qty_milli / 1000, 1)
                facts = {"qty": qty, "qty_milli": qty_milli}
                said = render("item_stock", lang, name=name, qty=qty, unit=item["unit"])
                provenance = [{"kind": "stock"}]
            return self.envelope(lang, heard, said, provenance=provenance)
        if tool == "patron_khata":
            patron = await self.read(mid, _patron_by_name, str(params.get("who", "")))
            accounts = await self.read(mid, _accounts, patron) if patron else []
            if not accounts:
                return self.envelope(lang, heard, render("patron_unknown", lang, text=params.get("who", "")))
            view = await self.read(mid, account_view, accounts[0], clock)
            facts = {"balance_paise": view["balance_paise"]}
            said = render("patron_khata", lang, name=view["display_name"], money=view["balance_paise"])
            return self.envelope(
                lang,
                heard,
                said,
                provenance=[{"kind": "khata", "count": 1}],
                sensitivity="discreet",  # LED-12: one customer's dues are never read out loud by default
            )
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
            rounded = {k: round(day[k], -3) for k in ("p50_paise", "p10_paise", "p90_paise")}
            facts = {**day, "rounded": rounded}  # the spoken (rounded) figures are what the guard checks
            said = (
                render(  # an estimate is spoken in round rupees (nearest ₹10), never with paise
                    "forecast",
                    lang,
                    money=rounded["p50_paise"],
                    low=rounded["p10_paise"],
                    high=rounded["p90_paise"],
                )
                if result["status"] == "ready"
                else render("forecast_unknown", lang)
            )
            provenance = [{"kind": "forecast"}]
        elif tool == "low_stock":
            rows = [
                r for r in (await self.read(mid, stock_view, clock))["items"] if r["status"] in {"low", "out"}
            ]
            facts = {"count": len(rows)}
            names = list(dict.fromkeys(r["name"] for r in rows))  # one mention per name
            said = render("low_stock", lang, count=len(rows), names=", ".join(names[:3]) or "-")
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


async def _patron_by_name(repo: Repository, who: str) -> str | None:
    """Spoken name → one patron: identity resolution first, then a unique first-name match; else ask."""
    found = await resolve_identity(repo, "spoken_name", who)
    if found["candidates"] and not found["needs_clarification"]:
        return str(found["candidates"][0]["patron_id"])
    first = who.strip().lower().split()[0] if who.strip() else ""
    matches = [
        r["id"]
        for r in await repo.select(patrons, patrons.c.erased == 0)
        if r["display_name"].lower().split()[0] == first
    ]
    return str(matches[0]) if len(matches) == 1 else None
