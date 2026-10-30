"""Run Alembic migrations programmatically (app boot, tests, scenario snapshots)."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from alembic import command
from alembic.config import Config

from arth.core.paths import BACKEND_DIR


def upgrade(db_path: Path, revision: str = "head") -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    # URL-quote (SQLAlchemy unquotes the path), then escape % for configparser interpolation.
    cfg.set_main_option(
        "sqlalchemy.url", f"sqlite:///{quote(db_path.as_posix(), safe='/:')}".replace("%", "%%")
    )
    command.upgrade(cfg, revision)
