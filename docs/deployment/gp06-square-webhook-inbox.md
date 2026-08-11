# GP-06 Square webhook inbox

## Contract

Every signature-verified Square event must contain a non-empty `event_id` and
`type`. The API persists the raw event as parsed JSON plus a SHA-256 digest of
the exact signed bytes before business processing begins. `event_id` is unique.

- A successfully processed event returns 200 and becomes `processed`.
- A byte-identical duplicate returns 200 without repeating business work.
- Reuse of an event ID with different bytes returns 409.
- A processing exception rolls back business changes, leaves a durable `failed`
  receipt, and returns 503 so Square retries it.
- A failed delivery is claimable again; an abandoned `processing` lease is
  claimable after five minutes.
- Attempts and sanitized exception class names are retained. Exception messages
  and webhook bodies are not logged.

The event handler no longer commits independently. Its business mutations and
the receipt's transition to `processed` commit together. The initial inbox row
is committed separately so a failed attempt cannot erase evidence of delivery.

## Fresh-launch acceptance

Before production Square credentials are enabled, run the signed webhook tests
against the fresh VPS database and Square sandbox. Prove successful delivery,
simultaneous duplicate delivery, a forced processing failure followed by retry,
refund reconciliation, and that no event is acknowledged as successful while
its receipt remains failed.

Migration `gp06_square_webhook_inbox` is forward-only and follows
`gp01_pricing_policy`. It creates one table and two small empty-table indexes;
on the selected GP-03B fresh-install path it carries no legacy data or lock-risk
rehearsal requirement beyond the normal empty-to-head migration proof.
