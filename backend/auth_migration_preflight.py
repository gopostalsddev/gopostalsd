"""Read-only safety preflight for auth migration ``f3a5c1d8e9b0``.

This module deliberately lives outside the Flask application package. Running
it must not initialize integrations, register routes, seed data, or otherwise
require an application boot. Only aggregate counts and category names are
reported; identity values and authentication secrets never leave PostgreSQL.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
import re
from typing import Iterable

import sqlalchemy as sa


MIGRATION_REVISION = "f3a5c1d8e9b0"
PARENT_REVISION = "b6dd5b87b433"
VALID_STATUSES = (
    "pending_verification",
    "active",
    "suspended",
    "deactivated",
)
PASSWORD_HASH_PATTERN = r"^[0-9A-Fa-f]{64}:[0-9A-Fa-f]{64}$"
EMAIL_PATTERN = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"


@dataclass(frozen=True)
class Finding:
    category: str
    count: int
    blocking: bool
    description: str


@dataclass(frozen=True)
class PreflightReport:
    migration_revision: str
    parent_revision: str
    passed: bool
    transaction_read_only: bool
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict:
        return {
            "migration_revision": self.migration_revision,
            "parent_revision": self.parent_revision,
            "passed": self.passed,
            "transaction_read_only": self.transaction_read_only,
            "findings": [asdict(finding) for finding in self.findings],
        }


class _Collector:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def add(self, category: str, count: int, description: str) -> None:
        self.findings.append(
            Finding(
                category=category,
                count=int(count),
                blocking=int(count) > 0,
                description=description,
            )
        )


def _scalar(
    connection,
    statement: str | sa.sql.elements.TextClause,
    parameters: dict | None = None,
) -> int:
    query = sa.text(statement) if isinstance(statement, str) else statement
    return int(
        connection.execute(query, parameters or {}).scalar_one() or 0
    )


def _columns(inspector, table: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table)}


def _email_expression(user_columns: set[str]) -> str | None:
    has_email = "email" in user_columns
    has_legacy = "email_address" in user_columns
    if has_email and has_legacy:
        return (
            "CASE WHEN email IS NULL OR email = '' "
            "THEN lower(email_address) ELSE email END"
        )
    if has_email:
        return "email"
    if has_legacy:
        return "lower(email_address)"
    return None


def _missing_columns(
    collector: _Collector,
    inspector,
    table: str,
    required: Iterable[str],
) -> set[str]:
    columns = _columns(inspector, table)
    missing = set(required) - columns
    collector.add(
        f"schema.{table}.missing_required_columns",
        len(missing),
        f"{table} lacks columns required by the migration or post-migration model.",
    )
    return columns


def _check_existing_auth_table(
    collector: _Collector,
    connection,
    inspector,
    table: str,
    required_columns: tuple[str, ...],
    unique_columns: tuple[str, ...] = (),
    required_unique_keys: tuple[tuple[str, ...], ...] = (),
) -> None:
    if not inspector.has_table(table):
        collector.add(
            f"existing_auth.{table}.invalid_shape",
            0,
            f"{table} is absent and will be created by the migration.",
        )
        return

    columns = _columns(inspector, table)
    missing = set(required_columns) - columns
    missing_user_fk = 0
    if "user_id" in required_columns and "user_id" in columns:
        missing_user_fk = int(
            not any(
                foreign_key.get("referred_table") == "users"
                and tuple(foreign_key.get("constrained_columns") or ())
                == ("user_id",)
                for foreign_key in inspector.get_foreign_keys(table)
            )
        )
    unique_keys = {
        tuple(constraint.get("column_names") or ())
        for constraint in inspector.get_unique_constraints(table)
    }
    unique_keys.update(
        tuple(index.get("column_names") or ())
        for index in inspector.get_indexes(table)
        if index.get("unique")
    )
    missing_unique_keys = sum(
        1 for key in required_unique_keys if key not in unique_keys
    )
    collector.add(
        f"existing_auth.{table}.invalid_shape",
        len(missing) + missing_user_fk + missing_unique_keys,
        f"Existing {table} lacks required columns, relationships, or uniqueness.",
    )
    if missing:
        return

    if "user_id" in columns:
        collector.add(
            f"existing_auth.{table}.orphaned_users",
            _scalar(
                connection,
                f'SELECT count(*) FROM "{table}" child '
                'LEFT JOIN users parent ON parent.id = child.user_id '
                'WHERE child.user_id IS NULL OR parent.id IS NULL',
            ),
            f"Existing {table} contains rows without a valid user.",
        )

    for column in unique_columns:
        if column not in columns:
            continue
        collector.add(
            f"existing_auth.{table}.duplicate_{column}",
            _scalar(
                connection,
                f'SELECT COALESCE(sum(group_count), 0) FROM ('
                f'SELECT count(*) AS group_count FROM "{table}" '
                f'WHERE "{column}" IS NOT NULL '
                f'GROUP BY "{column}" HAVING count(*) > 1) duplicates',
            ),
            f"Existing {table}.{column} values would violate a unique index.",
        )


def run_preflight(engine: sa.Engine) -> PreflightReport:
    """Inspect migration preconditions inside a transaction forced read-only."""
    if engine.dialect.name != "postgresql":
        raise ValueError("The auth migration preflight requires PostgreSQL")

    collector = _Collector()
    with engine.connect() as connection:
        # This must be the first statement: PostgreSQL rejects changing the
        # transaction mode after a query or write has run.
        connection.exec_driver_sql("SET TRANSACTION READ ONLY")
        transaction_read_only = (
            connection.exec_driver_sql("SHOW transaction_read_only").scalar_one()
            == "on"
        )
        inspector = sa.inspect(connection)

        if inspector.has_table("alembic_version"):
            revisions = connection.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalars().all()
            revision_mismatch = int(revisions != [PARENT_REVISION])
        else:
            revision_mismatch = 1
        collector.add(
            "schema.unexpected_alembic_revision",
            revision_mismatch,
            "Database must be at the migration's single direct parent revision.",
        )

        required_tables = ("users", "roles", "addresses")
        missing_tables = [
            table for table in required_tables if not inspector.has_table(table)
        ]
        collector.add(
            "schema.missing_foundational_tables",
            len(missing_tables),
            "Foundational users, roles, and addresses tables must already exist.",
        )

        if inspector.has_table("users"):
            user_columns = _missing_columns(
                collector,
                inspector,
                "users",
                ("id", "first_name", "last_name", "role_id"),
            )
            user_count = _scalar(connection, "SELECT count(*) FROM users")
            collector.add(
                "users.creation_timestamp_would_be_lost",
                user_count
                if "creation_date" in user_columns and "created_at" not in user_columns
                else 0,
                "The migration would drop creation_date without copying it into a newly added created_at column.",
            )
            collector.add(
                "users.missing_status_source",
                user_count if "status" not in user_columns else 0,
                "Existing users have no explicit status and would all receive a default state.",
            )
            collector.add(
                "users.missing_verification_state",
                user_count if "email_verified" not in user_columns else 0,
                "Existing users have no verification state and would all become unverified.",
            )
            email_expression = _email_expression(user_columns)
            collector.add(
                "users.missing_email_source",
                int(email_expression is None),
                "Neither email nor legacy email_address can supply the final identity.",
            )
            if email_expression is not None:
                collector.add(
                    "users.null_or_blank_final_email",
                    _scalar(
                        connection,
                        f"SELECT count(*) FROM users WHERE ({email_expression}) IS NULL "
                        f"OR btrim(({email_expression})) = ''",
                    ),
                    "Projected final email is null or blank.",
                )
                collector.add(
                    "users.invalid_final_email",
                    _scalar(
                        connection,
                        f"SELECT count(*) FROM users WHERE ({email_expression}) IS NOT NULL "
                        f"AND btrim(({email_expression})) <> '' "
                        f"AND NOT (btrim(({email_expression})) ~ :pattern)",
                        {"pattern": EMAIL_PATTERN},
                    ),
                    "Projected final email is incompatible with application validation.",
                )
                collector.add(
                    "users.final_email_too_long",
                    _scalar(
                        connection,
                        f"SELECT count(*) FROM users "
                        f"WHERE length(({email_expression})) > 120",
                    ),
                    "Projected final email exceeds the target column length.",
                )
                collector.add(
                    "users.noncanonical_final_email",
                    _scalar(
                        connection,
                        f"SELECT count(*) FROM users "
                        f"WHERE ({email_expression}) IS NOT NULL "
                        f"AND ({email_expression}) <> lower(btrim(({email_expression})))",
                    ),
                    "Projected email differs from the identity normalization used at login.",
                )
                collector.add(
                    "users.duplicate_final_email",
                    _scalar(
                        connection,
                        "SELECT COALESCE(sum(group_count), 0) FROM ("
                        f"SELECT count(*) AS group_count FROM users "
                        f"WHERE ({email_expression}) IS NOT NULL "
                        f"GROUP BY ({email_expression}) HAVING count(*) > 1"
                        ") duplicates",
                    ),
                    "Projected values would violate ix_users_email uniqueness.",
                )
                collector.add(
                    "users.normalized_identity_collision",
                    _scalar(
                        connection,
                        "SELECT COALESCE(sum(group_count), 0) FROM ("
                        f"SELECT count(*) AS group_count FROM users "
                        f"WHERE ({email_expression}) IS NOT NULL "
                        f"GROUP BY lower(btrim(({email_expression}))) "
                        "HAVING count(*) > 1) duplicates",
                    ),
                    "Emails collide under the normalization used by authentication.",
                )

            has_oauth = inspector.has_table("oauth_accounts") and {
                "user_id",
                "provider",
                "provider_user_id",
            }.issubset(_columns(inspector, "oauth_accounts"))
            oauth_clause = (
                "AND NOT EXISTS (SELECT 1 FROM oauth_accounts oauth "
                "WHERE oauth.user_id = users.id)"
                if has_oauth
                else ""
            )
            if "password_hash" not in user_columns:
                credentialless = _scalar(
                    connection,
                    f"SELECT count(*) FROM users WHERE true {oauth_clause}",
                )
                malformed_hashes = 0
            else:
                credentialless = _scalar(
                    connection,
                    "SELECT count(*) FROM users WHERE "
                    "(password_hash IS NULL OR btrim(password_hash) = '') "
                    f"{oauth_clause}",
                )
                malformed_hashes = _scalar(
                    connection,
                    "SELECT count(*) FROM users WHERE password_hash IS NOT NULL "
                    "AND btrim(password_hash) <> '' "
                    "AND NOT (password_hash ~ :pattern)",
                    {"pattern": PASSWORD_HASH_PATTERN},
                )
            collector.add(
                "users.credentialless_accounts",
                credentialless,
                "Users would have neither a compatible local hash nor an OAuth identity.",
            )
            collector.add(
                "users.malformed_password_hash",
                malformed_hashes,
                "Stored local hashes do not match the PBKDF2 salt:hash format.",
            )

            if "status" in user_columns:
                status_meta = connection.execute(
                    sa.text(
                        "SELECT data_type FROM information_schema.columns "
                        "WHERE table_schema = current_schema() "
                        "AND table_name = 'users' AND column_name = 'status'"
                    )
                ).scalar_one()
                status_type_invalid = int(
                    status_meta not in ("character varying", "text")
                )
                collector.add(
                    "users.status_type_incompatible",
                    status_type_invalid,
                    "Migration calls lower(status), which requires a textual column.",
                )
                invalid_statuses = 0
                if not status_type_invalid:
                    invalid_statuses = _scalar(
                        connection,
                        sa.text(
                            "SELECT count(*) FROM users WHERE status IS NULL "
                            "OR lower(status) NOT IN :statuses"
                        ).bindparams(sa.bindparam("statuses", expanding=True)),
                        {"statuses": VALID_STATUSES},
                    )
                collector.add(
                    "users.invalid_status",
                    invalid_statuses,
                    "Status cannot be normalized to a supported account state.",
                )
            else:
                collector.add(
                    "users.status_type_incompatible",
                    0,
                    "Missing status is reported separately as an unsafe default.",
                )
                collector.add(
                    "users.invalid_status",
                    0,
                    "Missing status is reported separately as an unsafe default.",
                )

            if inspector.has_table("roles") and "role_id" in user_columns:
                collector.add(
                    "roles.orphaned_user_assignments",
                    _scalar(
                        connection,
                        "SELECT count(*) FROM users LEFT JOIN roles "
                        "ON roles.id = users.role_id "
                        "WHERE users.role_id IS NULL OR roles.id IS NULL",
                    ),
                    "Users have no valid role assignment.",
                )

        if inspector.has_table("roles"):
            role_columns = _missing_columns(
                collector, inspector, "roles", ("id", "name")
            )
            if "name" in role_columns:
                collector.add(
                    "roles.invalid_names",
                    _scalar(
                        connection,
                        "SELECT count(*) FROM roles WHERE name IS NULL "
                        "OR btrim(name) = ''",
                    ),
                    "Role names must be non-empty.",
                )
                collector.add(
                    "roles.normalized_name_collisions",
                    _scalar(
                        connection,
                        "SELECT COALESCE(sum(group_count), 0) FROM ("
                        "SELECT count(*) AS group_count FROM roles "
                        "GROUP BY lower(btrim(name)) HAVING count(*) > 1"
                        ") duplicates",
                    ),
                    "Role names collide after case/whitespace normalization.",
                )

        for legacy_table in ("accounts", "hashing_algorithms"):
            collector.add(
                f"legacy.{legacy_table}.rows_would_be_dropped",
                _scalar(connection, f'SELECT count(*) FROM "{legacy_table}"')
                if inspector.has_table(legacy_table)
                else 0,
                f"Migration drops {legacy_table}; non-empty data has no mapping.",
            )

        _check_existing_auth_table(
            collector,
            connection,
            inspector,
            "permissions",
            ("id", "name", "description", "resource", "action", "created_at"),
            ("name",),
            (("name",),),
        )
        _check_existing_auth_table(
            collector,
            connection,
            inspector,
            "user_sessions",
            (
                "id",
                "user_id",
                "session_token",
                "refresh_token",
                "ip_address",
                "user_agent",
                "is_active",
                "expires_at",
                "created_at",
                "last_accessed",
            ),
            ("session_token", "refresh_token"),
        )
        _check_existing_auth_table(
            collector,
            connection,
            inspector,
            "password_reset_tokens",
            ("id", "user_id", "token", "expires_at", "used", "created_at", "used_at"),
            ("token",),
        )
        _check_existing_auth_table(
            collector,
            connection,
            inspector,
            "email_verification_tokens",
            ("id", "user_id", "token", "expires_at", "used", "created_at", "used_at"),
            ("token",),
        )
        _check_existing_auth_table(
            collector,
            connection,
            inspector,
            "oauth_accounts",
            (
                "id",
                "user_id",
                "provider",
                "provider_user_id",
                "provider_email",
                "access_token",
                "refresh_token",
                "token_expires_at",
                "created_at",
                "updated_at",
            ),
            required_unique_keys=(("provider", "provider_user_id"),),
        )
        if inspector.has_table("oauth_accounts"):
            oauth_columns = _columns(inspector, "oauth_accounts")
            if {"provider", "provider_user_id"}.issubset(oauth_columns):
                collector.add(
                    "existing_auth.oauth_accounts.duplicate_provider_identity",
                    _scalar(
                        connection,
                        "SELECT COALESCE(sum(group_count), 0) FROM ("
                        "SELECT count(*) AS group_count FROM oauth_accounts "
                        "GROUP BY provider, provider_user_id HAVING count(*) > 1"
                        ") duplicates",
                    ),
                    "OAuth provider identities violate the target unique constraint.",
                )

        if not transaction_read_only:
            collector.add(
                "execution.transaction_not_read_only",
                1,
                "PostgreSQL did not confirm a read-only transaction.",
            )

    findings = tuple(collector.findings)
    return PreflightReport(
        migration_revision=MIGRATION_REVISION,
        parent_revision=PARENT_REVISION,
        passed=not any(finding.blocking for finding in findings),
        transaction_read_only=transaction_read_only,
        findings=findings,
    )


def _database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value.replace("postgres://", "postgresql://", 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only preflight for auth migration f3a5c1d8e9b0"
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        engine = sa.create_engine(_database_url(), pool_pre_ping=True)
        try:
            report = run_preflight(engine)
        finally:
            engine.dispose()
    except Exception as exc:
        # Error class is operationally useful; exception details can contain
        # SQL/connection data and therefore are deliberately not printed.
        print(
            json.dumps(
                {
                    "migration_revision": MIGRATION_REVISION,
                    "passed": False,
                    "error": type(exc).__name__,
                },
                sort_keys=True,
            )
        )
        return 2

    print(
        json.dumps(
            report.to_dict(),
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
