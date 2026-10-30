from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from arth.core.db import Database
from arth.core.migrate import upgrade


@pytest.fixture
async def db(tmp_path: Path) -> AsyncIterator[Database]:
    path = tmp_path / "arth.db"
    upgrade(path)
    database = Database(path)
    await database.open()
    yield database
    await database.close()


def seed_repo(conn, merchant_id):
    """Trusted test seeding: domain writes otherwise require an executing bus command."""
    from arth.governance.repository import Repository

    repo = Repository(conn, merchant_id)
    repo.command_id = "cmd_fixture"
    return repo
