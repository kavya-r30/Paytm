import json
from datetime import timedelta

from test_governance_commands import make_bus


async def test_partial_batch_and_plan_scope_are_explicit(db):
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gates = [await bus.submit(owner, "test.write", {}, str(n)) for n in range(3)]
    thread = await bus.batch(owner, [g["gate_id"] for g in gates], mode="plan")
    results = await bus.decide(owner, thread, "approve", "partial", decisions={gates[1]["gate_id"]: "snooze"})
    assert [r["status"] for r in results["items"]] == ["queued", "snoozed", "queued"]
    async with db.read() as conn:
        rows = await Repository(conn, "a").select(approvals)
        assert all(json.loads(r["scope"])["mode"] == "plan" for r in rows)


async def test_conditional_scope_failure_raises_fresh_gate(db):
    from arth.governance.policy import PolicyContext, Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    actual = {"price_paise": 4500}

    async def facts(repo, payload):
        return PolicyContext(facts=actual)

    schema, handler, _ = bus.registry["test.write"]
    bus.register("test.write", schema.schema, handler, facts)
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one", {"price_paise": {"lte": 4500}})
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    actual["price_paise"] = 4550
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 0
    async with db.read() as conn:
        rows = await Repository(conn, "a").select(approvals)
        assert [r["status"] for r in rows] == ["superseded", "pending"]
        assert rows[0]["scope_hash"] != rows[1]["scope_hash"]


async def test_series_scope_and_edit_create_new_gate(db):
    from arth.governance.policy import Session

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one")
    thread = await bus.batch(owner, [gate["gate_id"]], mode="series")
    result = await bus.decide(owner, thread, "edit", "edit", edits={"fail": False})
    assert result["status"] == "needs_approval"
    assert result["gate_id"] != gate["gate_id"]


async def test_queued_scope_mutation_requires_reapproval(db):
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one")
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    async with db.write() as conn:
        repo = Repository(conn, "a")
        row = (await repo.select(approvals))[0]
        scope = json.loads(row["scope"])
        scope["payload"] = {"fail": False}
        await repo.update(approvals, {"scope": json.dumps(scope)})
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 0
