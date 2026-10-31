"""The 12 standard charts (T3.2, v5.1 F10.3) as chart cards, reproducible from their tool call, plus an SVG
renderer for WhatsApp/Voice images. Takeaways are parameters (the UI and TTS localise them), never free text.
"""

from datetime import timedelta
from html import escape
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.domains.offers import liability
from arth.governance.repository import Repository
from arth.intel import analytics as a
from arth.intel.forecast import cashflow, item_forecast, sales_forecast

TITLES = {
    1: "chart.daily_sales",
    2: "chart.payment_modes",
    3: "chart.hour_weekday",
    4: "chart.top_items",
    5: "chart.category_vs_peers",
    6: "chart.khata_aging",
    7: "chart.cashflow",
    8: "chart.lifecycle_mix",
    9: "chart.offer_result",
    10: "chart.festival_readiness",
    11: "chart.offer_budget",
    12: "chart.forecast_accuracy",
}


def card(
    n: int,
    kind: str,
    x: dict[str, str],
    series: list[dict[str, Any]],
    data: list[dict[str, Any]],
    clock: SimClock,
    takeaway: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "chart",
        "chart_no": n,
        "kind": kind,
        "title_key": TITLES[n],
        "x": x,
        "series": series,
        "data": data,
        "data_ref": f"tool:chart.{n}",
        "as_of": iso_utc(clock.now()),
        "takeaway": takeaway,
    }


async def build(
    n: int, repo: Repository, clock: SimClock, calendar: Any = None, peers: dict[str, Any] | None = None
) -> dict[str, Any]:
    end = a.today(clock)
    start = end - timedelta(days=27)
    if n == 1:
        actual = await a.daily_sales(repo, start, end - timedelta(days=1))
        forecast = await sales_forecast(repo, clock, calendar)
        data = [{"date": r["date"], "sales_paise": r["sales_paise"]} for r in actual] + forecast["days"]
        total = sum(r["sales_paise"] for r in actual)
        return card(
            1,
            "line_band",
            {"field": "date", "type": "date"},
            [
                {"name": "actual", "field": "sales_paise", "unit": "INR"},
                {"name": "forecast", "field": "p50_paise", "band": ["p10_paise", "p90_paise"], "unit": "INR"},
            ],
            data,
            clock,
            {"key": "takeaway.total_28d", "total_paise": total},
        )
    if n == 2:
        rows = await a.payments_by_mode(repo, end, end)
        return card(
            2,
            "bar",
            {"field": "mode", "type": "category"},
            [{"name": "amount", "field": "amount_paise", "unit": "INR"}],
            rows,
            clock,
            {"key": "takeaway.payments_today", "total_paise": sum(r["amount_paise"] for r in rows)},
        )
    if n == 3:
        rows = await a.hourly(repo, start, end)
        peak = max(rows, key=lambda r: r["sales_paise"], default=None)
        return card(
            3,
            "heatmap",
            {"field": "hour", "type": "ordinal"},
            [{"name": "sales", "field": "sales_paise", "unit": "INR", "y": "weekday"}],
            rows,
            clock,
            {
                "key": "takeaway.peak_hour",
                "hour": peak["hour"] if peak else None,
                "weekday": peak["weekday"] if peak else None,
            },
        )
    if n == 4:
        rows = await a.top_items(repo, end - timedelta(days=6), end, 8)
        return card(
            4,
            "bar",
            {"field": "name", "type": "category"},
            [{"name": "amount", "field": "amount_paise", "unit": "INR"}],
            rows,
            clock,
            {"key": "takeaway.top_item", "name": rows[0]["name"] if rows else None},
        )
    if n == 5:
        metrics = (peers or {}).get("metrics", [])
        return card(
            5,
            "bar_range",
            {"field": "metric", "type": "category"},
            [{"name": "peer_range", "field": "p50", "band": ["p25", "p75"]}],
            metrics,
            clock,
            {"key": "takeaway.peers", "n": (peers or {}).get("n", 0)},
        )
    if n == 6:
        rows = await a.khata_aging(repo, clock)
        return card(
            6,
            "bar",
            {"field": "bucket", "type": "category"},
            [{"name": "due", "field": "amount_paise", "unit": "INR"}],
            rows,
            clock,
            {"key": "takeaway.khata_total", "total_paise": sum(r["amount_paise"] for r in rows)},
        )
    if n == 7:
        flow = await cashflow(repo, clock, calendar)
        return card(
            7,
            "line_band",
            {"field": "date", "type": "date"},
            [
                {
                    "name": "balance",
                    "field": "balance_p50_paise",
                    "band": ["balance_p10_paise", "balance_p90_paise"],
                    "unit": "INR",
                }
            ],
            flow["days"],
            clock,
            {"key": "takeaway.shortfall", "shortfall": flow["shortfall"]},
        )
    if n == 8:
        rows = await a.lifecycle(repo, clock)
        mix: dict[str, int] = {}
        for r in rows:
            mix[r["state"]] = mix.get(r["state"], 0) + 1
        data = [{"state": k, "count": v} for k, v in sorted(mix.items())]
        return card(
            8,
            "stacked_bar",
            {"field": "state", "type": "category"},
            [{"name": "patrons", "field": "count"}],
            data,
            clock,
            {"key": "takeaway.lifecycle", **mix},
        )
    if n in (9, 11):
        owed = await liability(repo)
        data = [{"kind": k.removesuffix("_paise"), "amount_paise": v} for k, v in owed.items()]
        kind = "dot_interval" if n == 9 else "bar"
        return card(
            n,
            kind,
            {"field": "kind", "type": "category"},
            [{"name": "amount", "field": "amount_paise", "unit": "INR"}],
            data,
            clock,
            {"key": "takeaway.offers", **owed},
        )
    if n == 10:
        from arth.domains.stock import stock_view

        need = {r["item_id"]: r for r in await item_forecast(repo, clock, horizon=10)}
        stock = (await stock_view(repo, clock))["items"]
        data = [
            {
                "name": s["name"],
                "cover_qty_milli": s["sellable_qty_milli"],
                "demand_qty_milli": need[s["item_id"]]["horizon_qty_milli"],
            }
            for s in stock
            if s["item_id"] in need
        ]
        short = [d["name"] for d in data if d["cover_qty_milli"] < d["demand_qty_milli"]]
        return card(
            10,
            "bar",
            {"field": "name", "type": "category"},
            [{"name": "cover", "field": "cover_qty_milli"}, {"name": "demand", "field": "demand_qty_milli"}],
            data,
            clock,
            {"key": "takeaway.readiness", "short_items": short[:5]},
        )
    if n == 12:
        forecast = await sales_forecast(repo, clock, calendar)
        data = [
            {
                "category": "all",
                "wape_bp": forecast["accuracy"]["wape_bp"],
                "coverage_bp": forecast["accuracy"]["coverage_bp"],
            }
        ]
        return card(
            12,
            "bar",
            {"field": "category", "type": "category"},
            [{"name": "wape", "field": "wape_bp"}],
            data,
            clock,
            {"key": "takeaway.accuracy", **data[0]},
        )
    raise ValueError("chart.unknown")


def svg(chart: dict[str, Any], width: int = 640, height: int = 320) -> str:
    """Minimal server-side image of the first series (WhatsApp/Voice fallback, INS-4)."""
    field = chart["series"][0]["field"] if chart["series"] else None
    values = [r.get(field) or 0 for r in chart["data"]] if field else []
    top = max(values + [1])
    bar = (width - 40) / max(1, len(values))
    scale = (height - 60) / top
    rects = "".join(
        f'<rect x="{20 + i * bar:.1f}" y="{height - 30 - v * scale:.1f}" width="{bar * 0.8:.1f}" '
        f'height="{v * scale:.1f}" fill="#2f6fde"/>'
        for i, v in enumerate(values)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<rect width="100%" height="100%" fill="#fff"/><text x="20" y="20" font-size="14">'
        f"{escape(chart['title_key'])}</text>{rects}</svg>"
    )
