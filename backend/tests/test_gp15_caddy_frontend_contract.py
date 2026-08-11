"""Static GP-15 Caddy and immutable frontend release contracts."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CADDY = (ROOT / "deploy/gopostal/Caddyfile").read_text(encoding="utf-8")
TEMPORARY = (ROOT / "deploy/gopostal/Caddyfile.temporary").read_text(encoding="utf-8")
PUBLISH = (ROOT / "deploy/gopostal/publish-frontend-release.sh").read_text(encoding="utf-8")


def test_hostname_and_release_root_are_runtime_variables():
    for config in (CADDY, TEMPORARY):
        assert "{$GOPOSTAL_HOST}" in config
        assert "gopostalsd.com" not in config
        assert "{$GOPOSTAL_RELEASE_ROOT:/srv/gopostal/current/frontend-dist}" in config


def test_api_health_and_exact_webhook_are_proxied_to_loopback():
    assert "@webhook path /api/payments/webhook" in CADDY
    assert "@backend path /api/* /health/live /health/ready" in CADDY
    assert CADDY.count("reverse_proxy 127.0.0.1:8500") == 3
    assert "/uploads" not in CADDY


def test_forwarded_headers_are_replaced_at_the_single_proxy_hop():
    for header in (
        "header_up Host {host}",
        "header_up X-Forwarded-Host {host}",
        "header_up X-Forwarded-Proto {scheme}",
        "header_up X-Forwarded-For {remote_host}",
    ):
        assert CADDY.count(header) == 3


def test_request_limits_match_backend_contract():
    assert CADDY.count("max_size 1MB") == 2
    assert CADDY.count("max_size 6MB") == 1
    assert "header Content-Type application/json*" in CADDY


def test_spa_caching_and_security_headers_are_explicit():
    assert "try_files {path} /index.html" in CADDY
    assert 'Cache-Control "public, max-age=31536000, immutable"' in CADDY
    assert 'Cache-Control "no-cache, no-store, must-revalidate"' in CADDY
    for value in (
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Permissions-Policy",
        "Content-Security-Policy",
        "sandbox.web.squarecdn.com",
        "web.squarecdn.com",
        "fonts.googleapis.com",
        "fonts.gstatic.com",
    ):
        assert value in CADDY


def test_hsts_is_safe_until_owner_validates_canonical_hostname():
    assert '{$GOPOSTAL_HSTS:max-age=0}' in CADDY
    assert "includeSubDomains" not in CADDY


def test_access_log_is_json_bounded_and_redacted():
    for value in (
        "gopostal-access.json",
        "roll_size 10MiB",
        "roll_keep 10",
        "Authorization delete",
        "Cookie delete",
        "replace token REDACTED",
        "replace code REDACTED",
    ):
        assert value in CADDY


def test_temporary_basic_auth_excludes_only_exact_webhook_path():
    assert "@protected not path /api/payments/webhook" in TEMPORARY
    assert "basic_auth @protected" in TEMPORARY
    assert "GOPOSTAL_BASIC_AUTH_USER" in TEMPORARY
    assert "GOPOSTAL_BASIC_AUTH_HASH" in TEMPORARY
    assert TEMPORARY.index("basic_auth @protected") < TEMPORARY.index("@webhook path")


def test_publish_script_uses_immutable_sha_directory_and_atomic_symlink():
    assert "/srv/gopostal/releases" in PUBLISH
    assert "/srv/gopostal/current" in PUBLISH
    assert 'if [ -e "$target" ]' in PUBLISH
    assert 'mv "$staging" "$target"' in PUBLISH
    assert 'ln -s "$target" "$temporary_link"' in PUBLISH
    assert 'mv -Tf "$temporary_link" "$current_link"' in PUBLISH
    assert "rm -rf" not in PUBLISH
