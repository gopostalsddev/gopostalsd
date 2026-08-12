# GP-09 single payment path

`POST /api/payments/process` is retired and returns 410 before parsing input,
loading an order, or constructing a payment provider. It cannot charge.

The only public charging endpoint is now
`POST /api/orders/<order_id>/payment`. It enforces authentication and order
ownership before delegating to the GP-07 durable attempt lifecycle. The
frontend already uses this canonical endpoint and has no reference to the
retired bypass.

The retired URL remains as an explicit 410 during migration so stale clients
fail safely and visibly rather than receiving a generic 404. It can be removed
after the client compatibility window.
