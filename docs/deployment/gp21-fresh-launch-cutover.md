# GP-21: fresh-launch cutover runbook

This runbook is prepared only. It authorizes no VPS, DNS, Render, MailerSend, or
Square mutation. The client-confirmed `CANONICAL_URL=https://uzimaprints.com`
and `CANONICAL_HOST=uzimaprints.com` remain explicit runbook inputs. `RELEASE_SHA` and
`IMAGE_DIGEST` are launch variables, not values to infer from the approved
sender address.

GoPostal has never served live clients and the retired Render database held
pre-launch/development state. GP-03B therefore launches a fresh PostgreSQL
database. There is no historical database transfer and no customer-data write
freeze. The operational freeze below is a release/configuration freeze so the
candidate tested by GP-17 remains identical to the candidate launched.

## Non-negotiable entry gate

The operator must have a GP-17 report with `verdict=MIGRATION_READY` and a
`release_sha` exactly equal to `RELEASE_SHA`. Every evidence record must still
be within its allowed age at T0. A green CI run is not a substitute. If any
record is pending, invalid, stale, or bound to another SHA, stop.

The owner-controlled launch variables must also be closed: canonical URL;
approved DNS change; MailerSend domain verification for
`support@uzimaprints.com`; safely installed production provider credentials;
encrypted off-host backup destination; alert recipient; and approved retention,
RPO, RTO, and rollback decision authority.

## T-7 days

1. Record `RELEASE_SHA`, `IMAGE_DIGEST`, sole Alembic head, dependency manifests,
   and the frontend artifact hash.
2. Confirm `CANONICAL_URL` and `CANONICAL_HOST`; inspect all generated Caddy,
   CORS, CSRF, Square webhook, MailerSend, and monitoring values for that host.
3. Confirm DNS ownership and approve a TTL reduction. Do not mutate DNS merely
   because this runbook exists.
4. Verify MailerSend DNS/domain status and intended sender identity without
   recording credentials in evidence.
5. Confirm Square production application/location/webhook ownership and the
   authorized person who will change it at T0. Sandbox acceptance must already
   be complete.
6. Confirm the off-host backup provider and owner-approved retention, RPO, and
   RTO. Run the GP-18 restore drill twice.
7. Complete GP-17 against a fresh VPS rehearsal using the exact release SHA.

## T-24 hours

1. Provision private PostgreSQL with dedicated migration and application roles,
   TLS, bounded host access, and no credentials reused from Rezza or Render.
2. Install root-owned environment files, Caddy configuration, monitoring
   fragments, backup controls, and immutable release artifacts. Verify modes and
   ownership without printing values.
3. Build/pull the image by `IMAGE_DIGEST`; migrate the empty database to the sole
   head as a one-shot operation; then run explicit idempotent bootstrap.
4. Create the initial administrator through the one-time bootstrap path, remove
   bootstrap credentials, recreate the app container, and prove their absence.
5. Produce a redacted schema/integrity manifest and a verified pre-launch backup;
   restore it into a disposable database and boot the same image against it.
6. Exercise temporary-host tests behind Basic Auth. Do not enable HSTS or expose
   the launch UI before canonical TLS and acceptance succeed.

## T-1 hour

1. Begin the release/configuration freeze. No source, image, migration, frontend,
   provider, or environment change is allowed without restarting GP-17.
2. Reconfirm image digest, source SHA, migration head/current revision, frontend
   hash, container health/isolation, database integrity, and backup freshness.
3. Verify production credentials are classified for GoPostal and production,
   remain absent from logs/evidence, and differ from Rezza and test credentials.
4. Capture the current DNS and provider settings needed for audit and rollback,
   excluding secret values.

## T-30 minutes — final GO/NO-GO

1. Re-run the GP-17 verifier for `RELEASE_SHA`.
2. Confirm database `/health/ready`, external temporary-host checks, logs,
   dashboards, alert delivery, restore evidence, and named rollback commander.
3. Confirm the canonical DNS change and Square webhook update are prepared but
   not yet applied.
4. Any discrepancy is NO-GO. Do not waive or manually edit the GP-17 verdict.

## T0

1. Publish the immutable frontend and start the exact web image against the
   already-migrated fresh database. Application startup must not run Alembic.
2. Apply the approved DNS change for `CANONICAL_HOST`.
3. Wait for authoritative/public resolution and valid canonical TLS. Verify
   certificate name/chain, SPA deep links, `/health/live`, and `/health/ready`.
4. Apply the canonical production Caddy configuration. Enable the approved HSTS
   value only after canonical HTTPS is proven.
5. Update the Square production webhook to
   `CANONICAL_URL/api/payments/webhook`; verify signature handling with the
   provider-supported test delivery. Do not replay captured production bodies.
6. Enable MailerSend production delivery only after verified-domain status is
   current. Send to controlled recipients and verify the approved From identity.
7. Remove temporary Basic Auth only after all T0 checks pass.

## T+15 minutes

1. Run controlled registration, verification, login/logout, password reset,
   catalog, pricing, cart, shipping, upload/retrieval, and admin authorization
   smoke tests.
2. Confirm Square webhook receipt persistence, duplicate handling, and logs. A
   real monetary charge/refund requires separate owner authorization; never
   create one merely to satisfy this runbook.
3. Confirm no debug/Swagger exposure, no cross-origin surprise, no secret/PII
   logging, and no unexpected 4xx/5xx spike.

## T+30 minutes

1. Confirm public/readiness/TLS, DB, container, capacity, backup, 5xx, and latency
   monitoring targets are present and alert routing is healthy.
2. Confirm Caddy and application logs reach the existing Loki pipeline with
   GoPostal labels and redaction.
3. Record DNS propagation and provider dashboard state without credential data.

## T+2 hours

1. Review resource use, errors, queue/retry states, webhook inbox, payment and
   refund attempts, email delivery, object storage, and database connections.
2. Take and verify the first scheduled/off-host-capable backup if due; do not
   advance the success metric for a local-only copy.
3. The rollback commander either closes the launch watch or invokes GP-22.

## T+24 hours

1. Review all alerts, access/error logs, authentication events, payments,
   refunds, provider delivery, backups, and capacity.
2. Confirm the backup timer produced a verified local and off-host copy and that
   the restore drill schedule is recorded.
3. Restore normal DNS TTL only with owner approval. Archive the redacted GP-17
   report, hashes, timestamps, decisions, and incident notes.

## Hard stop conditions

- GP-17 is not `MIGRATION_READY` for the exact release.
- canonical hostname, DNS authority, provider ownership, off-host backup, alert
  recipient, RPO/RTO, or rollback authority is unresolved;
- migration current/head mismatch, bootstrap secret present, readiness failure,
  invalid TLS, broken auth/admin boundary, webhook authenticity failure, or
  secret exposure;
- rollback commander cannot determine whether a real write has occurred.

Use GP-22 for every rollback decision. Because the historical Render database is
unavailable, pointing DNS back to Render is not a valid application rollback.
