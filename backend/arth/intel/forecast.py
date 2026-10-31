"""Forecasts (T3.3, T3.4): weekday-seasonal P10/P50/P90 with calendar uplift and an honest accuracy figure.

Prototype model (seasonal naive, statsforecast-style): P50 = mean of the same weekday in the
last four weeks × a festival factor from the calendar; the band comes from empirical quantiles of relative
backtest errors. Accuracy (WAPE, band coverage) is measured on a rolling 14-day backtest and shown with every
forecast (FCT-6). Chronos-2 can replace `_p50` later without changing the read model.
"""

import random
from datetime import date, timedelta
from typing import Any

from arth.core.clock import SimClock
from arth.domains.commerce_tables import loan_applications, loan_offers, purchase_orders
from arth.domains.ledger_tables import payable_allocations, payables
from arth.governance.repository import Repository
from arth.intel.analytics import daily_sales, item_sales, today

HISTORY = 28
BACKTEST = 14
FESTIVAL_FACTOR = 1.3


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))]


def _p50(history: dict[date, int], day: date, festive: set[date]) -> int:
    same = [history[d] for d in (day - timedelta(weeks=k) for k in range(1, 5)) if d in history]
    base = sum(same) / len(same) if same else (sum(history.values()) / len(history) if history else 0)
    return int(base * (FESTIVAL_FACTOR if day in festive else 1.0))


def festive_days(calendar: Any, city: str, start: date, end: date) -> set[date]:
    if calendar is None:
        return set()
    days: set[date] = set()
    try:
        occurrences = calendar.between(city, start, end)
    except (KeyError, ValueError):
        return days
    for occ in occurrences:
        if occ.type in {"festival", "season"} or occ.kind in {"diwali", "holi", "eid_ul_fitr", "salary_days"}:
            for i in range(-occ.lead_days, (occ.end - occ.start).days + 1):
                days.add(occ.start + timedelta(days=i))
    return days


async def sales_forecast(
    repo: Repository, clock: SimClock, calendar: Any = None, city: str = "lucknow", horizon: int = 7
) -> dict[str, Any]:
    now = today(clock)
    start = now - timedelta(days=HISTORY + BACKTEST)
    rows = await daily_sales(repo, start, now - timedelta(days=1))
    history = {date.fromisoformat(r["date"]): r["sales_paise"] for r in rows}
    festive = festive_days(calendar, city, start, now + timedelta(days=horizon))
    errors, covered, abs_err, actual_sum = [], 0, 0, 0
    tested = [now - timedelta(days=i) for i in range(BACKTEST, 0, -1)]
    for day in tested:
        before = {d: v for d, v in history.items() if d < day}
        pred = _p50(before, day, festive)
        actual = history.get(day, 0)
        if pred > 0:
            errors.append((actual - pred) / pred)
        abs_err += abs(actual - pred)
        actual_sum += actual
    lo, hi = min(_quantile(errors, 0.1), 0.0), max(_quantile(errors, 0.9), 0.0)  # P10 ≤ P50 ≤ P90 always
    for day in tested:
        pred = _p50({d: v for d, v in history.items() if d < day}, day, festive)
        if pred * (1 + lo) <= history.get(day, 0) <= pred * (1 + hi):
            covered += 1
    wape_bp = abs_err * 10000 // actual_sum if actual_sum else None
    days: list[dict[str, Any]] = []
    for offset in range(horizon):
        day = now + timedelta(days=offset)
        p50 = _p50(history, day, festive)
        days.append(
            {
                "date": day.isoformat(),
                "p10_paise": max(0, int(p50 * (1 + lo))),
                "p50_paise": p50,
                "p90_paise": max(p50, int(p50 * (1 + hi))),
                "festive": day in festive,
            }
        )
    drivers = [{"key": "driver.weekday", "contribution_paise": days[0]["p50_paise"]}]
    if any(d["festive"] for d in days):
        drivers.append({"key": "driver.festival", "contribution_paise": int(days[0]["p50_paise"]) * 3 // 10})
    sufficient = len([v for v in history.values() if v > 0]) >= 14
    return {
        "metric": "sales",
        "status": "ready" if sufficient else "needs_more_data",
        "actuals": [{"date": d.isoformat(), "sales_paise": v} for d, v in sorted(history.items())][-6:],
        "days": days,
        "accuracy": {
            "wape_bp": wape_bp,
            "coverage_bp": covered * 10000 // len(tested) if tested else None,
            "window_days": BACKTEST,
            "within_band": covered,
        },
        "drivers": drivers,
    }


async def item_forecast(repo: Repository, clock: SimClock, horizon: int = 7) -> list[dict[str, Any]]:
    """Per-item daily rate over 28 days → expected units over the horizon (stock cover, chart 10)."""
    now = today(clock)
    rows = await item_sales(repo, now - timedelta(days=HISTORY), now - timedelta(days=1))
    return [
        {
            **r,
            "daily_qty_milli": r["qty_milli"] // HISTORY,
            "horizon_qty_milli": r["qty_milli"] * horizon // HISTORY,
        }
        for r in rows
    ]


async def cashflow(
    repo: Repository, clock: SimClock, calendar: Any = None, horizon: int = 14
) -> dict[str, Any]:
    """TRS-6/FCT-4: P10/P50/P90 inflow vs scheduled outflows (payables, open POs, EDI) → shortfall date."""
    forecast = await sales_forecast(repo, clock, calendar, horizon=horizon)
    now = today(clock)
    out: dict[date, int] = {}
    for payable in await repo.select(payables):
        paid = sum(
            r["amount_paise"]
            for r in await repo.select(payable_allocations, payable_allocations.c.payable_id == payable["id"])
        )
        due = date.fromisoformat(payable["due_on"])
        if payable["amount_paise"] > paid:
            day = max(due, now)
            out[day] = out.get(day, 0) + payable["amount_paise"] - paid
    for po in await repo.select(purchase_orders, purchase_orders.c.status.in_(["sent", "confirmed"])):
        day = date.fromisoformat(po["due_on"]) if po["due_on"] else now + timedelta(days=3)
        out[max(day, now)] = out.get(max(day, now), 0) + po["total_paise"]
    for application in await repo.select(loan_applications):
        offer = await repo.select(loan_offers, loan_offers.c.id == application["offer_id"])
        if offer:
            for i in range(1, horizon):
                out[now + timedelta(days=i)] = out.get(now + timedelta(days=i), 0) + offer[0]["edi_paise"]
    balance = {"p10": 0, "p50": 0, "p90": 0}
    path, shortfall = [], None
    for row in forecast["days"]:
        day = date.fromisoformat(row["date"])
        spend = out.get(day, 0)
        for band in balance:
            balance[band] += row[f"{band}_paise"] - spend
        path.append(
            {
                "date": row["date"],
                "inflow_p50_paise": row["p50_paise"],
                "outflow_paise": spend,
                "balance_p10_paise": balance["p10"],
                "balance_p50_paise": balance["p50"],
                "balance_p90_paise": balance["p90"],
            }
        )
        if shortfall is None and balance["p10"] < 0:
            shortfall = {"date": row["date"], "amount_paise": -balance["p10"]}
    return {"days": path, "shortfall": shortfall, "status": forecast["status"]}


def bootstrap_ci(
    treated: list[int], holdout: list[int], *, seed: int = 7, rounds: int = 500
) -> dict[str, Any]:
    """T3.9: treated − holdout mean with a 90% bootstrap CI; counts mode when samples are small."""
    if len(treated) < 20 or len(holdout) < 10:
        return {
            "mode": "counts",
            "treated_n": len(treated),
            "holdout_n": len(holdout),
            "treated_sum": sum(treated),
            "holdout_sum": sum(holdout),
            "measurable": False,
        }
    rng = random.Random(seed)
    diffs = []
    for _ in range(rounds):
        t = [rng.choice(treated) for _ in treated]
        h = [rng.choice(holdout) for _ in holdout]
        diffs.append(sum(t) / len(t) - sum(h) / len(h))
    point = sum(treated) / len(treated) - sum(holdout) / len(holdout)
    return {
        "mode": "ci",
        "uplift": round(point),
        "ci90": [round(_quantile(diffs, 0.05)), round(_quantile(diffs, 0.95))],
        "treated_n": len(treated),
        "holdout_n": len(holdout),
        "measurable": True,
    }
