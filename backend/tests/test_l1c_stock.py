from datetime import timedelta

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from l1c_helpers import fixture_shop


async def test_stock_projection_counts_fefo_recall_and_oversell_rollback(db):
    from arth.domains.stock import issue_stock, on_hand, register_stock
    from arth.domains.stock_tables import stock_moves
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, actor, item = await fixture_shop(db)
    register_stock(bus, bus.packs)
    for n, expiry in [(1, "2026-12-01"), (2, "2026-11-01")]:
        await bus.submit(
            actor,
            "stock.receive",
            {
                "item_id": item,
                "qty_milli": 10000,
                "batch": {"batch_no": str(n), "expires_on": expiry, "mrp_paise": 3000, "cost_paise": 2000},
            },
            "receive" + str(n),
        )

    async def issue(repo, payload):
        return {
            "moves": await issue_stock(
                repo, bus.clock, item, payload["qty_milli"], repo.command_id, buyer_id=actor.actor_id
            )
        }

    bus.policy.policies.tiers["test.issue"] = "R1"
    bus.register(
        "test.issue",
        {
            "type": "object",
            "properties": {"qty_milli": {"type": "integer", "minimum": 1}},
            "required": ["qty_milli"],
            "additionalProperties": False,
        },
        issue,
    )
    result = await bus.submit(actor, "test.issue", {"qty_milli": 12000}, "issue")
    assert [r["qty_milli"] for r in result["data"]["moves"]] == [10000, 2000]
    async with db.read() as conn:
        repo = Repository(conn, actor.merchant_id)
        assert await on_hand(repo, item) == 8000
        rows = await repo.select(stock_moves)
        assert sum(r["delta_qty_milli"] for r in rows) == 8000
        assert await on_hand(Repository(conn, "other"), item) == 0
    with pytest.raises(CommandError, match="insufficient"):
        await bus.submit(actor, "test.issue", {"qty_milli": 9000}, "too-much")
    remaining = result["data"]["moves"][1]["batch_id"]
    recalled = await bus.submit(
        actor, "stock.recall_batch", {"batch_id": remaining, "reason": "stock.recall"}, "recall"
    )
    assert recalled["data"]["buyer_ids"] == [actor.actor_id]
    with pytest.raises(CommandError):
        await bus.submit(actor, "test.issue", {"qty_milli": 1000}, "recalled-sale")
    await bus.submit(
        actor, "stock.count", {"item_id": item, "batch_id": remaining, "counted_qty_milli": 5000}, "count"
    )
    async with db.read() as conn:
        assert await on_hand(Repository(conn, actor.merchant_id), item) == 5000


@settings(max_examples=12, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=5))
async def test_fefo_and_quantity_projection_property(db, quantities):
    from arth.domains.stock import issue_stock, on_hand, register_stock
    from arth.governance.repository import Repository

    bus, actor, item = await fixture_shop(db)
    register_stock(bus, bus.packs)
    batches = []
    for n, qty in enumerate(quantities):
        expiry = (bus.clock.now_ist().date() + timedelta(days=10 + n)).isoformat()
        result = await bus.submit(
            actor,
            "stock.receive",
            {
                "item_id": item,
                "qty_milli": qty,
                "batch": {"batch_no": str(n), "expires_on": expiry, "mrp_paise": 3000, "cost_paise": 2000},
            },
            "receive" + str(n),
        )
        batches.append(result["data"]["batch_id"])
    wanted = max(1, sum(quantities) // 2)

    async def take(repo, payload):
        return {"moves": await issue_stock(repo, bus.clock, item, wanted, repo.command_id)}

    bus.policy.policies.tiers["test.take"] = "R1"
    bus.register("test.take", {"type": "object", "additionalProperties": False}, take)
    moves = (await bus.submit(actor, "test.take", {}, "take"))["data"]["moves"]
    assert [r["batch_id"] for r in moves] == batches[: len(moves)]
    assert sum(r["qty_milli"] for r in moves) == wanted
    async with db.read() as conn:
        assert await on_hand(Repository(conn, actor.merchant_id), item) == sum(quantities) - wanted
