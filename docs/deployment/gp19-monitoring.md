# GP-19: existing-stack monitoring integration

This package supplies merge fragments for the existing VPS monitoring stack; it
does not deploy a second stack or mutate the host. The scrape template retains
`__GOPOSTAL_HOST__`, `__GOPOSTAL_BLACKBOX_EXPORTER_TARGET__`,
`__GOPOSTAL_CADDY_METRICS_TARGET__`, and
`__GOPOSTAL_POSTGRES_EXPORTER_TARGET__` until an authorized operator
substitutes targets verified reachable from the existing Prometheus execution
context. Container loopback must not be assumed to reach host services.

Caddy exposes per-host Prometheus metrics only on its loopback admin endpoint.
Blackbox probes cover the public root, database-aware readiness, and TLS expiry.
Alert rules cover availability, DB visibility, missing containers, memory, host
disk, stale verified off-host backups, HTTP 5xx, and p95 latency.

The backup textfile metric advances only after the archive and encrypted
off-host hook both succeed. A local-only backup therefore remains stale/absent
and alerts rather than being misreported as complete.

Before MIGRATION READY, an authorized VPS operator must merge and validate these
fragments in the existing Prometheus/Blackbox/node-exporter/cAdvisor/Caddy
configuration, route alerts to the approved recipient, and produce evidence for
each safe synthetic failure:

- failed readiness and public probe;
- absent/stale backup metric;
- DB exporter unavailable;
- missing/stopped test container and controlled memory pressure;
- synthetic 5xx/latency;
- certificate-expiry rule evaluation.

GoPostal stdout and Caddy JSON access logs must be added to the existing Loki
pipeline with `application=gopostal` labels. Authorization, cookies, query
tokens, raw Square webhook/payment bodies, and client PII must remain excluded.
The exact Alloy merge is intentionally left host-specific until the authorized
existing configuration can be inspected.
