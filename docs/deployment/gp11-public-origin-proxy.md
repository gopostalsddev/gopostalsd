# GP-11 — Canonical public origin and proxy boundary

The launch hostname is still an explicit unresolved owner variable. GP-11 does
not choose or hardcode it.

Production runtime requires:

- `PUBLIC_BASE_URL=https://<client-confirmed-origin>` with no path;
- `TRUSTED_PROXY_HOPS=1` for the single ingress reverse proxy;
- the API bound so clients cannot bypass that ingress.

Credentialed CORS and unauthenticated CSRF checks use only the exact
`PUBLIC_BASE_URL` origin. Historical Render URLs, backend-provider URLs, and
generic `FRONTEND_URL` values are not silently added to the production
allowlist. Referer paths are accepted only after reducing them to their exact
origin; lookalike suffixes are rejected.

Development trusts no forwarded headers by default. Production trusts exactly
the nearest proxy-supplied address; configuring zero, two, or a non-integer hop
count aborts startup. Migration mode serves no traffic, trusts no proxy, and
does not require the unresolved launch origin.

The frontend defaults to same-origin `/api`. The former Render-hostname
inference has been removed. A split-origin rehearsal may still provide an
explicit build-time `VITE_API_BASE_URL`.

VPS deployment and binding/firewall evidence remain separate execution-time
requirements; this package does not access or mutate the VPS or DNS.
