# GP-03 database path decision

## Current fact pattern

As of 2026-08-11, the historical Render PostgreSQL service is absent from the
owner's Render service list. The deployed API retains an obsolete
`DATABASE_URL`, and a real login attempt fails because its PostgreSQL hostname
cannot resolve. This is evidence that the dependency is unavailable; it is not
evidence that the database can or cannot be recovered.

No recovery attempt, Render access, production connection, or historical-data
fabrication is authorized by this decision.

## Owner decision

On 2026-08-11, the owner confirmed that the project has never served real
clients and is intended to launch only after successful VPS certification.
GP-03B is therefore the selected path. GP-03A is not applicable unless the
owner later identifies an unexpected historical backup that they explicitly
want restored.

## GP-03A: conditional historical-data recovery

GP-03A applies only if the owner locates an owner-controlled PostgreSQL custom
dump, provider export, or other verifiable backup. That artifact must be kept
out of Git and restored into an isolated same-major PostgreSQL instance. The
procedure in the migration execution plan then remains mandatory: checksum and
list the dump, restore twice with exit-on-error, compare redacted manifests,
run the GP-02 SELECT-only auth preflight, prove the stored revision is a known
ancestor of the sole head, rehearse the upgrade, test authentication and
business integrity, and prove restore time.

Do not stamp, repair, or migrate an unknown historical schema in place.

## GP-03B: fresh-install path

GP-03B applies because the owner explicitly confirmed that GoPostal will launch
as a fresh installation and that there is no real-client historical dataset.

GP-01 already supplies authoritative technical evidence for an empty database:

- empty PostgreSQL traverses the complete migration graph;
- exactly one Alembic head, `gp01_pricing_policy`, is reached;
- explicit bootstrap succeeds and is idempotent;
- two production-mode boots cause no schema or row mutations.

GP-02's synthetic legacy fixtures remain sufficient evidence for the behavior
of irreversible migration `f3a5c1d8e9b0` when there is no real legacy database
to migrate. They prove its preconditions, unsafe-state detection, data
transformation, ORM compatibility, and authentication behavior. They do not
prove or claim recovery of absent historical data.

### Evidence still required for a fresh launch

1. A newly provisioned, private PostgreSQL database with a supported major,
   dedicated least-privilege application and migration roles, TLS, backups, and
   no reused Rezza credentials.
2. One-shot migration from empty to the sole repository head, followed by
   explicit bootstrap; migration and application startup remain separate.
3. A redacted post-bootstrap manifest, sequence/FK/unique checks, and a verified
   backup plus disposable restore drill for the new database.
4. The fresh-install acceptance suite below, using sandbox/test providers before
   any production credential is enabled.

### Historical requirements that become not applicable

- Render source-database dump, checksum, and source/restore equality;
- ancestry validation of a historical production revision;
- historical table counts, financial aggregates, identifier hashes, sequences,
  legacy FK orphans, and legacy auth preflight results;
- preservation or reconciliation of historical customers, orders, payments,
  sessions, OAuth links, and provider identifiers;
- historical-data migration RTO.

Backup/restore, integrity, and RTO controls for the **new** database remain
applicable.

### Fresh-install acceptance suite

- health and database readiness;
- one migration head and exact current revision;
- idempotent bootstrap and repeated mutation-free production boots;
- initial administrator creation through the approved explicit bootstrap path,
  followed by removal of bootstrap credentials;
- customer registration, verification, login, refresh/session invalidation,
  password reset, authorization, lockout, and logout;
- catalog sync using non-production fixtures, pricing, cart, shipping, and file
  upload/storage boundaries;
- sandbox checkout, persisted order/payment state, signed webhook, duplicate
  delivery, failed-processing retry, refund, and reconciliation;
- transactional email delivery to controlled test recipients;
- empty-state and newly-created-record behavior in customer/admin interfaces;
- backup creation, checksum/list, isolated restore, restored application boot,
  and measured RTO;
- logs, alerts, resource limits, TLS, CORS/CSRF, and no production secrets in
  the sandbox evidence environment.

## Release effect

The absence of historical data is not a migration blocker because the owner has
confirmed that no real-client dataset exists and selected a fresh launch. The
release may become migration-ready after all fresh-install gates pass. No records
may be recreated from guesses, screenshots, application defaults, or synthetic
fixtures.
