"""Normal-mode flow check: drives billing, khata (udhaar lending), catalog, stock and capital through the live
API exactly as the surfaces do (POST /v1/commands, approvals, GET views) and checks every read model moved.

    python -m arth.tools.flow_check [--api http://localhost:8000]

Needs a running API with one seeded shop (the Director's presenter session picks it). Exits 1 on any failure.
"""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from typing import Any

import httpx


class Flow:
    def __init__(self, api: str) -> None:
        self.http = httpx.Client(base_url=api, timeout=60)
        director = {"Authorization": "Bearer dev-director"}
        token = self.http.post("/v1/director/session", json={"surface": "device"}, headers=director)
        token.raise_for_status()
        self.auth = {"Authorization": f"Bearer {token.json()['token']}"}
        self.failures: list[str] = []

    # plumbing -------------------------------------------------------------------------------------
    def view(self, path: str) -> Any:
        res = self.http.get(f"/v1/views/{path}", headers=self.auth)
        if res.status_code >= 400:
            raise AssertionError(f"GET {path} -> {res.status_code} {res.text[:200]}")
        return res.json()

    def run(self, type_: str, payload: dict[str, Any], approve: bool = True) -> dict[str, Any]:
        """Submit like the device: R2/R3 answers need_approval and the owner says haan; R1 queues for the
        undo window, so wait it out until the command executed."""
        key = {"Idempotency-Key": uuid.uuid4().hex}
        res = self.http.post(
            "/v1/commands", json={"type": type_, "payload": payload}, headers=self.auth | key
        )
        if res.status_code >= 400:
            raise AssertionError(f"{type_} -> {res.status_code} {res.text[:240]}")
        body: dict[str, Any] = res.json()
        if body["status"] == "needs_approval" and approve:
            key = {"Idempotency-Key": uuid.uuid4().hex}
            res = self.http.post(
                f"/v1/approvals/{body['thread_id']}", json={"decision": "approve"}, headers=self.auth | key
            )
            if res.status_code >= 400:
                raise AssertionError(f"approve {type_} -> {res.status_code} {res.text[:240]}")
            body = res.json()
        if body["status"] == "queued":
            body = self.await_queued(type_, body)
        return body

    def await_queued(self, type_: str, body: dict[str, Any]) -> dict[str, Any]:
        """An R1 command executes once the sim clock passes its undo window (the tick loop runs it)."""
        due = body["due_at"].replace("Z", "+00:00")
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            clock = self.http.get("/healthz").json()["clock"].replace("Z", "+00:00")
            if clock > due:
                time.sleep(2)  # one tick for run_due
                return body
            time.sleep(1.5)
        raise AssertionError(f"{type_} stayed queued past its undo window: the sim clock is not running")

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        """Gateway routes (patrons, staff) keep PII and PINs out of the command log."""
        res = self.http.post(path, json=body, headers=self.auth | {"Idempotency-Key": uuid.uuid4().hex})
        if res.status_code >= 400:
            raise AssertionError(f"POST {path} -> {res.status_code} {res.text[:240]}")
        return dict(res.json())

    def check(self, name: str, fn: Any) -> None:
        try:
            fn()
            print(f"ok    {name}")
        except Exception as exc:  # report every flow, not just the first failure
            self.failures.append(f"{name}: {exc}")
            print(f"FAIL  {name}: {exc}")

    # flows ----------------------------------------------------------------------------------------
    def sellable(self) -> list[dict[str, Any]]:
        return [i for i in self.view("stock")["items"] if i["sellable_qty_milli"] >= 3000]

    def price(self, item_id: str) -> int:
        return int(self.view(f"item/{item_id}")["price_paise"])

    def new_bill(self) -> str:
        return str(self.run("counter.open_bill", {})["data"]["bill_id"])

    def billing(self) -> None:
        a, b = self.sellable()[:2]
        before = {i["item_id"]: i["on_hand_qty_milli"] for i in self.view("stock")["items"]}
        bill = self.new_bill()
        lines = [
            {"item_id": a["item_id"], "qty_milli": 1000, "added_via": "tap"},
            {"item_id": b["item_id"], "qty_milli": 2000, "added_via": "tap"},
        ]
        self.run("counter.add_lines", {"bill_id": bill, "lines": lines})
        state = self.view(f"bill/{bill}")["bill"]
        assert len(state["lines"]) == 2 and state["total_paise"] > 0, state

        def line(item_id: str) -> dict[str, Any]:  # lines are append-only: a qty change is a new line
            return next(ln for ln in self.view(f"bill/{bill}")["bill"]["lines"] if ln["item_id"] == item_id)

        self.run("counter.set_qty", {"bill_id": bill, "line_id": line(a["item_id"])["id"], "qty_milli": 3000})
        assert line(a["item_id"])["qty_milli"] == 3000
        self.run("counter.remove_line", {"bill_id": bill, "line_id": line(b["item_id"])["id"]})
        state = self.view(f"bill/{bill}")["bill"]
        assert [ln["item_id"] for ln in state["lines"]] == [a["item_id"]], state["lines"]
        first = line(a["item_id"])
        total = state["total_paise"]
        self.run("counter.park", {"bill_id": bill})
        assert bill in [p["id"] for p in self.view("park")["bills"]], "parked bill missing from park view"
        self.run("counter.resume", {"bill_id": bill})
        self.run("counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": total}]})
        paid = self.view(f"bill/{bill}/paid")
        assert paid["bill"]["status"] == "closed", paid["bill"]["status"]
        after = {i["item_id"]: i["on_hand_qty_milli"] for i in self.view("stock")["items"]}
        assert after[a["item_id"]] == before[a["item_id"]] - 3000, (before[a["item_id"]], after[a["item_id"]])
        assert after[b["item_id"]] == before[b["item_id"]], "removed line still issued stock"
        self.returned = (bill, first["id"], a["item_id"], after[a["item_id"]])

    def returns(self) -> None:
        bill, line, item, on_hand = self.returned
        self.run(
            "counter.return",
            {
                "bill_id": bill,
                "lines": [{"line_id": line, "qty_milli": 1000}],
                "reason_key": "return.changed_mind",
                "refund_mode": "cash",
            },
        )
        stock = {i["item_id"]: i["on_hand_qty_milli"] for i in self.view("stock")["items"]}
        assert stock[item] == on_hand + 1000, (on_hand, stock[item])

    def void(self) -> None:
        bill = self.new_bill()
        item = self.sellable()[0]
        self.run(
            "counter.add_lines",
            {"bill_id": bill, "lines": [{"item_id": item["item_id"], "qty_milli": 1000, "added_via": "tap"}]},
        )
        self.run("counter.void_bill", {"bill_id": bill, "reason_key": "void.customer_left"})
        assert self.view(f"bill/{bill}")["bill"]["status"] == "voided"

    def upi(self) -> None:
        bill = self.new_bill()
        item = self.sellable()[0]
        self.run(
            "counter.add_lines",
            {"bill_id": bill, "lines": [{"item_id": item["item_id"], "qty_milli": 1000, "added_via": "tap"}]},
        )
        self.run("counter.request_upi", {"bill_id": bill})
        token = self.view(f"bill/{bill}/pay")["pay_token"]
        assert token, "no dynamic QR token on the pay view"
        res = self.http.post(f"/sim/pay/{token}", json={"outcome": "success", "payer_vpa": "flow@okbank"})
        assert res.status_code == 200, res.text[:200]
        deadline = time.monotonic() + 30
        while self.view(f"bill/{bill}")["bill"]["status"] != "closed":
            assert time.monotonic() < deadline, "UPI payment never closed the bill"
            time.sleep(1)

    def khata(self) -> None:
        accounts = [
            a for a in self.view("khata")["accounts"] if a["limit_paise"] - a["balance_paise"] > 20000
        ]
        assert accounts, "no khata account with headroom"
        account = accounts[0]
        start = account["balance_paise"]
        item = self.sellable()[0]
        bill = self.new_bill()
        self.run(
            "counter.add_lines",
            {"bill_id": bill, "lines": [{"item_id": item["item_id"], "qty_milli": 1000, "added_via": "tap"}]},
        )
        total = self.view(f"bill/{bill}")["bill"]["total_paise"]
        self.run(
            "counter.checkout_khata",
            {"bill_id": bill, "account_id": account["account_id"], "khata_paise": total, "payments": []},
        )
        balance = self.view(f"khata/{account['patron_id']}")["balance_paise"]
        assert balance == start + total, (start, total, balance)
        self.run(
            "ledger.record_payment",
            {
                "account_id": account["account_id"],
                "amount_paise": total,
                "payment_ref": f"payment_{uuid.uuid4().hex[:26].upper()}",
                "mode": "cash",
            },
        )
        assert self.view(f"khata/{account['patron_id']}")["balance_paise"] == start, "payment not allocated"
        self.khata_account = account

    def promise_and_reverse(self) -> None:
        account = self.khata_account
        item = self.sellable()[0]
        price = self.price(item["item_id"])
        entry = self.run(
            "ledger.add_entry",
            {
                "account_id": account["account_id"],
                "amount_paise": price,
                "lines": [{"item_id": item["item_id"], "qty_milli": 1000, "unit_price_paise": price}],
                "source": "voice",
            },
        )["data"]["entry_id"]
        view = self.view(f"khata/{account['patron_id']}")
        self.run("ledger.reverse_entry", {"entry_id": entry, "reason_key": "ledger.wrong_entry"})
        assert self.view(f"khata/{account['patron_id']}")["balance_paise"] == view["balance_paise"] - price

    def catalog_and_stock(self) -> None:
        sku = "FLOW-" + uuid.uuid4().hex[:6].upper()
        item = self.run(
            "catalog.add_item",
            {
                "sku": sku,
                "names": {"en": "Flow Check Biscuit", "hi-Latn": "Flow biscuit"},
                "unit": "pcs",
                "mrp_paise": 2000,
                "price_paise": 1800,
                "cost_paise": 1500,
                "category": "snacks",
            },
        )["data"]["item_id"]
        self.run("catalog.change_price", {"item_id": item, "price_paise": 1900})
        self.run("stock.receive", {"item_id": item, "qty_milli": 10000})
        self.run("stock.adjust", {"item_id": item, "delta_qty_milli": -2000, "reason": "stock.damaged"})
        row = [i for i in self.view("stock")["items"] if i["item_id"] == item]
        assert row and row[0]["on_hand_qty_milli"] == 8000, row
        assert self.view(f"item/{item}")["price_paise"] == 1900

    def capital(self) -> None:
        view = self.view("capital")
        assert "offers" in view or "profile" in view, list(view)
        # CAP-5: applying for a loan is R4, Console + OTP only; the device must be refused
        res = self.http.post(
            "/v1/commands",
            json={"type": "capital.apply", "payload": {"offer_id": "capoffer_01K8S08QNP0000000000000000"}},
            headers=self.auth | {"Idempotency-Key": uuid.uuid4().hex},
        )
        assert res.status_code >= 400, "capital.apply ran from the device"

    def now(self) -> str:
        return str(self.http.get("/healthz").json()["clock"])

    def supply(self) -> None:
        supplier = self.view("suppliers")["suppliers"][0]
        item = self.sellable()[0]
        po = self.run(
            "supply.draft_po",
            {
                "supplier_id": supplier["id"],
                "lines": [{"item_id": item["item_id"], "qty_milli": 5000, "unit_price_paise": 1000}],
            },
        )["data"]["po_id"]
        self.run("supply.place_po", {"po_id": po})
        self.run("supply.confirm_po", {"po_id": po})
        before = {i["item_id"]: i["on_hand_qty_milli"] for i in self.view("stock")["items"]}
        self.run("supply.receive", {"po_id": po, "lines": [{"item_id": item["item_id"], "qty_milli": 4000}]})
        after = {i["item_id"]: i["on_hand_qty_milli"] for i in self.view("stock")["items"]}
        assert after[item["item_id"]] == before[item["item_id"]] + 4000, "GRN did not receive stock"
        assert self.view(f"grn/{po}"), "no GRN view"

    def offers(self) -> None:
        now = self.now()
        program = (
            self.run(
                "offers.create_program",
                {
                    "type": "next_txn_cashback",
                    "rules": {"reward_paise": 1000, "min_spend_paise": 10000, "validity_days": 7},
                    "terms": {"amount_paise": 1000, "min_spend_paise": 10000, "expiry_days": 7},
                    "budget_paise": 50000,
                    "funding": "merchant",
                    "holdout_bp": 2000,  # policies.growth.holdout_share 0.2
                    "valid_from": now,
                    "valid_until": now[:4] + "-12-31T18:29:59Z",
                },
            )
            .get("data", {})
            .get("program_id")
            or self.view("latest/offer")["id"]
        )  # R3: queued, no data
        assert program in [p["id"] for p in self.view("offers")["programs"]]
        self.run("offers.pause_program", {"program_id": program})
        assert self.view(f"offers/{program}")["program"]["status"] == "paused"

    def orders(self) -> None:
        item = self.sellable()[0]
        line = {"item_id": item["item_id"], "text": "flow", "qty_milli": 1000, "confidence_bp": 10000}
        order = self.run("orders.create_draft", {"channel": "device", "lines": [line]})["data"]["order_id"]
        self.run("orders.place", {"order_id": order})
        self.run("orders.accept", {"order_id": order})
        self.run("orders.advance", {"order_id": order, "to": "packed"})
        self.run("orders.advance", {"order_id": order, "to": "delivered"})
        self.run("orders.settle", {"order_id": order, "mode": "paid"})
        assert order in [o["id"] for o in self.view("orders")["orders"]]
        self.view(f"orders/{order}")

    def treasury_and_books(self) -> None:
        before = len(self.view("hisaab")["expenses"])
        self.run("treasury.expense", {"category": "transport", "amount_paise": 5000, "paid_from": "cash"})
        assert len(self.view("hisaab")["expenses"]) == before + 1, "expense not on hisaab"
        assert self.view("reports"), "no reports view"

    def patrons(self) -> None:
        body = {"display_name": "Flow Check Ji", "lang": "hi-Latn", "identities": []}
        patron = self.post("/v1/patrons", body)["data"]["patron_id"]
        self.http.patch(
            "/v1/patrons",
            json={"patron_id": patron, "display_name": "Flow Check Sharma"},
            headers=self.auth | {"Idempotency-Key": uuid.uuid4().hex},
        ).raise_for_status()
        view = self.view(f"patron/{patron}")
        name = view.get("display_name") or view.get("patron", {}).get("display_name")
        assert name == "Flow Check Sharma", view
        self.patron = patron

    def storefront_feedback_privacy(self) -> None:
        store = self.view("storefront")
        public = self.http.get(f"/v1/public/storefront/{store['slug']}")
        assert public.status_code == 200 and public.json(), public.text[:200]
        self.run("feedback.record", {"target_kind": "bill", "target_id": self.returned[0], "rating": 4})
        assert self.view("feedback"), "no feedback view"
        export = self.http.get(f"/v1/privacy/patrons/{self.patron}/export", headers=self.auth)
        assert export.status_code == 200, export.text[:200]

    def staff(self) -> None:
        self.post(
            "/v1/staff", {"name": "Flow Helper", "role": "helper", "pin": "2580"}
        )  # PIN never in the log
        names = [s["name"] for s in self.view("settings/staff")["staff"]]
        assert "Flow Helper" in names, names

    def agents_and_growth(self) -> None:
        team = self.view("team")
        assert team["helpers"], "no helpers on the Team screen"
        helper = team["helpers"][0]
        agent = helper.get("agent") or helper.get("id")
        self.run("agents.pause", {"agent": agent, "paused": True})
        self.run("agents.pause", {"agent": agent, "paused": False})
        grow = self.view("grow")
        assert "levers" in grow and "diagnostics" in grow, list(grow)
        assert self.view("insights"), "no insights"
        assert self.view("forecast"), "no forecast"
        assert self.view("home")["brief"] is not None, "Night Shift brief missing on Aaj"

    def ai_turn(self) -> None:
        for text in ("Aaj kitna aaya?", "Kal ke liye kya order karna chahiye aur kyun?"):
            res = self.http.post(
                "/v1/turns",
                json={"text": text, "surface": "device"},
                headers=self.auth | {"Idempotency-Key": uuid.uuid4().hex},
            )
            assert res.status_code == 200, res.text[:300]
            body = res.json()
            print(f"      turn {text!r}: {str(body.get('speech') or body.get('text') or list(body))[:160]}")

    def audit(self) -> None:
        res = self.http.get("/v1/audit/verify", headers=self.auth).json()
        assert res.get("ok", res.get("valid")) is True, res


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--api", default="http://localhost:8000")
    flow = Flow(parser.parse_args().api)
    flow.check("billing: open, add, set qty, remove, park, resume, cash checkout, stock issued", flow.billing)
    flow.check("billing: return a line, stock back", flow.returns)
    flow.check("billing: void bill", flow.void)
    flow.check("billing: UPI QR paid through the rails simulator", flow.upi)
    flow.check("khata: checkout on credit, cash payment allocated", flow.khata)
    flow.check("khata: voice entry then reversal", flow.promise_and_reverse)
    flow.check("catalog + stock: add item, change price, receive, adjust", flow.catalog_and_stock)
    flow.check("capital: view; loan apply refused on the device (R4 Console only)", flow.capital)
    flow.check("supply: draft, place, confirm PO, receive GRN, stock up", flow.supply)
    flow.check("offers: create program, pause", flow.offers)
    flow.check("orders: draft, accept, pack, deliver, settle", flow.orders)
    flow.check("treasury + books: expense on hisaab, reports", flow.treasury_and_books)
    flow.check("patrons: add, rename", flow.patrons)
    flow.check("storefront public page, feedback, privacy export", flow.storefront_feedback_privacy)
    flow.check("staff: add helper", flow.staff)
    flow.check(
        "agents + growth + intel: pause/resume, grow, insights, forecast, brief", flow.agents_and_growth
    )
    flow.check("AI turns (live LLM)", flow.ai_turn)
    flow.check("audit chain verifies", flow.audit)
    print(f"\n{'FLOW FAILED' if flow.failures else 'FLOW GREEN'} ({len(flow.failures)} failures)")
    return 1 if flow.failures else 0


if __name__ == "__main__":
    sys.exit(main())
