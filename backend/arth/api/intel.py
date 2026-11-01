"""L3 read surface: forecast and insights views, parameterised analytics tools, chart cards, book exports."""

import csv
import io
import json
from datetime import date, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import Response

from arth.api.commerce import Actor
from arth.api.problems import ProblemError
from arth.core.clock import iso_utc
from arth.governance.repository import Repository
from arth.intel import analytics as a
from arth.intel.charts import build, svg
from arth.intel.commands import active_snoozes
from arth.intel.forecast import cashflow, item_forecast, sales_forecast
from arth.intel.insight import demand_clusters, next_best_actions, sufficiency
from arth.intel.tables import alerts
from arth.sim.peers import peers_view

router = APIRouter()
DateParam = Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")]


def bad(code: str) -> ProblemError:
    return ProblemError(422, code, "error." + code, title="Invalid request")


@router.get("/v1/views/forecast")
async def forecast(request: Request, session: Actor, metric: str = "sales") -> dict[str, Any]:
    if metric not in {"sales", "items"}:
        raise bad("view.invalid_metric")
    state = request.app.state
    async with state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        # 10 days ahead: far enough to show the next festival (Diwali is 9 days after the demo's 30 Oct)
        result = await sales_forecast(repo, state.clock, state.calendar, horizon=12)
        items = await item_forecast(repo, state.clock) if metric == "items" else []
    return {
        **result,
        "metric": metric,
        "items": [
            {k: r[k] for k in ("item_id", "name", "daily_qty_milli", "horizon_qty_milli")} for r in items
        ],
        "invalidate_on": ["forecast.updated", "bill.paid", "clock.day"],
    }


@router.get("/v1/views/insights")
async def insights(request: Request, session: Actor) -> dict[str, Any]:
    state = request.app.state
    async with state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        mix: dict[str, int] = {}
        for row in await a.lifecycle(repo, state.clock):
            mix[row["state"]] = mix.get(row["state"], 0) + 1
        raised = sorted(await repo.select(alerts), key=lambda r: r["raised_at"], reverse=True)[:20]
        return {
            "sufficiency": await sufficiency(repo, state.clock),
            "alerts": [
                {
                    **{k: r[k] for k in ("id", "key", "kind", "severity", "raised_at")},
                    "params": json.loads(r["params"]),
                }
                for r in raised
            ],
            "actions": await next_best_actions(
                repo, state.clock, await active_snoozes(repo, iso_utc(state.clock.now()))
            ),
            "lifecycle": mix,
            "demand_clusters": await demand_clusters(repo),
            "invalidate_on": ["alert.raised", "action.snoozed", "bill.paid", "stock.demand_logged"],
        }


@router.get("/v1/analytics/{tool}")
async def analytics(
    request: Request, tool: str, session: Actor, start: DateParam = None, end: DateParam = None
) -> dict[str, Any]:
    """Domain reads (C2): every number an answer uses comes from one of these parameterised tools."""
    state = request.app.state
    last = date.fromisoformat(end) if end else a.today(state.clock)
    first = date.fromisoformat(start) if start else last - timedelta(days=6)
    if first > last or (last - first).days > 366:
        raise bad("analytics.invalid_period")
    async with state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        tools: dict[str, Any] = {
            "sales": lambda: a.daily_sales(repo, first, last),
            "payments": lambda: a.payments_by_mode(repo, first, last),
            "compare": lambda: a.compare(
                repo, (first, last), (first - (last - first) - timedelta(days=1), first - timedelta(days=1))
            ),
            "top": lambda: a.top_items(repo, first, last),
            "slow": lambda: a.slow_items(repo, first, last),
            "khata_aging": lambda: a.khata_aging(repo, state.clock),
            "lifecycle": lambda: a.lifecycle(repo, state.clock),
            "lapsed": lambda: a.lapsed(repo, state.clock),
            "hourly": lambda: a.hourly(repo, first, last),
            "cycles": lambda: a.purchase_cycles(repo, state.clock),
            "affinity": lambda: a.affinity(repo),
            "cashflow": lambda: cashflow(repo, state.clock, state.calendar),
            "demand": lambda: demand_clusters(repo),
        }
        if tool not in tools:
            raise ProblemError(
                404, "analytics.unknown_tool", "error.analytics.unknown_tool", title="Unknown tool"
            )
        result = await tools[tool]()
    return {"tool": tool, "period": {"start": first.isoformat(), "end": last.isoformat()}, "result": result}


@router.get("/v1/charts/{number}", response_model=None)
async def chart(request: Request, number: int, session: Actor, format: str = "json") -> Any:
    if not 1 <= number <= 12:
        raise bad("chart.unknown")
    state = request.app.state
    async with state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        from arth.governance.tables import merchants

        pack = (await repo.select(merchants))[0]["pack"]
        result = await build(number, repo, state.clock, state.calendar, await peers_view(conn, pack))
    if format == "svg":
        return Response(svg(result), media_type="image/svg+xml")
    return {**result, "invalidate_on": ["bill.paid", "payment.received", "credit.changed", "clock.day"]}


@router.get("/v1/books/export/{kind}")
async def export(
    request: Request,
    kind: str,
    session: Actor,
    month: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None,
) -> dict[str, Any]:
    """BKS-2: accountant export pack as CSV text (P&L, GST summary, khata aging, payables, settlements)."""
    from arth.domains.tax import gst_summary, profit_and_loss
    from arth.domains.treasury import settlement_rows

    state = request.app.state
    chosen = month or (state.clock.now() + timedelta(hours=5, minutes=30)).strftime("%Y-%m")
    out = io.StringIO()
    writer = csv.writer(out)
    async with state.db.read() as conn:
        repo = Repository(conn, session.merchant_id)
        if kind == "pnl":
            pnl = await profit_and_loss(repo, chosen)
            writer.writerow(["line", "amount_paise"])
            for key in (
                "sales_paise",
                "returns_paise",
                "cogs_paise",
                "gross_profit_paise",
                "expenses_paise",
                "reward_cost_paise",
                "net_paise",
            ):
                writer.writerow([key, pnl[key]])
        elif kind == "gst":
            gst = await gst_summary(repo, chosen)
            writer.writerow(["rate_bp", "taxable_paise", "cgst_paise", "sgst_paise", "total_paise"])
            for row in gst["rates"]:
                writer.writerow(
                    [row[k] for k in ("rate_bp", "taxable_paise", "cgst_paise", "sgst_paise", "total_paise")]
                )
        elif kind == "khata_aging":
            writer.writerow(["bucket", "amount_paise"])
            for row in await a.khata_aging(repo, state.clock):
                writer.writerow([row["bucket"], row["amount_paise"]])
        elif kind == "settlements":
            writer.writerow(["date", "gross_paise", "net_paise", "explained"])
            for row in await settlement_rows(repo):
                writer.writerow([row["date"], row["gross_paise"], row["net_paise"], row["explained"]])
        else:
            raise ProblemError(
                404, "books.unknown_export", "error.books.unknown_export", title="Unknown export"
            )
    return {"kind": kind, "month": chosen, "csv": out.getvalue()}
