from arth.core.clock import SimClock
from arth.core.config import Settings


async def test_audit_chain_detects_tamper_and_isolates_tenants(db):
    from arth.governance.audit import append_audit, verify_audit
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log

    clock = SimClock(Settings(_env_file=None).clock_start)
    async with db.write() as conn:
        repo = Repository(conn, "a")
        await append_audit(repo, clock, "cmd_a", "executed", {"amount_paise": 45000})
        await append_audit(repo, clock, "cmd_b", "executed", {})
        assert (await verify_audit(repo))["valid"]
        assert (await verify_audit(Repository(conn, "b")))["checked"] == 0
        await repo.update(audit_log, {"data": "{}"}, audit_log.c.seq == 1)
        assert (await verify_audit(repo)) == {"valid": False, "checked": 0, "bad_seq": 1}


async def test_audit_hash_protects_sequence_number(db):
    from arth.governance.audit import append_audit, verify_audit
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log

    clock = SimClock(Settings(_env_file=None).clock_start)
    async with db.write() as conn:
        repo = Repository(conn, "a")
        await append_audit(repo, clock, "cmd_a", "executed", {})
        await repo.update(audit_log, {"seq": 99})
        assert not (await verify_audit(repo))["valid"]
