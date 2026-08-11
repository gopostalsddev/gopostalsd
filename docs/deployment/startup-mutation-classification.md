# Startup mutation classification

Alembic is the only schema-migration authority. Flask application creation is
side-effect free with respect to database schema and business data.

| Previous behavior | Classification | GP-01 disposition |
|---|---|---|
| Runtime `PricingPolicy.__table__.create()` | Schema migration | Adopted by `gp01_pricing_policy`; removed from startup |
| Unclassified product type ID 0 | Schema/migration state | Existing migration remains authoritative; explicit bootstrap verifies, never recreates it |
| Default `PricingPolicy` row | Required application bootstrap data | Created by explicit, idempotent `flask bootstrap-data` after migration |
| Default type for a category with none | Required application bootstrap data | Explicit, idempotent `flask bootstrap-data`; never automatic boot |
| Enable all categories when none enabled | Business bootstrap policy | Explicit opt-in `flask bootstrap-data --enable-categories-if-none` |
| Production admin | Required one-time administrative bootstrap | Explicit `flask bootstrap-admin`; credentials removed afterward |
| `utility_scripts/create_order_tables.py` direct table create/drop | Legacy/dead schema bypass | Must not be used; Alembic order migration is authoritative |
| `utility_scripts/setup_database.py` | Legacy deployment helper | Compatibility only; production deployment uses `migrate.sh` then explicit bootstrap commands |

Required deployment sequence:

1. Start/verify an empty or restored PostgreSQL database.
2. Run `backend/migrate.sh` as a one-shot step.
3. Assert Alembic current revision equals its single head.
4. Run `flask bootstrap-data` deliberately.
5. Optionally run `flask bootstrap-admin` once, then remove `ADMIN_*`.
6. Start Gunicorn with `backend/deploy.sh`.

Do not run `db.create_all()` or the legacy order-table utility in any deployed
environment.
