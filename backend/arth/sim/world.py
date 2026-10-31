"""World generator (T2.7, T2.8): a seeded, consistent shop history for any pack, written through the
Command Bus so every invariant and the audit chain hold. Returns a manifest of planted facts.

All randomness comes from `random.Random(seed)`; the manifest carries a hash of the key outputs.
"""

import hashlib
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any

from arth.core.clock import IST, iso_utc
from arth.core.ids import new_id
from arth.core.paths import PACKS_DIR
from arth.domains.catalog import get_item, read_starter
from arth.domains.counter import bill_state
from arth.domains.ledger_projection import statement
from arth.domains.merchants import provision_shop
from arth.domains.patron_identity import identity_value
from arth.domains.patrons import PatronService
from arth.domains.stock import stock_view
from arth.governance.commands import CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.sim.forge import screenshot
from arth.sim.hub import Simulators

NAMES = [
    "Priya Verma",
    "Rakesh Sharma",
    "Anita Mehta",
    "Rohit Kumar",
    "Sunita Devi",
    "Imran Khan",
    "Kavita Joshi",
    "Suresh Yadav",
    "Meena Gupta",
    "Arjun Nair",
    "Pooja Singh",
    "Vikram Rao",
    "Farah Sheikh",
    "Deepak Mishra",
    "Lakshmi Iyer",
    "Manoj Tiwari",
    "Neha Agarwal",
    "Sanjay Patel",
    "Ritu Saxena",
    "Ajay Chauhan",
    "Geeta Rani",
    "Harish Pandey",
    "Shabnam Ali",
    "Nitin Jain",
    "Rekha Das",
    "Gopal Krishnan",
    "Asha Bhatt",
    "Karan Malhotra",
    "Zoya Hussain",
    "Ramesh Pal",
    "Usha Kulkarni",
    "Tarun Bose",
    "Divya Menon",
    "Mohan Lal",
    "Seema Kapoor",
    "Firoz Ahmed",
    "Jyoti Sinha",
    "Prakash Reddy",
    "Anjali Ghosh",
    "Bhavesh Shah",
]
LANGS = ["hi", "hi", "hi-Latn", "hi-Latn", "en", "mr", "ta", "bn", "gu", "te"]
SIZE = {"micro": 8, "small": 18, "medium": 32}
PACK_ITEMS: dict[str, list[dict[str, Any]]] = {
    "kirana": [
        {
            "sku": "SUGAR-LOOSE",
            "names": {"en": "Sugar (loose)", "hi-Latn": "Khuli cheeni"},
            "unit": "kg",
            "mrp_paise": 5000,
            "price_paise": 4500,
            "cost_paise": 4000,
            "category": "staples",
            "hsn": "1701",
            "gst_rate_bp": 500,
        },
        {
            "sku": "TOOR-LOOSE",
            "names": {"en": "Toor dal (loose)", "hi-Latn": "Khuli arhar dal"},
            "unit": "kg",
            "mrp_paise": 16000,
            "price_paise": 15000,
            "cost_paise": 13000,
            "category": "staples",
            "hsn": "0713",
            "gst_rate_bp": 0,
        },
    ],
    "cafe": [
        {
            "sku": "MILK",
            "names": {"en": "Milk"},
            "unit": "ml",
            "mrp_paise": 6,
            "price_paise": 6,
            "cost_paise": 5,
            "category": "ingredient",
        },
        {
            "sku": "CHAI",
            "names": {"en": "Masala chai", "hi-Latn": "Masala chai"},
            "unit": "cup",
            "mrp_paise": 2000,
            "price_paise": 2000,
            "cost_paise": 600,
            "category": "tea",
            "hsn": "9963",
            "gst_rate_bp": 500,
            "modifier_groups": [
                {
                    "name": "Size",
                    "required": True,
                    "options": [
                        {"name": "Regular", "delta_paise": 0},
                        {"name": "Large", "delta_paise": 1000},
                    ],
                }
            ],
        },
        {
            "sku": "COFFEE",
            "names": {"en": "Filter coffee"},
            "unit": "cup",
            "mrp_paise": 3000,
            "price_paise": 3000,
            "cost_paise": 900,
            "category": "coffee",
            "hsn": "9963",
            "gst_rate_bp": 500,
        },
        {
            "sku": "SAMOSA",
            "names": {"en": "Samosa"},
            "unit": "plate",
            "mrp_paise": 2500,
            "price_paise": 2500,
            "cost_paise": 1000,
            "category": "snacks",
            "hsn": "9963",
            "gst_rate_bp": 500,
        },
        {
            "sku": "POHA",
            "names": {"en": "Poha"},
            "unit": "plate",
            "mrp_paise": 4000,
            "price_paise": 4000,
            "cost_paise": 1500,
            "category": "breakfast",
            "hsn": "9963",
            "gst_rate_bp": 500,
        },
    ],
    "pharmacy": [
        {
            "sku": "PARA",
            "names": {"en": "Paracetamol 500"},
            "unit": "strip",
            "mrp_paise": 3500,
            "price_paise": 3000,
            "cost_paise": 2000,
            "category": "otc",
            "hsn": "3004",
            "gst_rate_bp": 1200,
            "details": {
                "salt": "paracetamol",
                "strength": "500mg",
                "form": "tablet",
                "pack_size": "10",
                "schedule": "otc",
                "rx_required": False,
            },
        },
        {
            "sku": "ORS",
            "names": {"en": "ORS sachet"},
            "unit": "pcs",
            "mrp_paise": 2200,
            "price_paise": 2200,
            "cost_paise": 1500,
            "category": "otc",
            "hsn": "3004",
            "gst_rate_bp": 1200,
            "details": {
                "salt": "oral rehydration salts",
                "strength": "21g",
                "form": "powder",
                "pack_size": "1",
                "schedule": "otc",
                "rx_required": False,
            },
        },
        {
            "sku": "AMOX",
            "names": {"en": "Amoxicillin 250"},
            "unit": "strip",
            "mrp_paise": 9000,
            "price_paise": 9000,
            "cost_paise": 6000,
            "category": "antibiotic",
            "hsn": "3004",
            "gst_rate_bp": 1200,
            "details": {
                "salt": "amoxicillin",
                "strength": "250mg",
                "form": "capsule",
                "pack_size": "10",
                "schedule": "H",
                "rx_required": True,
            },
        },
        {
            "sku": "METF",
            "names": {"en": "Metformin 500"},
            "unit": "strip",
            "mrp_paise": 4500,
            "price_paise": 4500,
            "cost_paise": 3000,
            "category": "chronic",
            "hsn": "3004",
            "gst_rate_bp": 1200,
            "details": {
                "salt": "metformin",
                "strength": "500mg",
                "form": "tablet",
                "pack_size": "10",
                "schedule": "H",
                "rx_required": True,
            },
        },
    ],
    "salon": [
        {
            "sku": "HAIRCUT",
            "names": {"en": "Haircut"},
            "unit": "service",
            "mrp_paise": 20000,
            "price_paise": 20000,
            "cost_paise": 0,
            "category": "hair",
            "hsn": "9997",
            "gst_rate_bp": 1800,
            "details": {"duration_minutes": 30, "required_skill": "hair"},
        },
        {
            "sku": "FACIAL",
            "names": {"en": "Facial"},
            "unit": "service",
            "mrp_paise": 60000,
            "price_paise": 60000,
            "cost_paise": 15000,
            "category": "skin",
            "hsn": "9997",
            "gst_rate_bp": 1800,
            "details": {"duration_minutes": 60, "required_skill": "skin"},
        },
        {
            "sku": "SHAVE",
            "names": {"en": "Shave"},
            "unit": "service",
            "mrp_paise": 8000,
            "price_paise": 8000,
            "cost_paise": 0,
            "category": "hair",
            "hsn": "9997",
            "gst_rate_bp": 1800,
            "details": {"duration_minutes": 15, "required_skill": "hair"},
        },
    ],
}


@dataclass
class WorldSpec:
    pack: str = "kirana"
    days: int = 30
    seed: int = 1
    size: str = "small"
    name: str | None = None
    key: str | None = None
    patrons: int = 30
    planted: dict[str, Any] = field(default_factory=dict)


class WorldBuilder:
    def __init__(self, sim: Simulators, patrons: PatronService, spec: WorldSpec) -> None:
        self.sim, self.bus, self.patron_service, self.spec = sim, sim.bus, patrons, spec
        self.rng = random.Random(f"{spec.pack}:{spec.seed}")
        self.counter = 0
        self.manifest: dict[str, Any] = {
            "pack": spec.pack,
            "days": spec.days,
            "seed": spec.seed,
            "planted": {},
        }

    def key(self, label: str) -> str:
        self.counter += 1
        return f"world-{self.spec.key}-{label}-{self.counter}"

    async def run(self, kind: str, payload: dict[str, Any], *, approve: bool = True) -> dict[str, Any]:
        result = await self.bus.submit(self.owner, kind, payload, self.key(kind))
        if result["status"] == "needs_approval" and approve:
            result = await self.bus.decide(self.owner, result["thread_id"], "approve", self.key("ok"))
            if result["status"] == "queued":
                self.bus.clock.set(self.bus.clock.now() + timedelta(seconds=31))
                await self.bus.run_due(self.mid)
        return result

    async def read(self, fn: Any, *args: Any) -> Any:
        async with self.bus.db.read() as conn:
            return await fn(Repository(conn, self.mid), *args)

    def advance(self, moment: datetime) -> None:
        """Move the sim clock forward to `moment` (never backwards)."""
        if moment > self.bus.clock.now():
            self.bus.clock.set(moment)

    def at(self, day: datetime, hhmm: str) -> datetime:
        hour, minute = map(int, hhmm.split(":"))
        return datetime.combine(day.date(), time(hour, minute), IST)

    async def build(self) -> dict[str, Any]:
        spec, clock = self.spec, self.bus.clock
        target = clock.now()
        start = (target - timedelta(days=spec.days)).astimezone(IST)
        clock.reset(self.at(start, "08:30"))
        spec.key = spec.key or f"{spec.pack}-{spec.seed}"
        shop = await provision_shop(
            self.bus,
            spec.name or f"Demo {spec.pack.title()}",
            spec.pack,
            "Ramesh Gupta",
            "4826",
            "device-" + spec.key,
            key="world-" + spec.key,
        )
        self.mid = shop["merchant_id"]
        self.owner = Session(self.mid, shop["owner_id"], "owner", channel="console", step_up=True)
        self.manifest.update(
            merchant_id=self.mid, owner_id=shop["owner_id"], device_id=shop["device_id"], pin="4826"
        )
        await self.setup()
        for offset in range(spec.days):
            await self.day(offset, start + timedelta(days=offset))
        self.advance(target)
        await self.plant_final()
        self.manifest["items"] = dict(self.items)
        self.manifest["patrons"] = {
            p["name"].split()[0].lower(): {
                "id": p["id"],
                "vpa": p["vpa"],
                "persona": "p-" + p["id"],
                "account": p["account"],
            }
            for p in self.patrons
        }
        self.manifest["staff"] = {
            name.lower(): staff_id
            for name, staff_id in zip(("Asha", "Ravi"), getattr(self, "stylists", []), strict=False)
        }
        self.manifest["suppliers"] = {
            f"s{i + 1}": {"id": s, "persona": "s-" + s} for i, s in enumerate(self.suppliers)
        }
        self.manifest["counts"] = await self.counts()
        self.manifest["hash"] = hashlib.sha256(
            json.dumps(self.manifest["counts"], sort_keys=True).encode()
        ).hexdigest()
        return self.manifest

    async def setup(self) -> None:
        spec = self.spec
        await self.run(
            "merchant.update_settings",
            {
                "vpa": f"{spec.key}@paytm",
                "address": "Aminabad, Lucknow",
                "name": spec.name or f"Demo {spec.pack.title()}",
            },
        )
        await self.run("onboarding.complete_step", {"step": "language"})
        await self.run("onboarding.complete_step", {"step": "pack"})
        await self.run("onboarding.complete_step", {"step": "details"})
        items = read_starter(PACKS_DIR / "kirana" / "catalog_starter.csv") if spec.pack == "kirana" else []
        self.items: dict[str, str] = {}
        if items:
            result = await self.run("catalog.import_items", {"items": items, "confirmed": True})
            self.items = {i["sku"]: iid for i, iid in zip(items, result["data"]["item_ids"], strict=True)}
        for item in PACK_ITEMS.get(spec.pack, []):
            payload = dict(item)
            if item["sku"] == "CHAI":
                payload["recipe"] = [{"item_id": self.items["MILK"], "qty_milli": 150000}]
            self.items[item["sku"]] = (await self.run("catalog.add_item", payload))["data"]["item_id"]
        await self.run("onboarding.complete_step", {"step": "catalog"})
        await self.run("onboarding.complete_step", {"step": "people"})
        self.details = {sku: await self.read(get_item, iid) for sku, iid in self.items.items()}
        self.sellable = [sku for sku, d in self.details.items() if d["category"] != "ingredient"]
        await self.restock(initial=True)
        self.patrons: list[dict[str, Any]] = []
        for i in range(spec.patrons):
            name = NAMES[i % len(NAMES)]
            vpa = name.split()[0].lower() + str(i) + "@okbank"
            profile = {
                "display_name": name,
                "lang": LANGS[i % len(LANGS)],
                "identities": [{"kind": "vpa", "value": vpa}, {"kind": "spoken_name", "value": name}],
            }
            patron = (
                await self.patron_service.submit(self.owner, "patrons.add", profile, self.key("patron"))
            )["data"]["patron_id"]
            entry = {
                "id": patron,
                "name": name,
                "vpa": vpa,
                "account": None,
                "regular": i < spec.patrons * 0.6,
                "lapsing": False,
            }
            if self.rng.random() < 0.6:
                await self.patron_service.record_customer_instruction(
                    self.mid, patron, "receipts", True, new_id("evt")
                )
            if spec.pack in {"kirana", "pharmacy"} and i % 4 == 0:
                entry["account"] = (
                    await self.run("ledger.open_account", {"patron_id": patron, "limit_paise": 300000})
                )["data"]["account_id"]
            await self.sim.thread(self.mid, "p-" + patron, name, lang=str(profile["lang"]), patron_id=patron)
            self.patrons.append(entry)
        lapsing = [p for p in self.patrons if p["regular"]][:2]
        for p in lapsing:
            p["lapsing"] = True
        self.manifest["planted"]["lapsing_patrons"] = [p["id"] for p in lapsing]
        self.suppliers = []
        for name, lead in [("Agarwal Traders", 2), ("Shree Balaji Distributors", 4)]:
            supplier = (
                await self.run("supply.add_supplier", {"name": name, "lang": "hi", "lead_days": lead})
            )["data"]["supplier_id"]
            await self.sim.thread(self.mid, "s-" + supplier, name, role="supplier", supplier_id=supplier)
            self.suppliers.append(supplier)
        if spec.pack == "salon":
            self.stylists = []
            for name in ("Asha", "Ravi"):
                added = await self.bus.submit(
                    self.owner,
                    "staff.add",
                    {"name": name, "role": "helper"},
                    self.key("staff"),
                    private={"pin": "1357"},
                )
                staff_id = added["data"]["staff_id"]
                await self.run("staff.set_skills", {"staff_id": staff_id, "skills": ["hair", "skin"]})
                self.stylists.append(staff_id)
        await self.run(
            "storefront.publish",
            {"slug": str(spec.key).replace("_", "-")[:40], "published": True, "show_offers": True},
        )

    async def restock(self, initial: bool = False) -> None:
        if self.spec.pack == "salon":
            return
        view = {r["item_id"]: r for r in (await self.read(stock_view, self.bus.clock))["items"]}
        for sku, item_id in self.items.items():
            detail = self.details[sku]
            low = view[item_id]["sellable_qty_milli"] < (10_000_000 if sku == "MILK" else 20_000)
            if not (initial or low):
                continue
            qty = 40_000_000 if sku == "MILK" else 60_000
            payload: dict[str, Any] = {"item_id": item_id, "qty_milli": qty}
            if self.spec.pack == "pharmacy":
                today = self.bus.clock.now_ist().date()
                near = initial and sku == "PARA"
                expires = today + timedelta(days=self.spec.days + 20 if near else 400)
                payload["batch"] = {
                    "batch_no": f"{sku}-{self.counter}",
                    "expires_on": expires.isoformat(),
                    "mrp_paise": detail["mrp_paise"],
                    "cost_paise": detail["cost_paise"],
                }
                if near:
                    self.manifest["planted"]["near_expiry_batch_item"] = item_id
            await self.run("stock.receive", payload)

    def pick_patron(self, offset: int) -> dict[str, Any] | None:
        if self.rng.random() < 0.3:
            return None  # walk-in
        pool = [
            p
            for p in self.patrons
            if not (p["lapsing"] and offset >= self.spec.days - 21)
            and (p["regular"] or self.rng.random() < 0.3)
        ]
        return self.rng.choice(pool) if pool else None

    def lines(self) -> list[dict[str, Any]]:
        result = []
        for sku in self.rng.sample(self.sellable, k=min(len(self.sellable), self.rng.randint(1, 3))):
            detail = self.details[sku]
            line: dict[str, Any] = {
                "item_id": self.items[sku],
                "qty_milli": self.rng.randint(1, 3) * 1000,
                "added_via": self.rng.choice(["scan", "tap", "voice", "search"]),
            }
            if detail["modifier_groups"]:
                line["modifier_ids"] = [
                    g["options"][0]["id"] for g in detail["modifier_groups"] if g["required"]
                ]
            if detail["details"].get("rx_required"):
                line["rx_seen"] = True
            if "duration_minutes" in detail["details"]:
                line["qty_milli"] = 1000
            result.append(line)
        return result

    async def sale(self, patron: dict[str, Any] | None) -> None:
        bill = (await self.run("counter.open_bill", {"patron_id": patron["id"]} if patron else {}))["data"][
            "bill_id"
        ]
        await self.run("counter.add_lines", {"bill_id": bill, "lines": self.lines()})
        if self.spec.pack == "cafe" and self.rng.random() < 0.5:
            ticket = (await self.run("counter.send_to_kitchen", {"bill_id": bill}))["data"]["ticket_id"]
            for to in ("preparing", "ready", "served"):
                await self.run("counter.advance_ticket", {"ticket_id": ticket, "to": to})
        total = (await self.read(bill_state, bill))["total_paise"]
        roll = self.rng.random()
        try:
            if patron and patron["account"] and roll < 0.18:
                await self.run(
                    "counter.checkout_khata",
                    {"bill_id": bill, "account_id": patron["account"], "khata_paise": total, "payments": []},
                )
            elif roll < 0.62:
                intent = (await self.run("counter.request_upi", {"bill_id": bill}))["data"]
                qr = await self.sim.create_qr(self.mid, intent["order_ref"], intent["amount_paise"])
                payer = patron["vpa"] if patron else f"walkin{self.counter}@ybl"
                await self.sim.pay(self.mid, token=qr["token"], payer_vpa=payer)
            else:
                tendered = -(-total // 10000) * 10000
                await self.run(
                    "counter.checkout",
                    {
                        "bill_id": bill,
                        "payments": [{"mode": "cash", "amount_paise": total, "tendered_paise": tendered}],
                    },
                )
        except CommandError as exc:
            if str(exc) not in {"ledger.over_limit", "stock.insufficient_sellable"}:
                raise
            await self.run(
                "counter.checkout", {"bill_id": bill, "payments": [{"mode": "cash", "amount_paise": total}]}
            )

    async def day(self, offset: int, day: datetime) -> None:
        clock, spec = self.bus.clock, self.spec
        self.advance(self.at(day, "08:30"))
        factor = 1.3 if day.weekday() >= 5 else 1.0
        if offset == spec.days - 10:
            factor = 0.3
            self.manifest["planted"]["anomaly_day"] = day.date().isoformat()
        count = max(1, int(SIZE[spec.size] * factor * self.rng.uniform(0.8, 1.2)))
        minutes = 12 * 60 // (count + 1)
        for _ in range(count):
            clock.set(clock.now() + timedelta(minutes=minutes))
            await self.sale(self.pick_patron(offset))
        self.advance(self.at(day, "20:30"))
        for patron in self.patrons:
            if patron["account"] and self.rng.random() < 0.15:
                due = (await self.read(statement, patron["account"], clock))["balance_paise"]
                if due > 0:
                    await self.run(
                        "ledger.record_payment",
                        {
                            "account_id": patron["account"],
                            "amount_paise": max(100, due // 2),
                            "payment_ref": new_id("payment"),
                            "mode": "cash",
                        },
                    )
        if self.rng.random() < 0.4:
            await self.run(
                "treasury.expense",
                {
                    "category": self.rng.choice(["transport", "electricity", "supplies"]),
                    "amount_paise": self.rng.randint(5, 40) * 1000,
                    "paid_from": "cash",
                },
            )
        if offset % 7 == 3 and self.spec.pack != "salon":
            await self.purchase(variance=offset == 3)
        await self.restock()
        if offset == spec.days - 5:
            await self.run("stock.log_unmet_demand", {"text": "ghee nahi tha"})
            await self.run("stock.log_unmet_demand", {"text": "ghee ka bada dabba"})
            self.manifest["planted"]["unmet_demand"] = 2
        self.advance(self.at(day, "21:00"))
        await self.sim.settle(self.mid, day.date().isoformat())
        await self.run("treasury.daily_close", {"date": day.date().isoformat()})

    async def purchase(self, variance: bool) -> None:
        sku = self.sellable[0]
        detail = self.details[sku]
        supplier = self.suppliers[0]
        await self.run(
            "supply.record_quote",
            {"supplier_id": supplier, "item_id": self.items[sku], "unit_price_paise": detail["cost_paise"]},
        )
        po = (
            await self.run(
                "supply.draft_po",
                {
                    "supplier_id": supplier,
                    "lines": [
                        {
                            "item_id": self.items[sku],
                            "qty_milli": 20000,
                            "unit_price_paise": detail["cost_paise"],
                        }
                    ],
                },
            )
        )["data"]["po_id"]
        await self.run("supply.place_po", {"po_id": po})
        await self.bus.submit(
            Session(self.mid, new_id("system"), "system", actor_kind="supplier"),
            "supply.confirm_po",
            {"po_id": po},
            self.key("confirm"),
            private={"supplier_verified": True},
        )
        line: dict[str, Any] = {"item_id": self.items[sku], "qty_milli": 20000}
        if self.spec.pack == "pharmacy":
            expires = (self.bus.clock.now_ist().date() + timedelta(days=500)).isoformat()
            line["batch"] = {
                "batch_no": f"PO-{self.counter}",
                "expires_on": expires,
                "mrp_paise": detail["mrp_paise"],
                "cost_paise": detail["cost_paise"],
            }
        await self.run("supply.receive", {"po_id": po, "lines": [line]})
        billed = detail["cost_paise"] + (100 if variance else 0)
        due = (self.bus.clock.now_ist().date() + timedelta(days=15)).isoformat()
        await self.run(
            "supply.record_bill",
            {
                "po_id": po,
                "bill_ref": f"INV-{self.counter}",
                "due_on": due,
                "lines": [{"item_id": self.items[sku], "qty_milli": 20000, "unit_price_paise": billed}],
            },
        )
        if variance:
            self.manifest["planted"]["grn_variance_po"] = po

    async def plant_final(self) -> None:
        clock = self.bus.clock
        self.advance(clock.now() + timedelta(minutes=1))
        patron = next(p for p in self.patrons if p["regular"] and not p["lapsing"])
        bill = (await self.run("counter.open_bill", {"patron_id": patron["id"]}))["data"]["bill_id"]
        await self.run("counter.add_lines", {"bill_id": bill, "lines": self.lines()})
        intent = (await self.run("counter.request_upi", {"bill_id": bill}))["data"]
        qr = await self.sim.create_qr(self.mid, intent["order_ref"], intent["amount_paise"])
        await self.sim.pay(self.mid, token=qr["token"], payer_vpa=patron["vpa"])
        duplicate = await self.sim.pay(self.mid, payer_vpa=patron["vpa"], amount_paise=intent["amount_paise"])
        self.manifest["planted"]["duplicate_payment_utr"] = duplicate["utr"]
        forged = screenshot(
            84000, "430199990000", f"{self.spec.key}@paytm", iso_utc(clock.now()), edited=True
        )
        check = await self.run(
            "sentinel.check",
            {**forged["fields"], "phash": forged["phash"], "ela_score_bp": forged["ela_score_bp"]},
        )
        self.manifest["planted"]["forged_screenshot_check"] = check["data"]["check_id"]
        self.manifest["planted"]["forged_verdict"] = check["data"]["verdict"]

    async def counts(self) -> dict[str, int]:
        from arth.domains.commerce_tables import bills, payments
        from arth.domains.patron_tables import patrons

        async with self.bus.db.read() as conn:
            repo = Repository(conn, self.mid)
            return {
                "bills": len(await repo.select(bills, bills.c.status == "closed")),
                "payments": len(await repo.select(payments)),
                "patrons": len(await repo.select(patrons)),
                "items": len(self.items),
            }


def payer_ref(merchant_id: str, vpa: str) -> str:
    return identity_value(merchant_id, "vpa", vpa)[1]
