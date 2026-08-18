# GP-17: migration-readiness evidence gate

GP-17 combines the fresh-install acceptance requirements into a fail-closed
release-SHA-bound verdict. It does not run provider operations, deploy to the
VPS, mutate Render or DNS, or claim that CI is production evidence.

`requirements.json` is the canonical list. Each gate requires one JSON evidence
record named `<gate_id>.json`, captured against the exact 40-character release
SHA in the environment declared by that requirement. Records must say
`synthetic: false`, be current, and contain no secret-bearing fields. Missing
records are `PENDING`; malformed, stale, synthetic, wrong-release, or
wrong-environment records are `INVALID`. Either state yields `NOT_READY` and a
non-zero exit.

The verifier emits only status, timestamp, and evidence-file SHA-256. It does
not reproduce record summaries or provider output in the report. Evidence
files remain outside Git in an owner-controlled directory.

Example, after an authorized rehearsal has produced all records:

```bash
python3 deploy/gopostal/verify-acceptance-evidence.py \
  --requirements deploy/gopostal/acceptance/requirements.json \
  --evidence-dir /var/lib/gopostal-certification/evidence \
  --release-sha "$RELEASE_SHA" \
  --report /var/lib/gopostal-certification/gp17-report.json
```

## Current classification

GP-03B fresh installation is selected. Render source recovery, historical
production counts, historical revision ancestry, and historical customer/order
reconciliation are not applicable unless the owner later requests recovery of
an identified backup.

The following remain live evidence, not CI substitutes: canonical-host TLS and
browser checks; MailerSend verified-domain delivery from
`support@uzimaprints.com`; Square sandbox payment/refund/webhook reconciliation;
object-storage round trip; restored-database application boot and RTO; effective
VPS isolation; and routed monitoring-alert exercises. Until those records exist
for the candidate release, the correct verdict is `NOT_READY`.
