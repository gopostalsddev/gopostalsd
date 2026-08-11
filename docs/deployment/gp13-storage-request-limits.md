# GP-13 — Storage and request-size boundary

Production now requires an explicit `FILE_STORAGE_BACKEND=supabase` contract
with `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, and `SUPABASE_BUCKET`. It cannot
fall back to the ephemeral local filesystem. Live credentials and bucket
inspection remain owner-controlled acceptance prerequisites; GP-13 uses mocks
only and does not contact Supabase.

Flask rejects requests above 6 MiB globally and JSON bodies above 1 MiB before
route services read them. The existing image-storage boundary remains 5 MiB,
leaving multipart overhead. JPEG, PNG, and WebP are allowed only when extension,
declared MIME, and magic bytes agree; the inconsistent GIF route allowance has
been removed. Provider errors are logged without provider response details.

The storefront currently previews customer PDF artwork only in browser memory;
it does not transfer file bytes or persist an object reference. The UI now says
this explicitly and instructs the customer to arrange secure transfer before
production. A durable customer-artwork workflow is a separate product package,
not fabricated by the VPS migration.

The VPS/Caddy request-size ceiling will be pinned to the same values in GP-15.
