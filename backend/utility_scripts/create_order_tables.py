"""Retired direct-schema utility.

Order tables are owned by Alembic's ``create_order_management_tables``
migration.  Keeping a direct ``Table.create``/``Table.drop`` path would allow
deployed schema to diverge from the recorded Alembic revision.
"""

import sys


MESSAGE = (
    "This utility is retired. Use `flask db upgrade` (or backend/migrate.sh) "
    "to create/order database schema. Direct table create/drop is prohibited."
)


def create_order_tables():
    raise RuntimeError(MESSAGE)


def drop_order_tables():
    raise RuntimeError(MESSAGE)


if __name__ == "__main__":
    print(MESSAGE, file=sys.stderr)
    raise SystemExit(2)
