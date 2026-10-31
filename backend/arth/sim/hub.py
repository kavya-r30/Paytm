"""Simulated outside parties: Rails (bank/UPI), messaging network and lender (spec H1, v5.1 D7/D8).

Everything Arth learns from them arrives through signed webhooks that are verified at ingress and turned
into R1 commands from the restricted system actor. Simulator state lives in `sim_*` tables.
"""

import hashlib
import hmac
import json
from datetime import timedelta
from typing import Any

from arth.core.clock import iso_utc, parse_iso
from arth.core.ids import new_id
from arth.domains.ledger_tables import reminders
from arth.domains.patron_identity import identity_value
from arth.governance.commands import CommandBus, CommandError
from arth.governance.events import Dispatcher
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.sim.tables import (
    sim_lender_apps,
    sim_messages,
    sim_rails_cashbacks,
    sim_rails_faults,
    sim_rails_orders,
    sim_rails_payments,
    sim_rails_refunds,
    sim_rails_settlements,
    sim_threads,
)

QR_VALIDITY = timedelta(minutes=5)
FEE_BP = 10  # 0.1% platform fee in the settlement explainer
MARKETING_CAP_PER_WEEK = 1  # the network's own per-user cap (v5.1 D8)
IST = timedelta(hours=5, minutes=30)


class SignatureError(ValueError):
    pass


def system(merchant_id: str) -> Session:
    return Session(merchant_id, new_id("system"), "system", actor_kind="simulator")


class Simulators:
    def __init__(self, bus: CommandBus, dispatcher: Dispatcher | None, secret: str) -> None:
        self.bus, self.db, self.clock = bus, bus.db, bus.clock
        self._secret = hmac.new(secret.encode(), b"arth-sim-webhooks", hashlib.sha256).digest()
        self._utr = 0
        if dispatcher is not None:
            dispatcher.on("sim.world", self._consume)

    # signing -------------------------------------------------------------------------------------
    def sign(self, body: bytes) -> str:
        return hmac.new(self._secret, body, hashlib.sha256).hexdigest()

    def verify(self, body: bytes, signature: str) -> dict[str, Any]:
        if not hmac.compare_digest(self.sign(body), signature or ""):
            raise SignatureError("webhook.bad_signature")
        data: dict[str, Any] = json.loads(body)
        return data

    # rails ---------------------------------------------------------------------------------------
    def _next_utr(self) -> str:
        self._utr += 1
        stamp = int(self.clock.now().timestamp()) % 10**6
        return f"43{stamp:06d}{self._utr % 10**4:04d}"

    async def create_qr(self, merchant_id: str, order_ref: str, amount_paise: int) -> dict[str, Any]:
        token = new_id("qr").split("_", 1)[1].lower()
        expires = iso_utc(self.clock.now() + QR_VALIDITY)
        async with self.db.write() as conn:
            await Repository(conn, merchant_id).insert(
                sim_rails_orders,
                {
                    "id": new_id("simord"),
                    "order_ref": order_ref,
                    "token": token,
                    "amount_paise": amount_paise,
                    "status": "created",
                    "created_at": iso_utc(self.clock.now()),
                    "expires_at": expires,
                },
            )
        return {
            "token": token,
            "qr_payload": f"upi://pay?tr={order_ref}&am={amount_paise / 100:.2f}",
            "pay_url": f"/pay/{token}",
            "expires_at": expires,
            "amount_paise": amount_paise,
        }

    async def order_for_token(self, token: str) -> tuple[str, dict[str, Any]]:
        async with self.db.read() as conn:
            for merchant_id in self.bus.merchant_ids:
                rows = await Repository(conn, merchant_id).select(
                    sim_rails_orders, sim_rails_orders.c.token == token
                )
                if rows:
                    return merchant_id, rows[0]
        raise CommandError("sim.unknown_token")

    async def add_fault(self, merchant_id: str, kind: str, times: int = 1, arg: int = 0) -> None:
        if kind not in {"duplicate", "drop", "delay", "wrong_amount"}:
            raise CommandError("sim.unknown_fault")
        async with self.db.write() as conn:
            await Repository(conn, merchant_id).insert(
                sim_rails_faults, {"id": new_id("fault"), "kind": kind, "remaining": times, "arg": arg}
            )

    async def _take_fault(self, merchant_id: str) -> tuple[str, int] | None:
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            for row in await repo.select(sim_rails_faults, sim_rails_faults.c.remaining > 0):
                await repo.update(
                    sim_rails_faults, {"remaining": row["remaining"] - 1}, sim_rails_faults.c.id == row["id"]
                )
                return str(row["kind"]), int(row["arg"])
        return None

    async def pay(
        self,
        merchant_id: str,
        *,
        payer_vpa: str,
        payer_name: str = "",
        token: str | None = None,
        amount_paise: int | None = None,
        outcome: str = "success",
        link_id: str | None = None,
        platform_offer_paise: int = 0,
    ) -> dict[str, Any]:
        """A customer pays: dynamic QR (token), payment link (link_id) or static QR (amount only)."""
        order_ref, mode = None, "upi_static"
        if token:
            merchant_id, order = await self.order_for_token(token)
            if order["status"] != "created" or order["expires_at"] <= iso_utc(self.clock.now()):
                raise CommandError("sim.qr_expired")
            order_ref, amount_paise, mode = order["order_ref"], order["amount_paise"], "upi_qr"
        elif link_id:
            mode = "upi_link"
        if not amount_paise:
            raise CommandError("sim.amount_required")
        utr = self._next_utr()
        fault = await self._take_fault(merchant_id)
        status = "pending" if outcome == "pending" or (fault and fault[0] == "delay") else outcome
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            await repo.insert(
                sim_rails_payments,
                {
                    "id": new_id("simpay"),
                    "utr": utr,
                    "order_ref": order_ref,
                    "mode": mode,
                    "amount_paise": amount_paise,
                    "payer_vpa": payer_vpa,
                    "payer_name": payer_name,
                    "status": status,
                    "platform_offer_paise": platform_offer_paise,
                    "created_at": iso_utc(self.clock.now()),
                },
            )
            if token:
                await repo.update(
                    sim_rails_orders,
                    {"status": "paid" if status == "success" else status},
                    sim_rails_orders.c.token == token,
                )
        event = {
            "event_id": "rails_" + utr + "_" + status,
            "status": status,
            "order_ref": order_ref,
            "link_id": link_id,
            "amount_paise": amount_paise,
            "utr": utr,
            "mode": mode,
            "payer_vpa": payer_vpa,
            "payer_name": payer_name,
            "platform_offer_paise": platform_offer_paise,
            "ts": iso_utc(self.clock.now()),
        }
        if fault and fault[0] == "wrong_amount":
            event["amount_paise"] = amount_paise + (fault[1] or 100)
        results = []
        if not (fault and fault[0] == "drop"):
            results.append(await self.deliver_rails(merchant_id, event))
            if fault and fault[0] == "duplicate":
                results.append(await self.deliver_rails(merchant_id, event))
        if fault and fault[0] == "delay" and outcome == "success":
            results.append(await self.complete(merchant_id, utr, "success"))
        return {
            "utr": utr,
            "status": status if not fault or fault[0] != "delay" else outcome,
            "fault": fault[0] if fault else None,
            "deliveries": results,
        }

    async def complete(self, merchant_id: str, utr: str, outcome: str) -> dict[str, Any]:
        """A pending payment resolves (PEX-1)."""
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            rows = await repo.select(sim_rails_payments, sim_rails_payments.c.utr == utr)
            if not rows:
                raise CommandError("sim.unknown_utr")
            row = rows[0]
            await repo.update(sim_rails_payments, {"status": outcome}, sim_rails_payments.c.utr == utr)
        event = {
            "event_id": "rails_" + utr + "_" + outcome,
            "status": outcome,
            "order_ref": row["order_ref"],
            "link_id": None,
            "amount_paise": row["amount_paise"],
            "utr": utr,
            "mode": row["mode"],
            "payer_vpa": row["payer_vpa"],
            "payer_name": row["payer_name"],
            "platform_offer_paise": row["platform_offer_paise"],
            "ts": iso_utc(self.clock.now()),
        }
        return await self.deliver_rails(merchant_id, event)

    async def redeliver(self, merchant_id: str, utr: str) -> dict[str, Any]:
        """Retry after a dropped webhook: replays the payment's latest state."""
        async with self.db.read() as conn:
            row = (
                await Repository(conn, merchant_id).select(
                    sim_rails_payments, sim_rails_payments.c.utr == utr
                )
            )[0]
        return await self.complete(merchant_id, utr, row["status"])

    async def deliver_rails(self, merchant_id: str, event: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps({"merchant_id": merchant_id, **event}).encode()
        return await self.ingest_rails(body, self.sign(body))

    async def ingest_rails(self, body: bytes, signature: str) -> dict[str, Any]:
        """Arth's `/webhooks/rails` ingress: verify, hash the VPA, drop untrusted payer names, submit."""
        event = self.verify(body, signature)
        merchant_id = event["merchant_id"]
        payer_ref = identity_value(merchant_id, "vpa", event["payer_vpa"])[1]  # Arth never stores the raw VPA
        key = event["event_id"]
        if event.get("link_id") and event["status"] == "success":
            async with self.db.read() as conn:
                links = await Repository(conn, merchant_id).select(
                    reminders, reminders.c.link_id == event["link_id"]
                )
            if links:
                return await self.bus.submit(
                    system(merchant_id),
                    "ledger.apply_verified_payment",
                    {
                        "account_id": links[0]["account_id"],
                        "amount_paise": event["amount_paise"],
                        "payment_ref": "upi_" + event["utr"],
                        "link_ref": event["link_id"],
                    },
                    key,
                    private={"payment_verified": True},
                )
        payload: dict[str, Any] = {
            "status": event["status"],
            "utr": event["utr"],
            "amount_paise": event["amount_paise"],
            "mode": event["mode"],
            "payer_ref": payer_ref,
        }
        if event.get("order_ref"):
            payload["order_ref"] = event["order_ref"]
        return await self.bus.submit(
            system(merchant_id), "treasury.rails_event", payload, key, private={"payment_verified": True}
        )

    async def settle(self, merchant_id: str, day: str) -> dict[str, Any]:
        """Nightly settlement batch: gross → fee, EDI, refunds → net (TRS-2)."""
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            if await repo.select(sim_rails_settlements, sim_rails_settlements.c.date == day):
                raise CommandError("sim.already_settled")
            todays = [
                r
                for r in await repo.select(
                    sim_rails_payments,
                    sim_rails_payments.c.status == "success",
                    sim_rails_payments.c.settled == 0,
                )
                if (parse_iso(r["created_at"]) + IST).date().isoformat() <= day
            ]
            gross = sum(r["amount_paise"] for r in todays)
            lines = [{"kind": "fee", "amount_paise": gross * FEE_BP // 10000}]
            edi = 0
            for loan in await repo.select(
                sim_lender_apps, sim_lender_apps.c.status == "disbursed", sim_lender_apps.c.days_left > 0
            ):
                edi += loan["edi_paise"]
                await repo.update(
                    sim_lender_apps, {"days_left": loan["days_left"] - 1}, sim_lender_apps.c.id == loan["id"]
                )
            if edi:
                lines.append({"kind": "edi", "amount_paise": min(edi, gross)})
            refunded = sum(
                r["amount_paise"]
                for r in await repo.select(sim_rails_refunds)
                if (parse_iso(r["created_at"]) + IST).date().isoformat() == day
            )
            if refunded:
                lines.append({"kind": "refund", "amount_paise": refunded})
            net = gross - sum(line["amount_paise"] for line in lines)
            for row in todays:
                await repo.update(sim_rails_payments, {"settled": 1}, sim_rails_payments.c.id == row["id"])
            await repo.insert(
                sim_rails_settlements,
                {
                    "id": new_id("simstl"),
                    "date": day,
                    "gross_paise": gross,
                    "net_paise": net,
                    "lines": json.dumps(lines),
                },
            )
        return await self.bus.submit(
            system(merchant_id),
            "treasury.record_settlement",
            {
                "external_ref": "stl-" + day,
                "date": day,
                "gross_paise": gross,
                "net_paise": net,
                "lines": lines,
                "utrs": [r["utr"] for r in todays],
            },
            "settle-" + day,
            private={"payment_verified": True},
        )

    # messaging -----------------------------------------------------------------------------------
    async def thread(
        self,
        merchant_id: str,
        persona_id: str,
        name: str,
        *,
        role: str = "customer",
        lang: str = "hi",
        phone: str | None = None,
        patron_id: str | None = None,
        supplier_id: str | None = None,
    ) -> dict[str, Any]:
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            rows = await repo.select(sim_threads, sim_threads.c.persona_id == persona_id)
            if rows:
                return rows[0]
            row = {
                "id": new_id("thread"),
                "persona_id": persona_id,
                "name": name,
                "role": role,
                "lang": lang,
                "phone": phone
                or "9"
                + hashlib.sha256(persona_id.encode())
                .hexdigest()[:9]
                .translate(str.maketrans("abcdef", "012345")),
                "patron_id": patron_id,
                "supplier_id": supplier_id,
            }
            await repo.insert(sim_threads, row)
            return {**row, "merchant_id": merchant_id}

    async def send(
        self,
        merchant_id: str,
        thread_id: str,
        category: str,
        kind: str,
        body: dict[str, Any],
        source_ref: str | None = None,
    ) -> dict[str, Any]:
        """Cloud-API-shaped outbound (text, buttons, image, document, template) with the network's own cap."""
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            if source_ref and await repo.select(sim_messages, sim_messages.c.source_ref == source_ref):
                return {"status": "duplicate"}
            if category == "marketing":
                since = iso_utc(self.clock.now() - timedelta(days=7))
                recent = [
                    m
                    for m in await repo.select(
                        sim_messages,
                        sim_messages.c.thread_id == thread_id,
                        sim_messages.c.category == "marketing",
                        sim_messages.c.direction == "out",
                    )
                    if m["created_at"] > since
                ]
                if len(recent) >= MARKETING_CAP_PER_WEEK:
                    return {"status": "rejected_cap"}
            identity = new_id("msg")
            await repo.insert(
                sim_messages,
                {
                    "id": identity,
                    "thread_id": thread_id,
                    "direction": "out",
                    "category": category,
                    "kind": kind,
                    "body": json.dumps(body),
                    "source_ref": source_ref,
                    "created_at": iso_utc(self.clock.now()),
                },
            )
        return {"status": "delivered", "message_id": identity}

    async def inbound(
        self, merchant_id: str, persona_id: str, text: str, kind: str = "text"
    ) -> dict[str, Any]:
        """A persona writes to the shop; delivered to Arth as a signed `/webhooks/messages` call."""
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            thread = (await repo.select(sim_threads, sim_threads.c.persona_id == persona_id))[0]
            identity = new_id("msg")
            await repo.insert(
                sim_messages,
                {
                    "id": identity,
                    "thread_id": thread["id"],
                    "direction": "in",
                    "category": "service",
                    "kind": kind,
                    "body": json.dumps({"text": text}),
                    "source_ref": None,
                    "created_at": iso_utc(self.clock.now()),
                },
            )
        body = json.dumps(
            {
                "merchant_id": merchant_id,
                "message_id": identity,
                "thread_ref": thread["id"],
                "persona_ref": persona_id,
                "patron_id": thread["patron_id"],
                "supplier_id": thread["supplier_id"],
                "kind": kind,
                "text": text,
            }
        ).encode()
        return await self.ingest_message(body, self.sign(body))

    async def ingest_message(self, body: bytes, signature: str) -> dict[str, Any]:
        event = self.verify(body, signature)
        payload = {k: event[k] for k in ("thread_ref", "persona_ref", "kind", "text")}
        for key in ("patron_id", "supplier_id"):
            if event.get(key):
                payload[key] = event[key]
        return await self.bus.submit(
            system(event["merchant_id"]),
            "messages.receive",
            payload,
            "msg-" + event["message_id"],
            private={"message_verified": True},
        )

    async def threads(self, merchant_id: str) -> list[dict[str, Any]]:
        async with self.db.read() as conn:
            repo = Repository(conn, merchant_id)
            result = []
            for thread in await repo.select(sim_threads):
                messages = sorted(
                    await repo.select(sim_messages, sim_messages.c.thread_id == thread["id"]),
                    key=lambda r: r["created_at"],
                )
                result.append(
                    {
                        **{
                            k: thread[k]
                            for k in ("id", "persona_id", "name", "role", "lang", "patron_id", "supplier_id")
                        },
                        "messages": [
                            {k: m[k] for k in ("id", "direction", "category", "kind", "created_at")}
                            | {"body": json.loads(m["body"])}
                            for m in messages
                        ],
                    }
                )
            return result

    # lender --------------------------------------------------------------------------------------
    async def lender_offers(
        self, merchant_id: str, need_paise: int, purpose_ref: str | None = None
    ) -> list[str]:
        """Pre-qualified offers around the need: smaller, exact and larger (CAP-4 fields)."""
        ids = []
        for i, (factor, tenor, apr) in enumerate([(0.6, 60, 2200), (1.0, 90, 2400), (1.6, 180, 2600)]):
            amount = max(int(need_paise * factor) // 100 * 100, 100000)
            total = amount + amount * apr * tenor // (10000 * 365)
            payload = {
                "lender": ["Sandbox Finance", "Kirana Credit NBFC", "Udyam Capital"][i],
                "amount_paise": amount,
                "tenor_days": tenor,
                "apr_bp": apr,
                "edi_paise": -(-total // tenor),
                "processing_fee_paise": amount // 100,
                "kfs_url": f"https://lender.sim/kfs/{i}",
                "cooling_off_days": 3,
                "expires_at": iso_utc(self.clock.now() + timedelta(days=7)),
            }
            if purpose_ref:
                payload["purpose_ref"] = purpose_ref
            result = await self.bus.submit(
                system(merchant_id),
                "capital.record_offer",
                payload,
                f"offer-{purpose_ref}-{need_paise}-{i}",
                private={"lender_verified": True},
            )
            ids.append(result["data"]["offer_id"])
        return ids

    # consumers: what the outside world does after Arth's events ----------------------------------
    async def _consume(self, repo: Repository, event: dict[str, Any]) -> None:
        topic, payload = event["type"], event["payload"]
        now = iso_utc(self.clock.now())
        if topic == "offer.cashback_requested":
            if not await repo.select(
                sim_rails_cashbacks,
                sim_rails_cashbacks.c.payment_ref == payload["payment_id"],
                sim_rails_cashbacks.c.program_ref == payload["issuance_id"],
            ):
                await repo.insert(
                    sim_rails_cashbacks,
                    {
                        "id": new_id("simcb"),
                        "payment_ref": payload["payment_id"],
                        "program_ref": payload["issuance_id"],
                        "amount_paise": payload["amount_paise"],
                        "funding": payload["funding"],
                        "created_at": now,
                    },
                )
        elif topic == "payment.refunded":
            if not await repo.select(
                sim_rails_refunds, sim_rails_refunds.c.refund_ref == payload["refund_id"]
            ):
                await repo.insert(
                    sim_rails_refunds,
                    {
                        "id": new_id("simref"),
                        "refund_ref": payload["refund_id"],
                        "amount_paise": payload["amount_paise"],
                        "created_at": now,
                    },
                )
        elif topic == "capital.applied":
            from arth.domains.commerce_tables import loan_offers

            offer = (await repo.select(loan_offers, loan_offers.c.id == payload["offer_id"]))[0]
            if not await repo.select(sim_lender_apps, sim_lender_apps.c.offer_id == offer["id"]):
                await repo.insert(
                    sim_lender_apps,
                    {
                        "id": new_id("simloan"),
                        "offer_id": offer["id"],
                        "status": "disbursed",
                        "principal_paise": offer["amount_paise"],
                        "edi_paise": offer["edi_paise"],
                        "days_left": offer["tenor_days"],
                        "created_at": now,
                    },
                )
        elif topic == "message.out":
            if not await repo.select(sim_messages, sim_messages.c.source_ref == event["event_id"]):
                await repo.insert(
                    sim_messages,
                    {
                        "id": new_id("msg"),
                        "thread_id": payload["thread_ref"],
                        "direction": "out",
                        "category": payload["category"],
                        "kind": "template",
                        "body": json.dumps({"template": payload["template"], "params": payload["params"]}),
                        "source_ref": event["event_id"],
                        "created_at": now,
                    },
                )
        else:
            await self._deliver_outbound(repo, topic, payload, event["event_id"], now)

    async def _deliver_outbound(
        self, repo: Repository, topic: str, payload: dict[str, Any], ref: str, now: str
    ) -> None:
        from arth.domains.commerce_tables import claims, orders, purchase_orders
        from arth.domains.ledger_tables import credit_accounts

        thread, category, body = None, "utility", {}
        if topic in {"credit.reminder_requested", "credit.statement_requested", "credit.receipt_requested"}:
            if topic == "credit.reminder_requested":
                rows = await repo.select(reminders, reminders.c.id == payload["reminder_id"])
                patron = rows[0]["patron_id"] if rows else None
                body = {
                    "template": "khata_reminder",
                    "link_id": rows[0]["link_id"] if rows else None,
                    "balance_paise": rows[0]["balance_paise"] if rows else 0,
                }
            else:
                accounts = await repo.select(credit_accounts, credit_accounts.c.id == payload["account_id"])
                patron = accounts[0]["patron_id"] if accounts else None
                body = {
                    "template": topic.split(".")[1].replace("_requested", ""),
                    "account_id": payload["account_id"],
                }
            thread = await self._thread_for(repo, patron_id=patron)
        elif topic == "po.changed" and payload.get("status") in {"sent", "claim_sent"}:
            if payload["status"] == "sent":
                po = await repo.select(purchase_orders, purchase_orders.c.id == payload["po_id"])
                supplier = po[0]["supplier_id"] if po else None
                body = {"template": "purchase_order", "po_id": payload["po_id"], "document": "po.pdf"}
            else:
                claim = await repo.select(claims, claims.c.po_id == payload["po_id"])
                supplier = claim[0]["supplier_id"] if claim else None
                body = {
                    "template": "variance_claim",
                    "po_id": payload["po_id"],
                    "amount_paise": claim[0]["amount_paise"] if claim else 0,
                }
            thread = await self._thread_for(repo, supplier_id=supplier)
        elif topic == "order.changed" and payload.get("status") == "accepted":
            order = await repo.select(orders, orders.c.id == payload["order_id"])
            thread = await self._thread_for(repo, patron_id=order[0]["patron_id"] if order else None)
            body = {
                "template": "order_accepted",
                "order_id": payload["order_id"],
                "total_paise": order[0]["total_paise"] if order else 0,
            }
        if thread is None:
            return
        if not await repo.select(sim_messages, sim_messages.c.source_ref == ref):
            await repo.insert(
                sim_messages,
                {
                    "id": new_id("msg"),
                    "thread_id": thread["id"],
                    "direction": "out",
                    "category": category,
                    "kind": "template",
                    "body": json.dumps(body),
                    "source_ref": ref,
                    "created_at": now,
                },
            )

    async def _thread_for(
        self, repo: Repository, *, patron_id: str | None = None, supplier_id: str | None = None
    ) -> dict[str, Any] | None:
        if patron_id:
            rows = await repo.select(sim_threads, sim_threads.c.patron_id == patron_id)
        elif supplier_id:
            rows = await repo.select(sim_threads, sim_threads.c.supplier_id == supplier_id)
        else:
            return None
        return rows[0] if rows else None
