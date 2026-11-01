"""Build the kirana stage demo in a clean, throw-away database and save it as a snapshot the API restores.

    python -m arth.tools.build_demo [--days 40] [--name kirana-demo]

Building in an empty data dir keeps it fast (world building replays every day's jobs for every shop in
the database) and leaves exactly one shop in the snapshot, so the surfaces auto-connect to it. The first beat
(Night Shift: brief and the owner's checklist) is played before saving, so the demo opens with tasks waiting.
The snapshot and its metadata (clock, shop, the Director's scenario state) land in the real snapshots/ folder.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.main import create_app


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--days", type=int, default=40, help="days of history (forecasts need >= 14)")
    parser.add_argument("--name", default="kirana-demo")
    parser.add_argument("--scenario", default="gupta_diwali")
    parser.add_argument("--shop", default="Gupta General Store")
    args = parser.parse_args()
    target = Path(Settings().data_dir) / "snapshots"
    target.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="arth-demo-") as tmp:
        app = create_app(Settings(data_dir=Path(tmp), clock_running=False))
        director = {"Authorization": "Bearer dev-director"}
        with TestClient(app) as client:
            played = client.post(
                "/v1/director/play",
                json={"scenario": args.scenario, "days": args.days, "shop_name": args.shop},
                headers=director,
            )
            played.raise_for_status()
            first = played.json()["beats"][0]  # Night Shift: the morning brief and the checklist on Today
            beat = client.post("/v1/director/play/beat", json={"beat_id": first}, headers=director).json()
            print(f"beat {first}: {'pass' if beat.get('ok') else beat.get('error')}")
            # the owner's morning checklist ("Haan, teeno" in beat 1.2): Arth's reorders for the three items
            # lowest against their target, each a purchase order waiting for the owner's yes (R3)
            token = client.post("/v1/director/session", json={"surface": "device"}, headers=director).json()
            auth = {"Authorization": f"Bearer {token['token']}"}
            # running offers for the Diwali season (OFR): each program is R3, approved here so it is live
            now = client.get("/healthz").json()["clock"]
            catalog = {
                i["name"]: i["item_id"] for i in client.get("/v1/views/stock", headers=auth).json()["items"]
            }
            programs = [
                ("next_txn_cashback", 2000, 30000, 7, 200000, None),  # ₹20 back on the next bill over ₹300
                ("first_time_coupon", 2500, 20000, 14, 100000, None),  # ₹25 off a first bill over ₹200
                ("item_coupon", 1000, 0, 10, 50000, catalog.get("Haldiram Aloo Bhujia")),  # ₹10 off bhujia
            ]
            for kind, reward, min_spend, days, budget, item in programs:
                rules: dict[str, object] = {
                    "reward_paise": reward,
                    "min_spend_paise": min_spend,
                    "validity_days": days,
                }
                if item:
                    rules["item_id"] = item
                elif kind == "item_coupon":
                    continue
                asked = client.post(
                    "/v1/commands",
                    json={
                        "type": "offers.create_program",
                        "payload": {
                            "type": kind,
                            "rules": rules,
                            "terms": {
                                "amount_paise": reward,
                                "min_spend_paise": min_spend,
                                "expiry_days": days,
                            },
                            "budget_paise": budget,
                            "funding": "merchant",
                            "holdout_bp": 2000,
                            "valid_from": now,
                            "valid_until": "2026-11-15T18:29:59Z",
                        },
                    },
                    headers={**auth, "Idempotency-Key": f"demo-offer-{kind}"},
                ).json()
                if asked.get("status") == "needs_approval":
                    client.post(
                        f"/v1/approvals/{asked['thread_id']}",
                        json={"decision": "approve"},
                        headers={**auth, "Idempotency-Key": f"demo-offer-yes-{kind}"},
                    ).raise_for_status()
            client.post(
                "/v1/director/clock", json={"advance_minutes": 1}, headers=director
            )  # past the undo window
            deadline = time.monotonic() + 30  # the tick loop executes the queued (undo-window) commands
            while len(client.get("/v1/views/offers", headers=auth).json()["programs"]) < 3:
                if time.monotonic() > deadline:
                    break
                time.sleep(1)
            live = client.get("/v1/views/offers", headers=auth).json()["programs"]
            print(f"offers: {len(live)} program(s) -> {', '.join(p.get('type', '?') for p in live)}")
            stock = client.get("/v1/views/stock", headers=auth).json()["items"]
            low = sorted(stock, key=lambda r: r["on_hand_qty_milli"] / max(r.get("target_qty_milli") or 1, 1))
            for item in low[:3]:
                client.post(
                    "/v1/commands",
                    json={
                        "type": "playbooks.start",
                        "payload": {"playbook": "reorder", "subject": item["item_id"]},
                    },
                    headers={**auth, "Idempotency-Key": f"demo-reorder-{item['item_id']}"},
                ).raise_for_status()
            deadline = time.monotonic() + 90
            while len(client.get("/v1/views/notifications", headers=auth).json()["needs_you"]) < 3:
                if time.monotonic() > deadline:
                    print("warning: the reorder approvals did not all appear")
                    break
                time.sleep(1)
            waiting = client.get("/v1/views/notifications", headers=auth).json()["needs_you"]
            print(f"checklist: {len(waiting)} item(s) waiting for the owner's yes")
            client.post(
                "/v1/director/snapshot", json={"name": args.name}, headers=director
            ).raise_for_status()
        for suffix in (".db", ".json"):
            shutil.copyfile(Path(tmp) / "snapshots" / f"{args.name}{suffix}", target / f"{args.name}{suffix}")
    took = time.monotonic() - started
    print(f"demo snapshot {args.name}: {args.days} days of history, built in {took:.0f} s -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
