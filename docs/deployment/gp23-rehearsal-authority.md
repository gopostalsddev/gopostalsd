# GP-23: constrained GoPostal rehearsal authority

`ops-gopostal` is a dedicated operator identity for the private GoPostal VPS
rehearsal. It is intentionally separate from the REZZA operator identities.
It is not a member of the Docker group and receives no generic Docker, shell,
filesystem, service-manager, firewall, proxy, or SSH privilege.

The authority consists of twelve root-owned, zero-argument wrappers. Every
Docker operation fixes the project name, project directory, Compose file,
source path, repository, reviewed application SHA, container names, networks,
and volume. Before operating, wrappers reject dirty or unexpected source,
configuration drift, unsafe ownership/modes, and same-named Docker resources
that do not carry the `gopostal-rehearsal` Compose project label.

## Files and identities

- Source: `/srv/gopostal/rehearsal-app`
- Stack: `/srv/docker/stacks/gopostal-rehearsal`
- Backups: `/var/backups/gopostal-rehearsal`
- Restore evidence: `/var/lib/gopostal-rehearsal/evidence`
- Operator: `ops-gopostal`
- Application source: `6f7c9e8ea4b5d4fac4d5cc05c36f3d249d91acac`
- Local application endpoint: `127.0.0.1:8510`
- Local frontend endpoint: `127.0.0.1:8511`

The source and stack are root-owned. `ops-gopostal` can invoke only the exact
no-argument commands recorded in `sudoers.ops-gopostal`. Rehearsal provider
values are non-live placeholders. Provider-dependent GP-17 items remain
`PENDING OWNER CONFIG`; placeholders never constitute provider acceptance.

## Installation gate

Provisioning verifies `MANIFEST.sha256`, wrapper inventory, Bash syntax, and
sudoers syntax before installing anything. The runtime acceptance suite begins
by comparing every bundle wrapper hash with the installed root-owned copy. It
then verifies the exact grants, forbidden host/Docker/filesystem surfaces,
argument rejection, approved source synchronization, fixed project status,
localhost-only exposure, dedicated resources, and absence of privileged/host
networking.

The owner must run the provisioning and acceptance commands from the exact
reviewed authority-package commit. A nonzero acceptance result is a hard stop.
When the suite reports `TOTAL FAIL: 0`, Codex may resume the already-authorized
private rehearsal. No public hostname, DNS change, or provider-live operation
is part of this package.
