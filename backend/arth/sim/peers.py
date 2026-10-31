"""Peer cohorts (T2.9): synthetic peer shops per pack, exposed only as percentiles with n ≥ 10 (GRW-3)."""

import random
from typing import Any

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncConnection

from arth.sim.tables import sim_peer_metrics

MIN_PEERS = 10
PROFILES = {  # median daily sales (paise), median bill, UPI share, repeat-visit share, khata share
    "kirana": (450000, 18000, 6200, 5500, 1800),
    "cafe": (300000, 9000, 7000, 4500, 500),
    "pharmacy": (600000, 35000, 6500, 5000, 1200),
    "salon": (350000, 40000, 7500, 4000, 300),
}
METRICS = ("daily_sales_paise", "avg_bill_paise", "upi_share_bp", "repeat_share_bp", "khata_share_bp")


def percentile(values: list[int], pct: int) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, (len(ordered) - 1) * pct // 100)]


def cohort(pack: str, n: int = 12, seed: int = 7) -> dict[str, list[int]]:
    rng = random.Random(f"{pack}:{seed}")
    shops = [[int(m * rng.lognormvariate(0, 0.35)) for m in PROFILES[pack]] for _ in range(n)]
    return {metric: [shop[i] for shop in shops] for i, metric in enumerate(METRICS)}


async def generate(conn: AsyncConnection, n: int = 12, seed: int = 7) -> None:
    await conn.execute(delete(sim_peer_metrics))
    for pack in PROFILES:
        for metric, values in cohort(pack, n, seed).items():
            await conn.execute(
                insert(sim_peer_metrics).values(
                    pack=pack,
                    metric=metric,
                    n=n,
                    **{f"p{p}": percentile(values, p) for p in (10, 25, 50, 75, 90)},
                )
            )


async def peers_view(conn: AsyncConnection, pack: str) -> dict[str, Any]:
    rows = [
        dict(r)
        for r in (
            await conn.execute(select(sim_peer_metrics).where(sim_peer_metrics.c.pack == pack))
        ).mappings()
    ]
    n = min((r["n"] for r in rows), default=0)
    ready = n >= MIN_PEERS
    return {
        "pack": pack,
        "status": "ready" if ready else "insufficient_peers",
        "n": n,
        "metrics": [{k: r[k] for k in ("metric", "p10", "p25", "p50", "p75", "p90")} for r in rows]
        if ready
        else [],
        "invalidate_on": ["growth.peers_refreshed"],
    }
