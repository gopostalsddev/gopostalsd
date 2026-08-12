# GP-22: fresh-launch rollback and recovery

This runbook is prepared only and authorizes no host, DNS, provider, or database
mutation. It applies to the GP-03B fresh launch at unresolved `CANONICAL_URL`
and exact `RELEASE_SHA`.

The historical Render database is unavailable and is not a rollback target.
Returning DNS to a deployed Render service whose database dependency cannot
resolve does not restore GoPostal. Rollback means aborting before exposure,
serving a controlled maintenance response, reverting only compatible immutable
application/frontend/config artifacts, or rolling forward while preserving the
new VPS database and provider events.

## Decision authority and evidence

Before T0, name one rollback commander and one database custodian. Record the
release SHA, image digest, migration head/current revision, frontend hash,
canonical DNS before/after values, provider endpoint identifiers, backup names
and hashes, and the time of the first real write. Never record credentials,
webhook bodies, tokens, cookies, client files, or unnecessary PII.

The rollback commander must know which phase applies. When uncertain, assume a
real write has occurred and use Phase C.

## Phase A — before canonical DNS changes

Abort the launch. Do not change DNS or production provider endpoints. Leave the
temporary host protected. Preserve logs and GP-17 evidence, fix the candidate,
and repeat every affected acceptance gate. A failed empty-database migration may
be discarded and reprovisioned because no real user data exists; do not repair
or stamp a partially migrated schema and do not use `flask db downgrade`.

## Phase B — DNS changed, proven zero real writes

Stop public intake or serve a static maintenance response at the VPS edge.
Confirm zero registrations, password/reset state, uploads, carts, orders,
payment/refund attempts, webhook inbox rows, emails, or administrator mutations.
Take a verified diagnostic backup even when counts are zero.

Revert DNS only to an owner-approved functioning maintenance/static target. Do
not point it to the database-broken Render API. If the defect is limited to
Caddy or the frontend, restore the prior validated Caddy file or immutable
frontend release and re-run TLS/deep-link/security checks. If the backend image
is defective, start a prior schema-compatible image against the same database;
otherwise stay in maintenance and roll forward.

## Phase C — first real write has occurred

This is the latest safe rollback boundary for stateless artifacts, not for the
database. Immediately disable new checkout/registration/upload intake while
keeping health diagnostics and the Square webhook receiver available. Capture a
verified backup/checksum/metadata set before intervention and preserve logs,
webhook inbox rows, payment/refund attempts, object identifiers, and delivery
states.

Never restore the pre-launch database over new writes. Never run an Alembic
downgrade. Never point DNS at Render. A prior application image may be used only
when its declared schema compatibility includes the current database revision
and its Square webhook path preserves current inbox/idempotency behavior. If
compatibility is not proven, remain in maintenance and roll forward.

If a database restore is unavoidable after corruption, restore into an isolated
database first, reconcile every post-checkpoint write and provider event under
an approved incident plan, and cut over only after integrity and acceptance
checks. DNS changes alone cannot resolve database divergence.

## Failure-specific actions

### Migration failure

- Before any real write: stop; retain the pre-migration backup and failure logs;
  reprovision the fresh database or restore the verified checkpoint into an
  isolated target; fix forward; rehearse; retry from the entry gate.
- After a real write: migration should never be running as application startup.
  If an operator started one anyway, freeze intake, preserve the database, and
  perform incident-specific forward recovery. Do not downgrade or overwrite.

### Database restore failure

Do not launch. Keep DNS/provider settings unchanged. Diagnose archive checksum,
PostgreSQL version, roles/extensions, storage capacity, and `pg_restore` output
using a disposable target. A backup is not certified until two restores and an
application boot pass within approved RTO.

### Backend or readiness failure

Before writes, restore a schema-compatible image or stay in maintenance. After
writes, preserve the database and roll back only the immutable image when
compatibility is proven; otherwise roll forward. Re-run readiness, auth/admin,
provider, storage, and logging gates before reopening intake.

### Frontend or Caddy failure

Restore the prior immutable frontend symlink or validated Caddy configuration.
Do not modify database state. Revalidate canonical TLS, SPA deep links, request
limits, security headers, `/api`, webhook routing, and log redaction before
removing maintenance or Basic Auth.

### Square webhook or payment failure

Disable new payment initiation, but keep the canonical webhook endpoint
reachable so Square retries can be durably recorded. Do not redirect it to
Render and do not replay captured bodies. Verify the configured canonical URL,
signature key provenance, inbox/idempotency rows, provider event IDs, payment
attempts, refunds, and reconciliation. Roll back only to a schema-compatible
handler that honors the same inbox contract; otherwise roll forward.

### MailerSend failure

Stop new transactional sends if duplication or wrong-recipient risk exists.
Preserve delivery identifiers and retry state without message bodies or PII.
Authentication and orders must not be falsely marked delivered. Correct verified
domain/sender/configuration and resume through bounded idempotent retry.

### Object-storage failure

Disable new uploads. Preserve database object references and provider object
metadata; do not fabricate files or delete unmatched objects during an incident.
Reconcile authorized upload/retrieval state before reopening.

### Monitoring failure

Monitoring loss alone does not justify database rollback, but it blocks launch
and reopening intake. Restore scrape/alert/log delivery, then repeat the GP-19
synthetic alert exercises and current GP-17 verification.

## Reopen criteria

Reopen only when the rollback commander has: identified the active release and
database revision; reconciled all writes/provider events since the last verified
checkpoint; proven health/readiness, auth/admin, catalog/order, Square,
MailerSend, storage, backup/restore, edge, and monitoring behavior; and produced
a fresh GP-17 `MIGRATION_READY` report bound to the active release SHA.

At T+24, archive the redacted timeline, decisions, evidence hashes, backup and
restore proof, reconciliation result, and corrective actions. Treat any RPO/RTO
miss as an incident and update GP-18/GP-21 before another launch attempt.
