"""SQLite access: WAL, one writer at a time, many readers, snapshot and restore (spec v5.1 D2)."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

RESTORE_READER_TIMEOUT = 5.0

# busy_timeout first so the remaining pragmas (journal_mode needs a lock) already wait on contention.
PRAGMAS = (
    "PRAGMA busy_timeout=5000",
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA foreign_keys=ON",
)


def _apply_pragmas(dbapi_connection: Any, _record: Any) -> None:
    cursor = dbapi_connection.cursor()
    for pragma in PRAGMAS:
        cursor.execute(pragma)
    cursor.close()


def _vacuum_into(src: Path, dest: Path) -> None:
    conn = sqlite3.connect(src)
    try:
        escaped = dest.as_posix().replace("'", "''")
        conn.execute(f"VACUUM INTO '{escaped}'")
    finally:
        conn.close()


def _backup_into(src: Path, dest: Path) -> None:
    """Copy src over dest in place with SQLite's online backup API (transactional: all or nothing)."""
    src_conn = sqlite3.connect(f"{src.resolve().as_uri()}?mode=ro", uri=True)
    try:
        src_conn.execute("SELECT count(*) FROM sqlite_master").fetchone()  # raises if not a SQLite DB
        dest_conn = sqlite3.connect(dest, timeout=5.0)
        try:
            src_conn.backup(dest_conn)
        finally:
            dest_conn.close()
    finally:
        src_conn.close()


class Database:
    """Async SQLite wrapper: one writer at a time, many readers, snapshot and in-place restore.

    The write lock and reader gate are per-process (per event loop) asyncio primitives. Contention
    from another process is not coordinated here; it relies on SQLite's busy_timeout.

    Rules: always go through `read()`/`write()` (using `engine.connect()` directly bypasses the
    restore gate); don't nest `read()` inside `read()` (a restore starting in between waits for the
    outer reader and aborts after the timeout); never call `restore()`/`snapshot()` inside `write()`
    (the write lock is not reentrant).
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._engine: AsyncEngine | None = None
        self._write_lock = asyncio.Lock()
        self._gate = asyncio.Condition()
        self._readers = 0
        self._restoring = False

    async def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_async_engine(f"sqlite+aiosqlite:///{self.path.as_posix()}")
        event.listen(engine.sync_engine, "connect", _apply_pragmas)
        self._engine = engine

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Database.open() has not been called")
        return self._engine

    @asynccontextmanager
    async def read(self) -> AsyncIterator[AsyncConnection]:
        """Reader connection; waits while a restore is in progress and is counted so restore can drain."""
        async with self._gate:
            await self._gate.wait_for(lambda: not self._restoring)
            self._readers += 1
        try:
            async with self.engine.connect() as conn:
                yield conn
        finally:
            async with self._gate:
                self._readers -= 1
                self._gate.notify_all()

    @asynccontextmanager
    async def write(self) -> AsyncIterator[AsyncConnection]:
        """One writer at a time; the block commits on success and rolls back on error."""
        async with self._write_lock, self.engine.begin() as conn:
            yield conn

    async def snapshot(self, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with self._write_lock:
            dest.unlink(missing_ok=True)
            await asyncio.to_thread(_vacuum_into, self.path, dest)

    async def restore(self, src: Path) -> None:
        """Replace the live DB contents with a snapshot, in place (no file swap under open handles)."""
        if not src.is_file():
            raise FileNotFoundError(f"snapshot not found: {src}")
        async with self._write_lock:
            async with self._gate:
                self._restoring = True
            try:
                async with self._gate:
                    try:
                        await asyncio.wait_for(
                            self._gate.wait_for(lambda: self._readers == 0), RESTORE_READER_TIMEOUT
                        )
                    except TimeoutError as exc:
                        raise RuntimeError(
                            f"restore aborted: {self._readers} reader(s) still active after "
                            f"{RESTORE_READER_TIMEOUT}s"
                        ) from exc
                try:
                    await asyncio.to_thread(_backup_into, src, self.path)
                except sqlite3.Error as exc:
                    raise RuntimeError(f"restore failed, live database unchanged: {exc}") from exc
                await self.engine.dispose()
            finally:
                async with self._gate:
                    self._restoring = False
                    self._gate.notify_all()
