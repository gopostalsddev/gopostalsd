# GP-08 durable refund attempts

Refunds now use one canonical service. It locks the order and payment, checks
the sum of committed refunds, reserves a durable attempt and stable Square key,
and commits that reservation before the provider call.

- Partial and full refunds update local status according to the cumulative
  committed amount; a partial refund no longer marks the whole order refunded.
- Concurrent or changed requests cannot pass an active unknown/processing
  reservation, and cumulative refunds cannot exceed the captured payment.
- A definitive provider rejection releases the reservation for a new request.
- An unknown outcome remains reserved and retries only with the same amount,
  reason, payment and idempotency key.
- Provider success is not returned to the caller until the unique local refund,
  attempt, payment and order states commit together.
- A refund webhook can reconcile an unknown attempt by the single active
  payment/amount/currency identity; duplicate provider refund IDs are unique.

Migration `gp08_refund_attempts` follows `gp07_payment_attempts`, creates the
attempt table, and adds external-refund uniqueness. Under the selected GP-03B
fresh-install path these structures are applied before any customer data or
provider IDs exist.

Square Sandbox remains required for the final full/partial, concurrent,
timeout, webhook, duplicate, and cumulative-boundary acceptance matrix.
