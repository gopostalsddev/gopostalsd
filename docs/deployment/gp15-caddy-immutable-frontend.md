# GP-15: immutable frontend and Caddy boundary

This package prepares the frontend and edge configuration without selecting a
launch hostname or modifying a host. The client-owned canonical hostname remains
an explicit prerequisite.

## Required launch variables

- `GOPOSTAL_HOST`: the confirmed canonical hostname. It has no default.
- `GOPOSTAL_RELEASE_ROOT`: optional static root override; defaults to
  `/srv/gopostal/current/frontend-dist`.
- `GOPOSTAL_HSTS`: keep the default `max-age=0` until HTTPS and the canonical
  hostname are validated. Set the approved production policy only afterward.

For a temporary protected hostname, use `Caddyfile.temporary` and provide a
non-secret username plus a Caddy bcrypt hash through
`GOPOSTAL_BASIC_AUTH_USER` and `GOPOSTAL_BASIC_AUTH_HASH`. The exact
`/api/payments/webhook` path bypasses Basic Auth so Square can deliver signed
webhooks. Every other path remains protected.

## Release build and publication

Build with the same-origin API and non-secret Square browser identifiers:

```sh
cd frontend
npm ci
VITE_API_BASE_URL=/api \
VITE_SQUARE_ENVIRONMENT=production \
VITE_SQUARE_APPLICATION_ID="$SQUARE_APPLICATION_ID" \
VITE_SQUARE_LOCATION_ID="$SQUARE_LOCATION_ID" \
npm run build
```

Publish the already-built output under the exact Git commit SHA:

```sh
deploy/gopostal/publish-frontend-release.sh "$RELEASE_SHA" frontend/dist
```

The publisher refuses mutable/reused release directories, copies into a staging
directory, then atomically switches `/srv/gopostal/current`. A rollback switches
that symlink to a previously retained release; it does not alter the release.

## Edge contract

- Caddy serves the Vite SPA and falls back to `index.html` for deep links.
- Hashed `/assets/*` are immutable for one year; HTML is never cached.
- `/api/*`, `/health/live`, and `/health/ready` proxy only to
  `127.0.0.1:8500`.
- The exact webhook and JSON API bodies are limited to 1 MiB; other API bodies
  are limited to 6 MiB. Flask independently enforces the same JSON/global
  limits.
- Forwarded headers are overwritten at Caddy, matching
  `TRUSTED_PROXY_HOPS=1`.
- Logs are JSON, bounded, and redact authentication headers and sensitive query
  keys.
- The CSP permits only the application's known external browser dependencies:
  Google Fonts and the sandbox/production Square Web Payments SDK endpoints.
- There is no local `/uploads` route. GP-13 requires Supabase-backed storage in
  production.

## Validation and remaining gates

The GP-15 CI workflow parses both Caddyfiles with pinned Caddy 2.10.2, builds the
frontend from `npm ci`, runs the API/Square configuration tests, and exercises
the immutable publisher in a temporary directory.

The repository-wide ESLint command currently reports pre-existing legacy debt
(375 errors and 12 warnings). GP-15 adds no frontend source and the production
Vite build succeeds. Clearing that lint baseline remains required before a
future policy can make whole-repository lint a release gate; it is not silently
reported as passing here.

Live TLS, HSTS enablement, deep-link/browser checks, webhook delivery, and Caddy
reload validation require the confirmed hostname and authorized VPS and remain
cutover acceptance work. No DNS or host mutation is performed by this package.
