"""Analytics tool library (T3.1): parameterised reads over the ledgers; results match Treasury to the paisa.

"Sales" for a day = totals of bills closed that IST day (cash, card, UPI, coupons and khata). Payments by
mode come from the unified payments table, exactly as Treasury's day summary.
"""

from collections import defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any

from arth.core.clock import SimClock, parse_iso
from arth.domains.commerce_tables import bill_lines, bills, payment_events, payments
from arth.domains.ledger_tables import credit_accounts, credit_allocations, credit_entries
from arth.domains.summaries import label, patron_name
from arth.domains.tables import items
from arth.governance.repository import Repository

IST = timedelta(hours=5, minutes=30)


def ist_date(stamp: str) -> date:
    return (parse_iso(stamp) + IST).date()


def today(clock: SimClock) -> date:
    return clock.now_ist().date()


async def closed_bills(repo: Repository) -> list[dict[str, Any]]:
    return [b for b in await repo.select(bills, bills.c.status == "closed") if b["closed_at"]]


async def daily_sales(repo: Repository, start: date, end: date) -> list[dict[str, Any]]:
    days: dict[date, list[int]] = {start + timedelta(days=i): [0, 0] for i in range((end - start).days + 1)}
    for bill in await closed_bills(repo):
        day = ist_date(bill["closed_at"])
        if day in days:
            days[day][0] += bill["total_paise"]
            days[day][1] += 1
    return [{"date": d.isoformat(), "sales_paise": v[0], "bills": v[1]} for d, v in sorted(days.items())]


async def payments_by_mode(repo: Repository, start: date, end: date) -> list[dict[str, Any]]:
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for row in await repo.select(payments):
        events = await repo.select(payment_events, payment_events.c.payment_id == row["id"])
        status = max(events, key=lambda r: r["seq"])["status"] if events else "success"
        if status == "success" and start <= ist_date(row["received_at"]) <= end:
            totals[row["mode"]][0] += row["amount_paise"]
            totals[row["mode"]][1] += 1
    return [{"mode": m, "amount_paise": v[0], "count": v[1]} for m, v in sorted(totals.items())]


async def compare(repo: Repository, a: tuple[date, date], b: tuple[date, date]) -> dict[str, Any]:
    first = sum(r["sales_paise"] for r in await daily_sales(repo, *a))
    second = sum(r["sales_paise"] for r in await daily_sales(repo, *b))
    change_bp = (first - second) * 10000 // second if second else None
    return {"current_paise": first, "previous_paise": second, "change_bp": change_bp}


async def item_sales(repo: Repository, start: date, end: date) -> list[dict[str, Any]]:
    closed = {b["id"] for b in await closed_bills(repo) if start <= ist_date(b["closed_at"]) <= end}
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for line in await repo.select(bill_lines, bill_lines.c.status == "active"):
        if line["bill_id"] in closed:
            totals[line["item_id"]][0] += line["amount_paise"]
            totals[line["item_id"]][1] += line["qty_milli"]
    names = {r["id"]: (label(r["names"]), r["category"]) for r in await repo.select(items)}
    return sorted(
        (
            {
                "item_id": i,
                "name": names.get(i, ("", ""))[0],
                "category": names.get(i, ("", ""))[1],
                "amount_paise": v[0],
                "qty_milli": v[1],
            }
            for i, v in totals.items()
        ),
        key=lambda r: (-r["amount_paise"], r["item_id"]),
    )


async def top_items(repo: Repository, start: date, end: date, n: int = 5) -> list[dict[str, Any]]:
    return (await item_sales(repo, start, end))[:n]


async def slow_items(repo: Repository, start: date, end: date, n: int = 5) -> list[dict[str, Any]]:
    sold = {r["item_id"] for r in await item_sales(repo, start, end)}
    return [
        {"item_id": r["id"], "name": label(r["names"]), "category": r["category"]}
        for r in await repo.select(items)
        if r["id"] not in sold and r["category"] != "ingredient"
    ][:n]


async def khata_aging(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    """Open khata by age of the unpaid entry: 0–7, 8–30, 31–60, 60+ days (chart 6)."""
    buckets = {"0-7": 0, "8-30": 0, "31-60": 0, "60+": 0}
    now = today(clock)
    for account in await repo.select(credit_accounts):
        for entry in await repo.select(credit_entries, credit_entries.c.account_id == account["id"]):
            if entry["amount_paise"] <= 0:
                continue
            paid = sum(
                a["amount_paise"]
                for a in await repo.select(credit_allocations, credit_allocations.c.entry_id == entry["id"])
            )
            due = entry["amount_paise"] - paid
            if due <= 0:
                continue
            age = (now - ist_date(entry["occurred_at"])).days
            key = "0-7" if age <= 7 else "8-30" if age <= 30 else "31-60" if age <= 60 else "60+"
            buckets[key] += due
    return [{"bucket": k, "amount_paise": v} for k, v in buckets.items()]


async def visits(repo: Repository) -> dict[str, list[date]]:
    result: dict[str, list[date]] = defaultdict(list)
    for bill in await closed_bills(repo):
        if bill["patron_id"]:
            result[bill["patron_id"]].append(ist_date(bill["closed_at"]))
    return {k: sorted(v) for k, v in result.items()}


async def lifecycle(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    """v5.1 F3.1: new / regular / lapsing / lost / occasional from visit rhythm."""
    now = today(clock)
    result = []
    for patron_id, days in (await visits(repo)).items():
        gaps = [(b - a).days for a, b in zip(days, days[1:], strict=False) if (b - a).days > 0]
        rhythm = median(gaps) if gaps else None
        since = (now - days[-1]).days
        first = (now - days[0]).days
        if first <= 14 and len(days) <= 2:
            state = "new"
        elif since > 60:
            state = "lost"
        elif rhythm and len(days) >= 3 and since > max(2 * rhythm, 7):
            state = "lapsing"
        elif rhythm and len(days) >= 3:
            state = "regular"
        else:
            state = "occasional"
        result.append(
            {
                "patron_id": patron_id,
                "name": await patron_name(repo, patron_id),
                "state": state,
                "visits": len(days),
                "last_visit": days[-1].isoformat(),
                "days_since": since,
                "rhythm_days": rhythm,
            }
        )
    return sorted(result, key=lambda r: (r["state"], -r["visits"]))


async def lapsed(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    return [r for r in await lifecycle(repo, clock) if r["state"] in {"lapsing", "lost"}]


async def hourly(repo: Repository, start: date, end: date) -> list[dict[str, Any]]:
    """Sales by hour × weekday (chart 3)."""
    cells: dict[tuple[int, int], int] = defaultdict(int)
    for bill in await closed_bills(repo):
        local = parse_iso(bill["closed_at"]) + IST
        if start <= local.date() <= end:
            cells[(local.weekday(), local.hour)] += bill["total_paise"]
    return [{"weekday": w, "hour": h, "sales_paise": v} for (w, h), v in sorted(cells.items())]


async def purchase_cycles(repo: Repository, clock: SimClock) -> list[dict[str, Any]]:
    """v5.1 F3.2: per (patron, item) median repurchase gap → next due date with a ±band."""
    per: dict[tuple[str, str], list[date]] = defaultdict(list)
    closed = {b["id"]: b for b in await closed_bills(repo) if b["patron_id"]}
    for line in await repo.select(bill_lines, bill_lines.c.status == "active"):
        bill = closed.get(line["bill_id"])
        if bill:
            per[(bill["patron_id"], line["item_id"])].append(ist_date(bill["closed_at"]))
    result = []
    for (patron_id, item_id), days in per.items():
        days = sorted(set(days))
        gaps = [(b - a).days for a, b in zip(days, days[1:], strict=False)]
        if len(gaps) < 2:
            continue
        cycle = int(median(gaps))
        band = max(1, int(median(abs(g - cycle) for g in gaps)))
        result.append(
            {
                "patron_id": patron_id,
                "item_id": item_id,
                "cycle_days": cycle,
                "band_days": band,
                "next_due": (days[-1] + timedelta(days=cycle)).isoformat(),
                "overdue_days": max(0, (today(clock) - days[-1]).days - cycle),
            }
        )
    return sorted(result, key=lambda r: r["next_due"])


async def affinity(repo: Repository, min_support: int = 2) -> dict[str, Any]:
    """v5.1 F3.4: item pairs bought together (support, lift) and per-patron habits."""
    baskets: dict[str, set[str]] = defaultdict(set)
    closed = {b["id"]: b for b in await closed_bills(repo)}
    for line in await repo.select(bill_lines, bill_lines.c.status == "active"):
        if line["bill_id"] in closed:
            baskets[line["bill_id"]].add(line["item_id"])
    n = len(baskets) or 1
    single: dict[str, int] = defaultdict(int)
    pairs: dict[tuple[str, str], int] = defaultdict(int)
    for basket in baskets.values():
        ordered = sorted(basket)
        for item in ordered:
            single[item] += 1
        for i, a in enumerate(ordered):
            for b in ordered[i + 1 :]:
                pairs[(a, b)] += 1
    pair_rows: list[dict[str, Any]] = [
        {"a": a, "b": b, "support": c, "lift_bp": c * n * 10000 // (single[a] * single[b])}
        for (a, b), c in pairs.items()
        if c >= min_support
    ]
    habits: dict[tuple[str, str], int] = defaultdict(int)
    trips: dict[str, int] = defaultdict(int)
    for bill_id, basket in baskets.items():
        patron = closed[bill_id]["patron_id"]
        if patron:
            trips[patron] += 1
            for item in basket:
                habits[(patron, item)] += 1
    habit_rows = [
        {"patron_id": p, "item_id": i, "share_bp": c * 10000 // trips[p], "trips": trips[p]}
        for (p, i), c in habits.items()
        if trips[p] >= 3 and c * 10000 // trips[p] >= 6000
    ]
    return {"pairs": sorted(pair_rows, key=lambda r: -int(r["lift_bp"]))[:20], "habits": habit_rows}
