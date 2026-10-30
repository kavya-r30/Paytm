from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

import arth.core.tables  # noqa: F401  (registers tables on metadata)
from arth.core.db import metadata
from arth.core.migrate import upgrade


def test_migrations_match_models(tmp_path: Path) -> None:
    path = tmp_path / "drift.db"
    upgrade(path)
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    try:
        with engine.connect() as conn:
            ctx = MigrationContext.configure(
                conn,
                opts={
                    "compare_type": True,
                    "include_object": lambda obj, name, type_, reflected, compare_to: (
                        not (name == "items_fts" or name.startswith("items_fts_"))
                    ),
                },
            )
            assert compare_metadata(ctx, metadata) == []
    finally:
        engine.dispose()


def test_upgrade_handles_percent_in_path(tmp_path: Path) -> None:
    path = tmp_path / "a%20b" / "arth.db"
    upgrade(path)
    assert path.is_file()
