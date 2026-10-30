from alembic import context
from sqlalchemy import engine_from_config, pool

# Every new table module must be imported here so its tables register on metadata;
# otherwise autogenerate and the schema-drift test will not see them.
import arth.core.tables  # noqa: F401  (registers L0 tables on metadata)
import arth.governance.tables  # noqa: F401
import arth.domains.tables  # noqa: F401
import arth.domains.stock_tables  # noqa: F401
import arth.domains.patron_tables  # noqa: F401
import arth.domains.ledger_tables  # noqa: F401
import arth.domains.commerce_tables  # noqa: F401
import arth.sim.tables  # noqa: F401
from arth.core.db import metadata

config = context.config
target_metadata = metadata


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
