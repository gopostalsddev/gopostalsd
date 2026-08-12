# GP-18: GoPostal-only backup and restore controls

This package prepares repository-owned controls only. It does not install a
timer, access the VPS, or select an off-host provider.

`backup-database.sh scheduled` creates a PostgreSQL custom-format archive under
root-only `/var/backups/gopostal`. It refuses to publish a partial dump, rejects
implausibly small output, requires `pg_restore --list`, writes SHA-256 and JSON
metadata, and applies bounded tier retention (7 nightly, 5 weekly, 12 monthly,
5 pre-deploy). The daily UTC schedule promotes Sunday backups to weekly and the
first day of the month to monthly.

The local backup is not considered complete unless the root-owned
`/usr/local/sbin/gopostal-backup-offsite` hook successfully copies the archive,
checksum, and metadata to an encrypted independent destination. Until the owner
selects and authorizes that destination, the script retains the verified local
copy but exits `2`, making the missing off-host copy alertable and blocking
certification.

`restore-drill.sh <backup-basename.dump>` accepts no arbitrary path. It verifies
the checksum, restores into a uniquely named disposable database with
`--exit-on-error --single-transaction`, checks the single Alembic version row
and non-empty public schema, records duration/evidence, and drops the drill DB
on every exit.

Before MIGRATION READY, an authorized operator must:

1. install the scripts root-owned under `/usr/local/sbin`;
2. select, implement, and test the encrypted off-host hook;
3. obtain owner approval for retention, RPO, and RTO;
4. enable the systemd timer and prove stale/failure alerting;
5. run two successful disposable restores and a quarterly application-level
   smoke test from a restored archive;
6. separately decide whether Supabase objects need an independent backup or an
   object key/size/hash manifest.

No Rezza path, credential, container, or backup resource is referenced.
