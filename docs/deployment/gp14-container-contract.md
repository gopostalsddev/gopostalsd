# GP-14 — Minimal production container contract

Repository-owned production assets now define two running services only:
`gopostal_web` and `gopostal_db`.

The web image is a multi-stage Python 3.12 build, runs as fixed UID/GID 10001,
uses one Gunicorn worker with four threads, logs to stdout/stderr, exposes only a
loopback host port, and is compatible with a read-only root filesystem. Compose
drops all capabilities, enables `no-new-privileges`, provides only a bounded
`/tmp` tmpfs, applies CPU/memory/PID limits, and gates health on GP-12 readiness.

PostgreSQL 17.6 is private to the internal `gopostal_data` network, has no host
port, and uses the dedicated `gopostal_production_postgres` volume. The web and
database services consume separate root-owned environment files so application
provider secrets are not exposed to PostgreSQL. No Rezza resource or upload
volume is shared.

## Rehearsal sequence (not authorized yet)

1. Set `GOPOSTAL_IMAGE_TAG` to the immutable release SHA.
2. Start `db` and wait for `pg_isready` health.
3. Take/verify the required checkpoint.
4. Run `docker compose run --rm web ./migrate.sh` from the exact built image.
5. Assert Alembic current equals the single source head.
6. Start `web`, wait for `/health/ready`, then run acceptance checks.

GP-14 does not create host secrets, deploy to the VPS, or start any live
container. CI uses non-secret placeholders to validate Compose and build the
image. Image digest pinning follows the successful rehearsal build.
