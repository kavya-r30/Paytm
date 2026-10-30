import asyncio
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import func, insert, select, text

from arth.core.db import Database
from arth.core.tables import jobs


def job_row(job_id: str) -> dict:
    return {"id": job_id, "name": "t", "due_at": "2026-10-29T16:30:00.000000Z", "payload": "{}"}


async def test_pragmas_are_applied(db: Database) -> None:
    async with db.read() as conn:
        assert (await conn.execute(text("PRAGMA journal_mode"))).scalar() == "wal"
        assert (await conn.execute(text("PRAGMA foreign_keys"))).scalar() == 1
        assert (await conn.execute(text("PRAGMA synchronous"))).scalar() == 1
        assert (await conn.execute(text("PRAGMA busy_timeout"))).scalar() == 5000


async def test_migration_creates_l0_tables(db: Database) -> None:
    async with db.read() as conn:
        names = {
            row[0] for row in await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        }
    assert {"jobs", "spans", "alembic_version"} <= names


async def test_write_then_read(db: Database) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    async with db.read() as conn:
        assert (await conn.execute(select(func.count()).select_from(jobs))).scalar() == 1


async def test_snapshot_and_restore_round_trip(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "snapshots" / "scene-1.db"
    await db.snapshot(snap)
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))
    await db.restore(snap)
    async with db.read() as conn:
        assert (await conn.execute(select(func.count()).select_from(jobs))).scalar() == 1


async def count_jobs(db: Database) -> int:
    async with db.read() as conn:
        return (await conn.execute(select(func.count()).select_from(jobs))).scalar_one()


async def test_write_rolls_back_on_exception(db: Database) -> None:
    with pytest.raises(RuntimeError):
        async with db.write() as conn:
            await conn.execute(insert(jobs).values(**job_row("job_1")))
            raise RuntimeError("boom")
    assert await count_jobs(db) == 0


async def test_snapshot_includes_data_still_in_wal(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "wal.db"
    await db.snapshot(snap)
    check = sqlite3.connect(snap)
    try:
        assert check.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
    finally:
        check.close()


async def test_restore_waits_for_in_flight_reader(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "s.db"
    await db.snapshot(snap)
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))

    restore_task: asyncio.Task[None]
    async with db.read() as conn:
        assert (await conn.execute(select(func.count()).select_from(jobs))).scalar() == 2
        restore_task = asyncio.create_task(db.restore(snap))
        await asyncio.sleep(0.2)
        assert not restore_task.done()  # blocked on our open reader
        late_reader = asyncio.create_task(count_jobs(db))
        await asyncio.sleep(0.1)
        assert not late_reader.done()  # new readers are gated during restore
    await restore_task
    assert await late_reader == 1


async def test_restore_then_write_works_and_matches_snapshot(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    snap = tmp_path / "s.db"
    await db.snapshot(snap)
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))
    await db.restore(snap)
    async with db.read() as conn:
        ids = {r[0] for r in await conn.execute(select(jobs.c.id))}
        assert ids == {"job_1"}
        assert (await conn.execute(text("PRAGMA journal_mode"))).scalar() == "wal"
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_3")))
    assert await count_jobs(db) == 2


async def test_restore_times_out_with_stuck_reader(
    db: Database, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import arth.core.db as db_mod

    monkeypatch.setattr(db_mod, "RESTORE_READER_TIMEOUT", 0.2)
    snap = tmp_path / "s.db"
    await db.snapshot(snap)
    async with db.read():
        with pytest.raises(RuntimeError, match="reader"):
            await db.restore(snap)
    assert await count_jobs(db) == 0  # gate released; reads work again


async def test_restore_missing_file_leaves_db_untouched(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    with pytest.raises(FileNotFoundError, match="nope.db"):
        await db.restore(tmp_path / "nope.db")
    assert await count_jobs(db) == 1


async def test_restore_bad_file_leaves_db_untouched(db: Database, tmp_path: Path) -> None:
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_1")))
    bad = tmp_path / "bad.db"
    bad.write_bytes(b"this is not a sqlite database" * 100)
    with pytest.raises(RuntimeError, match="live database unchanged"):
        await db.restore(bad)
    assert await count_jobs(db) == 1
    async with db.write() as conn:
        await conn.execute(insert(jobs).values(**job_row("job_2")))
    assert await count_jobs(db) == 2
