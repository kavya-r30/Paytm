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
