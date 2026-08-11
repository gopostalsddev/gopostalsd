"""Real-PostgreSQL GP-01 migration and repeated-boot certification.

Set TEST_POSTGRES_ADMIN_URL to an administrative URL for a disposable PostgreSQL
server. The test creates and drops a uniquely named database; it never migrates
the database named in the supplied URL.
"""

import os
from pathlib import Path
import subprocess
import sys
import uuid

import pytest
import sqlalchemy as sa
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory


pytestmark = [pytest.mark.integration, pytest.mark.database, pytest.mark.postgresql]

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _run(command, env):
    return subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
    )


def _production_env(database_url):
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": database_url,
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "SESSION_COOKIE_SECURE": "true",
            "SECRET_KEY": "gp01-test-secret-key-not-for-production",
            "JWT_SECRET_KEY": "gp01-test-jwt-key-not-for-production",
            "SINALITE_BASE_URL": "https://example.invalid",
            "SINALITE_CLIENT_ID": "gp01-test-client",
            "SINALITE_CLIENT_SECRET": "gp01-test-secret",
            "SQUARE_WEBHOOK_SIGNATURE_KEY": "gp01-test-signature",
            "SQUARE_WEBHOOK_URL": "https://example.invalid/api/payments/webhook",
            "SQUARE_ENVIRONMENT": "sandbox",
            "SQUARE_ACCESS_TOKEN": "gp01-test-square-token",
            "SQUARE_APPLICATION_ID": "sandbox-sq0idb-gp01-test",
            "SQUARE_LOCATION_ID": "gp01-test-location",
            "OAUTH_TOKEN_ENCRYPTION_KEY": "gp01-test-oauth-key",
            "SQUARE_MOCK_PAYMENTS": "false",
            "AUTO_ENABLE_CATEGORIES_WHEN_NONE": "false",
            "FRONTEND_URL": "https://example.invalid",
            "BACKEND_URL": "https://example.invalid",
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_KEY": (
                "eyJhbGciOiJIUzI1NiJ9."
                "eyJyb2xlIjoic2VydmljZV9yb2xlIn0."
                "gp01-test-signature"
            ),
            "RUN_DB_MIGRATE": "1",
            "FLASK_APP": "app.py",
        }
    )
    for key in ("ADMIN_EMAIL", "ADMIN_PASSWORD", "ADMIN_FIRST_NAME", "ADMIN_LAST_NAME"):
        env.pop(key, None)
    return env


def _snapshot(engine):
    inspector = sa.inspect(engine)
    tables = sorted(inspector.get_table_names(schema="public"))
    with engine.connect() as connection:
        counts = {
            table: connection.execute(
                sa.text(f'SELECT count(*) FROM "{table}"')
            ).scalar_one()
            for table in tables
        }
    return {
        "tables": tables,
        "columns": {
            table: sorted(column["name"] for column in inspector.get_columns(table))
            for table in tables
        },
        "counts": counts,
    }


def test_empty_postgres_migrates_bootstraps_and_boots_twice_without_mutation():
    admin_url_value = os.getenv("TEST_POSTGRES_ADMIN_URL")
    if not admin_url_value:
        pytest.skip("TEST_POSTGRES_ADMIN_URL is required for real PostgreSQL certification")

    admin_url = sa.engine.make_url(admin_url_value)
    if not admin_url.drivername.startswith("postgresql"):
        pytest.fail("TEST_POSTGRES_ADMIN_URL must use PostgreSQL")

    database_name = f"gopostal_gp01_{uuid.uuid4().hex[:12]}"
    test_url = admin_url.set(database=database_name)
    test_url_value = test_url.render_as_string(hide_password=False)
    admin_engine = sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")
    test_engine = None

    try:
        with admin_engine.connect() as connection:
            connection.exec_driver_sql(f'CREATE DATABASE "{database_name}"')

        env = _production_env(test_url_value)
        migration_result = _run(
            [sys.executable, "-m", "flask", "db", "upgrade"], env
        )

        alembic_config = AlembicConfig(str(BACKEND_DIR / "migrations" / "alembic.ini"))
        alembic_config.set_main_option(
            "script_location", str(BACKEND_DIR / "migrations")
        )
        heads = ScriptDirectory.from_config(alembic_config).get_heads()
        assert heads == ["gp06_square_webhook_inbox"]

        test_engine = sa.create_engine(test_url)
        assert sa.inspect(test_engine).has_table("alembic_version"), (
            "flask db upgrade exited successfully without creating "
            "alembic_version\n"
            f"stdout:\n{migration_result.stdout}\n"
            f"stderr:\n{migration_result.stderr}"
        )
        with test_engine.connect() as connection:
            current = connection.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalars().all()
        assert current == heads

        # Required data is deliberate and separate from schema upgrade.
        bootstrap_env = env.copy()
        bootstrap_env.pop("RUN_DB_MIGRATE", None)
        _run([sys.executable, "-m", "flask", "bootstrap-data"], bootstrap_env)
        before_boot = _snapshot(test_engine)

        boot_command = [
            sys.executable,
            "-c",
            "from app import app; assert not app.config['MIGRATION_MODE']; print('boot-ok')",
        ]
        _run(boot_command, bootstrap_env)
        after_first_boot = _snapshot(test_engine)
        _run(boot_command, bootstrap_env)
        after_second_boot = _snapshot(test_engine)

        assert after_first_boot == before_boot
        assert after_second_boot == before_boot

        # Repeating explicit bootstrap is also idempotent.
        _run([sys.executable, "-m", "flask", "bootstrap-data"], bootstrap_env)
        assert _snapshot(test_engine) == before_boot
    finally:
        if test_engine is not None:
            test_engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(
                sa.text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :database_name AND pid <> pg_backend_pid()"
                ),
                {"database_name": database_name},
            )
            connection.exec_driver_sql(f'DROP DATABASE IF EXISTS "{database_name}"')
        admin_engine.dispose()
