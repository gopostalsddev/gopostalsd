# GP-07 durable payment attempts

## Financial boundary

The order lifecycle now reserves a `payment_attempts` row and commits it before
calling Square. Each attempt carries a server-generated, stable Square
idempotency key, a non-secret provider reference, the authoritative order
amount/currency, and a SHA-256 fingerprint of the ephemeral source token. The
source token itself is never stored.

- Concurrent requests serialize on the order. An in-flight attempt causes the
  second request to stop before contacting Square.
- A provider timeout or exception becomes `unknown`; a byte-equivalent retry
  reuses the same Square key. A different source is rejected until the unknown
  attempt is reconciled.
- A definitive decline becomes `failed`, returns the order to `pending`, and
  permits a new attempt with a new key.
- Success creates at most one provider-scoped `payments` row and marks the
  attempt and order complete in one transaction.
- A Square webhook arriving before the HTTP response can resolve the attempt by
  its safe provider reference. Amount and currency must match before it can
  create local payment state.
- A completed local payment is replayed without another provider call.

The migration adds unique identities for attempt keys, provider references,
attempt payment IDs, and `(payment_provider, external_payment_id)`.

## Fresh-launch impact

`gp07_payment_attempts` follows `gp06_square_webhook_inbox` and is forward-only.
The owner selected GP-03B, so the new table and payment uniqueness constraint
are applied to an empty launch database. No historical deduplication is needed.
The empty-to-head PostgreSQL job remains authoritative for DDL compatibility.

Final acceptance still requires Square Sandbox proof for double-click,
concurrent submission, timeout-after-provider-success, webhook-before-response,
and retry with one provider charge.
