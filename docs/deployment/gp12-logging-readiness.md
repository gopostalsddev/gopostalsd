# GP-12 — Stdout logging and readiness

GoPostal now writes structured JSON logs to stdout only. Runtime logging no
longer creates `app.log`, so an immutable/read-only container filesystem is a
supported target. `LOG_LEVEL` is honored through a strict allowlist.

The formatter redacts bearer values, common credential/token assignments,
token-bearing query parameters, and direct email identifiers. Exception output
includes the exception type and stack-frame locations but deliberately excludes
the exception message, which may contain provider responses, connection URLs,
PII, or secrets.

Health is split by purpose:

- `GET /health/live` proves only that the process can serve HTTP.
- `GET /health/ready` runs a read-only `SELECT 1` and returns 503 when the
  database is unavailable. PostgreSQL applies a transaction-local statement
  timeout (`READINESS_DB_TIMEOUT_MS`, default 2000 ms).
- `GET /health` remains as a compatibility alias for shallow liveness.

Readiness intentionally excludes Square, MailerSend, Sinalite, and Supabase so
an external-provider outage does not trigger an application restart cascade.
Render's repository blueprint now targets `/health/ready`; the production
Docker healthcheck will consume the same endpoint in GP-14.
