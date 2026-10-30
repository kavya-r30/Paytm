"""Demand clusters, data-sufficiency gates, alerts and the decision engine (T3.7, T3.10–T3.12)."""

import re
from datetime import timedelta
from typing import Any

from arth.core.clock import SimClock
from arth.domains.commerce_tables import bills, payment_exceptions, refunds
from arth.domains.patron_tables import patrons
from arth.domains.stock import expiry_view, stock_view
from arth.domains.stock_tables import unmet_demand
from arth.domains.treasury import unmatched
from arth.governance.repository import Repository
from arth.intel.analytics import closed_bills, ist_date, khata_aging, lifecycle, today
from arth.intel.forecast import sales_forecast

STOP = {"nahi", "tha", "ka", "ki", "ke", "the", "hai", "bada", "chhota", "dabba", "wala", "no", "not", "a"}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zऀ-ॿ]+", text.lower()) if t not in STOP and len(t) > 1}


async def demand_clusters(repo: Repository, threshold: float = 0.34) -> list[dict[str, Any]]:
    """Agglomerative clustering on token overlap (embeddings plug in at L4; naming is L4)."""
    rows = await repo.select(unmet_demand)
    clusters: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda r: r["occurred_at"]):
        tokens = _tokens(row["text"])
        best = None
        for cluster in clusters:
            overlap = len(tokens & cluster["tokens"]) / max(1, len(tokens | cluster["tokens"]))
            if overlap >= threshold and (best is None or overlap > best[0]):
                best = (overlap, cluster)
        if best:
            best[1]["tokens"] |= tokens
            best[1]["ids"].append(row["id"])
        else:
            clusters.append({"tokens": set(tokens), "ids": [row["id"]]})
    return sorted(
        (
            {
                "label": " ".join(sorted(c["tokens"]))[:60] or "?",
                "count": len(c["ids"]),
                "demand_ids": c["ids"],
            }
            for c in clusters
        ),
        key=lambda c: -c["count"],
    )


GATES = {  # AIQ-17 / ONB-6: feature → (days of history, bills, patrons with ≥3 visits)
    "counter_hints": (21, 200, 10),
    "forecast": (14, 100, 0),
    "winback": (30, 150, 10),
    "replenish": (30, 150, 5),
    "growth_plan": (28, 300, 15),
    "offers_targeting": (14, 100, 10),
    "capital": (28, 200, 0),
}


async def sufficiency(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    closed = await closed_bills(repo)
    first = min((ist_date(b["closed_at"]) for b in closed), default=today(clock))
    days = (today(clock) - first).days
    regulars = len([r for r in await lifecycle(repo, clock) if r["visits"] >= 3])
    result = []
    for feature, (need_days, need_bills, need_regulars) in GATES.items():
        missing_days = max(0, need_days - days)
        ready = missing_days == 0 and len(closed) >= need_bills and regulars >= need_regulars
        result.append(
            {
                "feature": feature,
                "status": "ready" if ready else "learning",
                "days_of_history": days,
                "days_needed": missing_days,
                "bills": len(closed),
                "bills_needed": max(0, need_bills - len(closed)),
                "reason_key": "sufficiency.ready" if ready else "sufficiency.more_data",
            }
        )
    return result


async def alerts(
    repo: Repository, clock: SimClock, calendar: Any = None, expiry_days: int = 30
) -> list[dict[str, Any]]:
    """T3.11: band breaches, refund spikes, settlement mismatches, near-expiry. Keys dedupe repeats."""
    found: list[dict[str, Any]] = []
    forecast = await sales_forecast(repo, clock, calendar)
    if forecast["status"] == "ready":
        yesterday = forecast["actuals"][-1] if forecast["actuals"] else None
        if yesterday:
            band_low = forecast["days"][0]["p10_paise"]
            if yesterday["sales_paise"] < band_low * 0.6:
                found.append(
                    {
                        "key": "sales_low:" + yesterday["date"],
                        "kind": "sales_below_band",
                        "severity": "warn",
                        "params": {
                            "date": yesterday["date"],
                            "sales_paise": yesterday["sales_paise"],
                            "p10_paise": band_low,
                        },
                    }
                )
    since = (clock.now() - timedelta(days=1)).isoformat()
    recent_refunds = [r for r in await repo.select(refunds) if r["occurred_at"] >= since[:19]]
    if len(recent_refunds) >= 3:
        found.append(
            {
                "key": "refund_spike:" + today(clock).isoformat(),
                "kind": "refund_spike",
                "severity": "warn",
                "params": {"count": len(recent_refunds)},
            }
        )
    for row in await repo.select(payment_exceptions, payment_exceptions.c.status == "open"):
        if row["kind"] in {"settlement_mismatch", "duplicate"}:
            found.append(
                {
                    "key": f"pex:{row['id']}",
                    "kind": row["kind"],
                    "severity": "urgent",
                    "params": {"exception_id": row["id"]},
                }
            )
    for batch in (await expiry_view(repo, clock, expiry_days))["batches"]:
        if batch["qty_milli"] > 0:
            found.append(
                {
                    "key": f"expiry:{batch['batch_id']}",
                    "kind": "near_expiry" if not batch["recalled"] else "recalled_stock",
                    "severity": "info",
                    "params": {"batch_id": batch["batch_id"], "days": batch["days_to_expiry"]},
                }
            )
    return found


async def next_best_actions(
    repo: Repository, clock: SimClock, snoozed: set[str], budget: int = 1
) -> dict[str, Any]:
    """DEC-1: generators → scored candidates → attention budget (1 proactive/day) with snooze."""
    candidates: list[dict[str, Any]] = []
    for bucket in await khata_aging(repo, clock):
        if bucket["bucket"] in {"31-60", "60+"} and bucket["amount_paise"]:
            candidates.append(
                {
                    "key": "collect:" + bucket["bucket"],
                    "kind": "collect_khata",
                    "value_paise": bucket["amount_paise"],
                    "params": bucket,
                }
            )
    for row in (await stock_view(repo, clock))["items"]:
        if row["status"] in {"low", "out"}:
            candidates.append(
                {
                    "key": "reorder:" + row["item_id"],
                    "kind": "reorder",
                    "value_paise": 0,
                    "params": {"item_id": row["item_id"], "name": row["name"]},
                }
            )
    for row in await lifecycle(repo, clock):
        if row["state"] == "lapsing":
            candidates.append(
                {
                    "key": "winback:" + row["patron_id"],
                    "kind": "winback",
                    "value_paise": 5000,
                    "params": {"patron_id": row["patron_id"], "name": row["name"]},
                }
            )
    for row in await unmatched(repo, clock):
        candidates.append(
            {
                "key": "match:" + row["payment_id"],
                "kind": "match_payment",
                "value_paise": row["amount_paise"],
                "params": {"payment_id": row["payment_id"]},
            }
        )
    weight = {"match_payment": 3, "collect_khata": 2, "reorder": 2, "winback": 1}
    for c in candidates:
        c["score"] = weight[c["kind"]] * 1000 + min(c["value_paise"] // 100, 999)
    ranked = sorted((c for c in candidates if c["key"] not in snoozed), key=lambda c: (-c["score"], c["key"]))
    return {"proactive": ranked[:budget], "queued": ranked[budget:], "snoozed": sorted(snoozed)}


async def day_counts(repo: Repository, clock: SimClock) -> dict[str, int]:
    now = today(clock)
    return {
        "bills_today": len(
            [
                b
                for b in await repo.select(bills, bills.c.status == "closed")
                if b["closed_at"] and ist_date(b["closed_at"]) == now
            ]
        ),
        "patrons": len(await repo.select(patrons)),
    }
