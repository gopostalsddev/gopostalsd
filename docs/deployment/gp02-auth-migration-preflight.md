# GP-02 auth migration safety gate

Migration `f3a5c1d8e9b0` is irreversible. Its downgrade is empty, and its upgrade
drops legacy identity columns plus the `accounts` and `hashing_algorithms`
tables. It must never be run on a database merely because Alembic reports that
the parent revision is current.

## What the migration actually does

- Extends `roles` with permissions, system-role, and timestamp metadata.
- Projects the final user email from `email` or `lower(email_address)`, makes it
  non-null and unique, then drops `email_address` and `creation_date`.
- Normalizes textual user status values to lowercase and adds current
  authentication fields when absent.
- Makes shipping and billing address relationships nullable.
- Creates permission, session, password-reset, OAuth, and email-verification
  tables when absent, plus unique token/provider identities.
- Drops `accounts` and `hashing_algorithms` without mapping their rows.

The migration is intentionally unchanged. GP-02 adds a deterministic safety
gate around it instead of rewriting migration history.

Two legacy-state defaults are not safe to infer. If `created_at` is absent, the
migration's initial column snapshot prevents the later `creation_date` copy and
the original timestamp is lost. Likewise, absent status and verification fields
would assign defaults to every existing user without evidence of their actual
account state. The preflight blocks those cases; they require a separately
reviewed reconciliation before rehearsal.

## Required preflight

Run from `backend/` with a PostgreSQL URL belonging to a SELECT-only role:

```bash
DATABASE_URL='postgresql://readonly:.../gopostal' \
python auth_migration_preflight.py --pretty
```

Exit `0` means all known preconditions passed. Exit `1` means one or more
blocking categories has a non-zero count. Exit `2` means the preflight could
not complete. The command reports category names and aggregate counts only; it
never prints emails, hashes, tokens, row identifiers, SQL errors, or connection
details.

The preflight itself begins with `SET TRANSACTION READ ONLY` and verifies the
server accepted that mode. Its checks cover:

- required tables and columns;
- missing, blank, malformed, oversized, duplicate, or normalization-colliding
  email identities;
- credentialless accounts and incompatible password hashes;
- incompatible or unsupported account status values;
- invalid user-role relationships and normalized role-name collisions;
- data in legacy tables the migration would discard;
- partial pre-existing auth tables, orphan rows, and duplicate tokens or OAuth
  provider identities.

## PostgreSQL fixture contract

| Input state | Expected preflight | Migration action | Expected state |
|---|---|---|---|
| Reconciled legacy user with canonical unique email, preserved creation time, explicit active/verified state, compatible PBKDF2 hash, and valid role | PASS | Rehearse | User, role, hash, normalized status and email survive; legacy structures are removed; auth tables and constraints exist |
| Missing email source; blank, malformed, oversized, noncanonical, duplicate, or normalization-colliding projected email | FAIL with its independent category | Do not run | Unchanged fixture |
| Missing creation-time, status, or verification source | FAIL with its independent category | Do not run | Unchanged fixture |
| Credentialless account without OAuth, malformed local hash, unsupported status, or non-text status | FAIL with its independent category | Do not run | Unchanged fixture |
| Orphaned user-role assignment, invalid role name, or normalized role collision | FAIL with its independent category | Do not run | Unchanged fixture |
| Any row in a legacy table the migration drops | FAIL naming that table and row count | Do not run | Unchanged fixture |
| Partial pre-existing auth table, orphaned auth row, or duplicate token/provider identity | FAIL with table-specific category | Do not run | Unchanged fixture |
| Account without local password but with a structurally valid, unique OAuth identity | PASS | Rehearse as applicable | OAuth identity remains the authentication source |

Unsafe fixtures intentionally stop before migration. A failure is evidence that
the guard prevented an unsafe operation, not an invitation for the test harness
to demonstrate the destructive outcome.

## Restored-production rehearsal required

Before any future production upgrade crosses `f3a5c1d8e9b0`:

1. Restore a current production backup into a disposable PostgreSQL instance
   with no route to production services.
2. Create a dedicated role with only `CONNECT`, schema `USAGE`, and table
   `SELECT`; do not grant write or DDL privileges.
3. Record the restored database revision, schema fingerprint, row counts, and a
   backup checksum without exporting identity or secret values.
4. Run the GP-02 preflight twice through the SELECT-only role. Both reports must
   be identical and pass; the before/after database snapshots must match.
5. Resolve every non-zero category through an explicitly reviewed data repair.
   Re-run from a fresh restore after any repair plan is approved.
6. Take a restorable checkpoint of the disposable database, then upgrade only
   to `f3a5c1d8e9b0`.
7. Verify migrated row counts, projected normalized email uniqueness, preserved
   password hashes and roles, the five auth tables, removed legacy structures,
   and the exact Alembic revision.
8. Exercise a known local account through ORM loading, password verification,
   active/verified login eligibility, session creation and logout. Exercise an
   OAuth-only account if production contains one. Use test delivery providers.
9. Upgrade the disposable database to the current single head, run explicit
   bootstrap, boot the application twice, and confirm neither boot mutates data.
10. Rehearse restoration from the checkpoint and record duration and operator
    commands. A successful forward run without a successful restore rehearsal
    is not sufficient.

Production remains **DO NOT RUN — REHEARSAL REQUIRED** until that evidence is
reviewed and the normal deployment gates separately pass.
