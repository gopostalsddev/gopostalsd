"""Real-PostgreSQL certification for the irreversible GP-02 auth migration."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import pytest
import sqlalchemy as sa

from auth_migration_preflight import MIGRATION_REVISION, run_preflight


pytestmark = [pytest.mark.integration, pytest.mark.database, pytest.mark.postgresql]

BACKEND_DIR = Path(__file__).resolve().parents[1]
PARENT_REVISION = "b6dd5b87b433"
SAFE_EMAIL = "safe.user@example.test"
SAFE_PASSWORD = "SafePass1!"
SALT = "a" * 64
SYNTHETIC_SUPABASE_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJyb2xlIjoic2VydmljZV9yb2xlIn0."
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
)
SAFE_HASH = (
    SALT
    + ":"
    + hashlib.pbkdf2_hmac(
        "sha256", SAFE_PASSWORD.encode(), SALT.encode(), 100000
    ).hex()
)


def _run(command, env, *, check=True):
    return subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=env,
        check=check,
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
            "SECRET_KEY": "gp02-test-secret-key-not-for-production",
            "JWT_SECRET_KEY": "gp02-test-jwt-key-not-for-production",
            "SINALITE_BASE_URL": "https://example.invalid",
            "SINALITE_CLIENT_ID": "gp02-test-client",
            "SINALITE_CLIENT_SECRET": "gp02-test-secret",
            "SQUARE_WEBHOOK_SIGNATURE_KEY": "gp02-test-signature",
            "SQUARE_WEBHOOK_URL": "https://example.invalid/api/payments/webhook",
            "SQUARE_ENVIRONMENT": "sandbox",
            "SQUARE_ACCESS_TOKEN": "gp02-test-square-token",
            "SQUARE_APPLICATION_ID": "sandbox-sq0idb-gp02-test",
            "SQUARE_LOCATION_ID": "gp02-test-location",
            "OAUTH_TOKEN_ENCRYPTION_KEY": "gp02-test-oauth-key",
            "SQUARE_MOCK_PAYMENTS": "false",
            "AUTO_ENABLE_CATEGORIES_WHEN_NONE": "false",
            "FRONTEND_URL": "https://example.invalid",
            "BACKEND_URL": "https://example.invalid",
            "PUBLIC_BASE_URL": "https://launch.example.test",
            "TRUSTED_PROXY_HOPS": "1",
            "EMAIL_PROVIDER": "mailersend",
            "EMAIL_FROM_ADDRESS": "support@uzimaprints.com",
            "EMAIL_FROM_NAME": "Uzima Prints",
            "MAILERSEND_API_KEY": "gp02-test-mailersend-key",
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_KEY": SYNTHETIC_SUPABASE_JWT,
            "SUPABASE_BUCKET": "gp02-test-bucket",
            "FILE_STORAGE_BACKEND": "supabase",
            "SUPABASE_KEY": SYNTHETIC_SUPABASE_JWT,
            "RUN_DB_MIGRATE": "1",
            "FLASK_APP": "app.py",
        }
    )
    for key in ("ADMIN_EMAIL", "ADMIN_PASSWORD", "ADMIN_FIRST_NAME", "ADMIN_LAST_NAME"):
        env.pop(key, None)
    return env


def _admin_url():
    value = os.getenv("TEST_POSTGRES_ADMIN_URL")
    if not value:
        pytest.skip("TEST_POSTGRES_ADMIN_URL is required for real PostgreSQL certification")
    url = sa.engine.make_url(value)
    if not url.drivername.startswith("postgresql"):
        pytest.fail("TEST_POSTGRES_ADMIN_URL must use PostgreSQL")
    return url


@contextmanager
def _legacy_database():
    admin_url = _admin_url()
    database_name = f"gopostal_gp02_{uuid.uuid4().hex[:12]}"
    database_url = admin_url.set(database=database_name)
    database_url_value = database_url.render_as_string(hide_password=False)
    admin_engine = sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")
    engine = None
    try:
        with admin_engine.connect() as connection:
            connection.exec_driver_sql(f'CREATE DATABASE "{database_name}"')

        env = _production_env(database_url_value)
        _run(
            [sys.executable, "-m", "flask", "db", "upgrade", PARENT_REVISION],
            env,
        )
        engine = sa.create_engine(database_url)
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"
            )
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN status VARCHAR(32) NOT NULL"
            )
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL"
            )
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN created_at TIMESTAMP NOT NULL"
            )
            connection.execute(
                sa.text(
                    "INSERT INTO addresses "
                    "(id, street, city, state, zip_code, country, apt) "
                    "VALUES (1, 'Safe Street', 'Safe City', 'CA', 92101, 'US', NULL)"
                )
            )
            connection.execute(
                sa.text(
                    "INSERT INTO roles (id, name, description) "
                    "VALUES (1, 'Customer', 'Safe fixture')"
                )
            )
            connection.execute(
                sa.text(
                    "INSERT INTO users "
                    "(id, first_name, last_name, email_address, creation_date, "
                    " shipping_address_id, billing_address_id, role_id, "
                    " password_hash, status, email_verified, created_at) "
                    "VALUES (1, 'Safe', 'User', :email, now(), 1, 1, 1, "
                    " :hash, 'ACTIVE', true, now())"
                ),
                {"email": SAFE_EMAIL, "hash": SAFE_HASH},
            )
            # A PostgreSQL dump/restore preserves sequence positions. These
            # synthetic legacy rows use explicit IDs, so model that state
            # explicitly instead of leaving the next role insert at ID 1.
            for table_name in ("addresses", "roles", "users"):
                connection.execute(
                    sa.text(
                        "SELECT setval("
                        "pg_get_serial_sequence(:table_name, 'id'), "
                        f"(SELECT max(id) FROM {table_name}), true)"
                    ),
                    {"table_name": table_name},
                )
        yield engine, env, admin_engine, database_name, database_url
    finally:
        if engine is not None:
            engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(
                sa.text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :database_name AND pid <> pg_backend_pid()"
                ),
                {"database_name": database_name},
            )
            connection.exec_driver_sql(f'DROP DATABASE IF EXISTS "{database_name}"')
            connection.exec_driver_sql(
                f'DROP ROLE IF EXISTS "{database_name}_reader"'
            )
        admin_engine.dispose()


def _finding(report, category):
    return next(item for item in report.findings if item.category == category)


def _snapshot(engine):
    inspector = sa.inspect(engine)
    tables = sorted(inspector.get_table_names())
    with engine.connect() as connection:
        revision = connection.execute(
            sa.text("SELECT version_num FROM alembic_version")
        ).scalar_one()
        counts = {
            table: connection.execute(
                sa.text(f'SELECT count(*) FROM "{table}"')
            ).scalar_one()
            for table in tables
        }
    return {
        "revision": revision,
        "tables": tables,
        "columns": {
            table: sorted(column["name"] for column in inspector.get_columns(table))
            for table in tables
        },
        "counts": counts,
    }


def _readonly_role(admin_engine, database_name, database_url):
    role = f"{database_name}_reader"
    password = uuid.uuid4().hex
    with admin_engine.begin() as connection:
        connection.exec_driver_sql(f'CREATE ROLE "{role}" LOGIN PASSWORD \'{password}\'')
        connection.exec_driver_sql(
            f'REVOKE TEMPORARY ON DATABASE "{database_name}" FROM PUBLIC'
        )
        connection.exec_driver_sql(f'GRANT CONNECT ON DATABASE "{database_name}" TO "{role}"')
    owner_engine = sa.create_engine(database_url)
    try:
        with owner_engine.begin() as connection:
            connection.exec_driver_sql("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
            connection.exec_driver_sql(f'GRANT USAGE ON SCHEMA public TO "{role}"')
            connection.exec_driver_sql(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{role}"')
    finally:
        owner_engine.dispose()
    return role, password, database_url.set(username=role, password=password)


def _assert_write_refused(url, statement):
    engine = sa.create_engine(url)
    try:
        with pytest.raises(sa.exc.DBAPIError):
            with engine.begin() as connection:
                connection.exec_driver_sql(statement)
    finally:
        engine.dispose()


def test_safe_preflight_is_repeatable_select_only_and_redacted():
    with _legacy_database() as (engine, env, admin_engine, database_name, url):
        before = _snapshot(engine)
        role, password, readonly_url = _readonly_role(
            admin_engine, database_name, url
        )
        readonly_engine = sa.create_engine(readonly_url)
        try:
            first = run_preflight(readonly_engine)
            second = run_preflight(readonly_engine)
        finally:
            readonly_engine.dispose()

        assert first.passed and second.passed
        assert first.transaction_read_only and second.transaction_read_only
        assert first.to_dict() == second.to_dict()
        assert _snapshot(engine) == before

        readonly_env = env.copy()
        readonly_env["DATABASE_URL"] = readonly_url.render_as_string(
            hide_password=False
        )
        cli = _run(
            [sys.executable, "auth_migration_preflight.py", "--pretty"],
            readonly_env,
        )
        payload = json.loads(cli.stdout)
        assert payload["passed"] is True
        assert payload["transaction_read_only"] is True
        for secret in (SAFE_EMAIL, SAFE_HASH, SAFE_PASSWORD, password, role):
            assert secret not in cli.stdout

        for statement in (
            "INSERT INTO accounts (username) VALUES ('forbidden')",
            "UPDATE users SET first_name = 'Forbidden' WHERE id = 1",
            "DELETE FROM users WHERE id = 1",
            "CREATE TABLE forbidden_table (id integer)",
            "ALTER TABLE users ADD COLUMN forbidden integer",
            "DROP TABLE accounts",
            "TRUNCATE TABLE users",
            "UPDATE alembic_version SET version_num = 'forbidden'",
        ):
            _assert_write_refused(readonly_url, statement)
        assert _snapshot(engine) == before


UNSAFE_FIXTURES = (
    (
        "users.null_or_blank_final_email",
        "UPDATE users SET email_address = '' WHERE id = 1",
    ),
    (
        "users.invalid_final_email",
        "UPDATE users SET email_address = 'not-an-email' WHERE id = 1",
    ),
    (
        "users.final_email_too_long",
        "ALTER TABLE users ALTER COLUMN email_address TYPE text; "
        "UPDATE users SET email_address = repeat('a', 121) WHERE id = 1",
    ),
    (
        "users.missing_email_source",
        "ALTER TABLE users DROP COLUMN email_address",
    ),
    (
        "users.creation_timestamp_would_be_lost",
        "ALTER TABLE users DROP COLUMN created_at",
    ),
    (
        "users.missing_status_source",
        "ALTER TABLE users DROP COLUMN status",
    ),
    (
        "users.missing_verification_state",
        "ALTER TABLE users DROP COLUMN email_verified",
    ),
    (
        "users.noncanonical_final_email",
        "UPDATE users SET email_address = ' safe.user@example.test ' WHERE id = 1",
    ),
    (
        "users.duplicate_final_email",
        "INSERT INTO users "
        "(id, first_name, last_name, email_address, creation_date, "
        " shipping_address_id, billing_address_id, role_id, password_hash, status, "
        " email_verified, created_at) "
        "VALUES (2, 'Other', 'User', 'SAFE.USER@example.test', now(), "
        f"1, 1, 1, '{SAFE_HASH}', 'ACTIVE', true, now())",
    ),
    (
        "users.normalized_identity_collision",
        "ALTER TABLE users ADD COLUMN email VARCHAR(120); "
        "UPDATE users SET email = 'Case@example.test' WHERE id = 1; "
        "INSERT INTO users "
        "(id, first_name, last_name, email_address, email, creation_date, "
        " shipping_address_id, billing_address_id, role_id, password_hash, status, "
        " email_verified, created_at) "
        "VALUES (2, 'Other', 'User', 'other@example.test', "
        f"' case@example.test ', now(), 1, 1, 1, '{SAFE_HASH}', 'ACTIVE', true, now())",
    ),
    (
        "users.credentialless_accounts",
        "UPDATE users SET password_hash = NULL WHERE id = 1",
    ),
    (
        "users.malformed_password_hash",
        "UPDATE users SET password_hash = 'plaintext' WHERE id = 1",
    ),
    (
        "users.invalid_status",
        "UPDATE users SET status = 'UNKNOWN' WHERE id = 1",
    ),
    (
        "users.status_type_incompatible",
        "ALTER TABLE users ALTER COLUMN status TYPE integer USING 1",
    ),
    (
        "roles.orphaned_user_assignments",
        "ALTER TABLE users DROP CONSTRAINT users_role_id_fkey; "
        "UPDATE users SET role_id = 999 WHERE id = 1",
    ),
    (
        "roles.normalized_name_collisions",
        "INSERT INTO roles (id, name, description) "
        "VALUES (2, ' customer ', 'Collision')",
    ),
    (
        "roles.invalid_names",
        "UPDATE roles SET name = '' WHERE id = 1",
    ),
    (
        "legacy.accounts.rows_would_be_dropped",
        "INSERT INTO accounts (username) VALUES ('legacy-user')",
    ),
    (
        "legacy.hashing_algorithms.rows_would_be_dropped",
        "INSERT INTO hashing_algorithms (id) VALUES (1)",
    ),
    (
        "schema.missing_foundational_tables",
        "DROP TABLE users CASCADE",
    ),
)


@pytest.mark.parametrize(("category", "mutation"), UNSAFE_FIXTURES)
def test_each_identified_unsafe_fixture_blocks(category, mutation):
    with _legacy_database() as (engine, _env, _admin, _name, _url):
        with engine.begin() as connection:
            for statement in mutation.split("; "):
                connection.exec_driver_sql(statement)
        report = run_preflight(engine)
        assert report.passed is False
        assert _finding(report, category).count > 0


def test_existing_auth_table_shape_and_duplicate_tokens_block():
    with _legacy_database() as (engine, _env, _admin, _name, _url):
        with engine.begin() as connection:
            connection.exec_driver_sql("CREATE TABLE permissions (id integer PRIMARY KEY)")
            connection.exec_driver_sql(
                "CREATE TABLE user_sessions ("
                "id integer PRIMARY KEY, user_id integer, session_token text, "
                "refresh_token text, expires_at timestamp)"
            )
            connection.exec_driver_sql(
                "INSERT INTO user_sessions VALUES "
                "(1, 1, 'duplicate', 'refresh', now()), "
                "(2, 1, 'duplicate', 'refresh', now())"
            )
            connection.exec_driver_sql(
                "CREATE TABLE oauth_accounts ("
                "id integer PRIMARY KEY, user_id integer, provider text, "
                "provider_user_id text, created_at timestamp, updated_at timestamp)"
            )
            connection.exec_driver_sql(
                "INSERT INTO oauth_accounts VALUES "
                "(1, 1, 'google', 'duplicate', now(), now()), "
                "(2, 999, 'google', 'duplicate', now(), now())"
            )
        report = run_preflight(engine)
        assert report.passed is False
        assert _finding(
            report, "existing_auth.permissions.invalid_shape"
        ).count > 0
        assert _finding(
            report, "existing_auth.user_sessions.duplicate_session_token"
        ).count == 2
        assert _finding(
            report, "existing_auth.user_sessions.duplicate_refresh_token"
        ).count == 2
        assert _finding(
            report, "existing_auth.oauth_accounts.orphaned_users"
        ).count == 1
        assert _finding(
            report, "existing_auth.oauth_accounts.duplicate_provider_identity"
        ).count == 2


def test_valid_oauth_identity_allows_account_without_local_password():
    with _legacy_database() as (engine, _env, _admin, _name, _url):
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "CREATE TABLE oauth_accounts ("
                "id integer PRIMARY KEY, user_id integer NOT NULL REFERENCES users(id), "
                "provider varchar(50) NOT NULL, provider_user_id varchar(255) NOT NULL, "
                "provider_email varchar(120), access_token text, refresh_token text, "
                "token_expires_at timestamp, created_at timestamp NOT NULL, "
                "updated_at timestamp NOT NULL, UNIQUE (provider, provider_user_id))"
            )
            connection.exec_driver_sql(
                "INSERT INTO oauth_accounts "
                "(id, user_id, provider, provider_user_id, created_at, updated_at) "
                "VALUES (1, 1, 'google', 'safe-provider-id', now(), now())"
            )
            connection.exec_driver_sql(
                "UPDATE users SET password_hash = NULL WHERE id = 1"
            )
        report = run_preflight(engine)
        assert report.passed is True
        assert _finding(report, "users.credentialless_accounts").count == 0


def test_safe_fixture_migrates_and_authentication_state_survives_to_head():
    with _legacy_database() as (engine, env, admin_engine, database_name, url):
        _role, _password, readonly_url = _readonly_role(
            admin_engine, database_name, url
        )
        readonly_engine = sa.create_engine(readonly_url)
        try:
            assert run_preflight(readonly_engine).passed
        finally:
            readonly_engine.dispose()

        _run(
            [sys.executable, "-m", "flask", "db", "upgrade", MIGRATION_REVISION],
            env,
        )
        inspector = sa.inspect(engine)
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        assert "email" in user_columns
        assert "email_address" not in user_columns
        assert "creation_date" not in user_columns
        assert not inspector.has_table("accounts")
        assert not inspector.has_table("hashing_algorithms")
        for table in (
            "permissions",
            "user_sessions",
            "password_reset_tokens",
            "oauth_accounts",
            "email_verification_tokens",
        ):
            assert inspector.has_table(table)

        with engine.begin() as connection:
            row = connection.execute(
                sa.text(
                    "SELECT email, password_hash, status FROM users WHERE id = 1"
                )
            ).mappings().one()
            assert row == {
                "email": SAFE_EMAIL,
                "password_hash": SAFE_HASH,
                "status": "active",
            }
            connection.execute(
                sa.text("UPDATE users SET email_verified = true WHERE id = 1")
            )

        auth_env = env.copy()
        auth_env.pop("RUN_DB_MIGRATE", None)
        auth_check = (
            "from app import app; "
            "from server.models.auth import User, UserStatus; "
            "from server.services.password_service import PasswordService; "
            "ctx=app.app_context(); ctx.push(); "
            f"u=User.query.filter_by(email='{SAFE_EMAIL}').one(); "
            "assert u.status is UserStatus.ACTIVE; "
            "assert u.can_login(); "
            f"assert PasswordService().verify_password('{SAFE_PASSWORD}', u.password_hash); "
            "ctx.pop(); print('auth-ok')"
        )
        assert "auth-ok" in _run([sys.executable, "-c", auth_check], auth_env).stdout

        _run([sys.executable, "-m", "flask", "db", "upgrade"], env)
        _run([sys.executable, "-m", "flask", "bootstrap-data"], auth_env)
        _run(
            [
                sys.executable,
                "-c",
                "from app import app; assert not app.config['MIGRATION_MODE']; print('boot-ok')",
            ],
            auth_env,
        )
        with engine.connect() as connection:
            assert connection.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalar_one() == "gp08_refund_attempts"
