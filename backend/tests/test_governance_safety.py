import ast
from datetime import datetime

import pytest

from arth.core.clock import IST, SimClock
from arth.core.config import load_policies
from arth.core.paths import BACKEND_DIR, CONFIG_DIR


def test_domain_sql_execution_is_centralized_in_scoped_repository():
    violations = []
    for path in (BACKEND_DIR / "arth" / "governance").glob("*.py"):
        if path.name == "repository.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        violations += [
            f"{path.name}:{n.lineno}"
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr in {"execute", "exec_driver_sql"}
        ]
    assert violations == []


@pytest.mark.parametrize(
    "hour,minute,expected",
    [(8, 0, "allow"), (21, 29, "allow"), (21, 30, "policy.quiet_hours"), (7, 59, "policy.quiet_hours")],
)
def test_quiet_hour_boundaries(hour, minute, expected):
    from arth.governance.policy import PolicyContext, PolicyEngine, Session

    clock = SimClock(datetime(2026, 10, 30, hour, minute, tzinfo=IST))
    policy = PolicyEngine(load_policies(CONFIG_DIR / "policies.yaml"), clock)
    assert (
        policy.evaluate(
            "send", "R3", Session("a", "o", "owner"), PolicyContext(purpose="marketing", consent=True)
        ).code
        == expected
    )


@pytest.mark.parametrize(
    "message_class,age,known,template,allowed",
    [
        ("reply", 600, False, False, True),
        ("reply", 601, False, False, False),
        ("rfq", None, True, True, True),
        ("rfq", None, False, True, False),
        ("receipt", None, False, False, True),
        ("campaign", None, False, False, False),
    ],
)
def test_r1_classes_are_bounded(message_class, age, known, template, allowed):
    from arth.governance.policy import PolicyContext, PolicyEngine, Session

    clock = SimClock(datetime(2026, 10, 30, 12, tzinfo=IST))
    policy = PolicyEngine(load_policies(CONFIG_DIR / "policies.yaml"), clock)
    decision = policy.evaluate(
        "send",
        "R1",
        Session("a", "o", "owner"),
        PolicyContext(
            purpose="receipts",
            consent=True,
            message_class=message_class,
            reply_age_seconds=age,
            known_supplier=known,
            approved_template=template,
        ),
    )
    assert (decision.code == "allow") == allowed


async def test_fresh_conditional_gate_cannot_replay_old_approval(db):
    from datetime import timedelta

    from test_governance_commands import make_bus

    from arth.governance.policy import PolicyContext, Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    actual = {"price": 45}

    async def context(repo, payload):
        return PolicyContext(facts=actual)

    schema, handler, _ = bus.registry["test.write"]
    bus.register("test.write", schema.schema, handler, context)
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one", {"price": {"lte": 45}})
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    actual["price"] = 46
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    await bus.run_due("a")
    async with db.read() as conn:
        pending = (await Repository(conn, "a").select(approvals, approvals.c.status == "pending"))[0]
    result = await bus.decide(owner, pending["thread_id"], "approve", "yes")
    assert result["due_at"] == "2026-10-29T02:16:00.000000Z"
