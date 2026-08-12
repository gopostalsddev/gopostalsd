"""GP-11 tests for canonical origin, CORS, CSRF, and proxy trust."""

from unittest.mock import patch

from flask import Flask, request
import pytest

from server import _configure_proxy_boundary, _resolve_cors_origins
from server.email_config import EmailConfigurationError, trusted_proxy_hops
from server.middleware.auth_middleware import _origin_is_allowed


def _remote_address(config: str, migration_mode: bool, environment: dict) -> str:
    app = Flask(__name__)
    with patch.dict("os.environ", environment, clear=True):
        _configure_proxy_boundary(app, config, migration_mode)

    @app.get("/")
    def index():
        return request.remote_addr

    response = app.test_client().get(
        "/", headers={"X-Forwarded-For": "198.51.100.20, 203.0.113.10"}
    )
    return response.get_data(as_text=True)


def test_production_cors_allows_only_the_unresolved_launch_variable_value():
    environment = {"PUBLIC_BASE_URL": "https://launch.example.test"}
    with patch.dict("os.environ", environment, clear=True):
        assert _resolve_cors_origins("production", False) == [
            "https://launch.example.test"
        ]


def test_production_cors_does_not_fall_back_to_render_or_frontend_variables():
    environment = {
        "FRONTEND_URL": "https://old-frontend.example.test",
        "RENDER_FRONTEND_URL": "https://old-render.example.test",
        "RENDER_EXTERNAL_URL": "https://api-provider.example.test",
    }
    with patch.dict("os.environ", environment, clear=True):
        with pytest.raises(EmailConfigurationError, match="PUBLIC_BASE_URL"):
            _resolve_cors_origins("production", False)


def test_migration_mode_needs_no_public_origin_and_exposes_no_cors_origin():
    with patch.dict("os.environ", {}, clear=True):
        assert _resolve_cors_origins("production", True) == []


@pytest.mark.parametrize("value", ("0", "2", "many"))
def test_proxy_hop_count_rejects_every_value_except_one(value):
    with patch.dict("os.environ", {"TRUSTED_PROXY_HOPS": value}, clear=True):
        with pytest.raises(EmailConfigurationError, match="exactly 1"):
            trusted_proxy_hops(required=True)


def test_direct_development_request_cannot_spoof_forwarded_client_address():
    assert _remote_address("development", False, {}) == "127.0.0.1"


def test_production_trusts_only_the_nearest_of_two_forwarded_addresses():
    assert _remote_address(
        "production", False, {"TRUSTED_PROXY_HOPS": "1"}
    ) == "203.0.113.10"


@pytest.mark.parametrize(
    "candidate",
    (
        "https://launch.example.test",
        "https://launch.example.test/checkout",
    ),
)
def test_origin_or_referer_on_canonical_host_is_allowed(candidate):
    assert _origin_is_allowed(candidate, ["https://launch.example.test"])


@pytest.mark.parametrize(
    "candidate",
    (
        "https://launch.example.test.evil.invalid",
        "https://evil.invalid/https://launch.example.test",
        "null",
    ),
)
def test_lookalike_or_opaque_origins_are_rejected(candidate):
    assert not _origin_is_allowed(candidate, ["https://launch.example.test"])
