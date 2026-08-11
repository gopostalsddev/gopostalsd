# GP-16: focused authentication and runtime security

## Account-state oracle

Login now performs PBKDF2 verification before disclosing whether a known account
is locked, unverified, suspended, or deactivated. Unknown users and OAuth-only
users are checked against a valid dummy hash so the negative path still performs
password work. A wrong password returns the same `INVALID_CREDENTIALS` envelope
for every account state. State-specific guidance is returned only after the
caller proves knowledge of the local password.

The lock check also normalizes comparisons to the timezone convention returned
by the historical database column. This prevents a locked account loaded as a
naive UTC timestamp from turning a denial into a 500 response.

## Production runtime

- `DEBUG` and `FLASK_DEBUG` must be disabled.
- Swagger UI and the machine-readable Swagger specification are not registered
  in production.
- The pinned runtime starts one Gunicorn worker with four threads. This makes the
  current in-memory rate limiter process-consistent for initial launch. Moving
  to multiple workers requires a shared Redis-backed limiter first.
- The production Compose contract overrides debug/documentation flags to their
  safe values even if a stale env file contains different values.

## One-time administrator bootstrap

Normal production boot refuses any remaining `ADMIN_*` bootstrap value. The
one-time command requires both an explicit mode flag and the exact CLI command:

```sh
RUN_ADMIN_BOOTSTRAP=true \
ADMIN_EMAIL='owner-confirmed-address' \
ADMIN_PASSWORD='one-time-secret' \
flask bootstrap-admin
```

The values must be supplied through an owner-controlled secret channel and
removed immediately after the command. A subsequent ordinary production boot
is the proof that no bootstrap credential remains.

## Explicitly deferred

Password-reset, verification, and session-token hashing at rest requires a
separately rehearsed schema/data migration. It remains a documented post-launch
hardening package and is not disguised as part of this focused runtime cut.
