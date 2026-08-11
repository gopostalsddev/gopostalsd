"""GP-04 tests for one explicit frontend/backend Square environment."""

from unittest.mock import patch

import pytest

from server.config import validate_production_security_settings
from server.square_config import (
    SquareConfigurationError,
    resolve_square_environment,
    validate_square_configuration,
)
from server.thirdparty import square as square_module


SANDBOX = {
    "SQUARE_ENVIRONMENT": "sandbox",
    "SQUARE_ACCESS_TOKEN": "test-token",
    "SQUARE_APPLICATION_ID": "sandbox-sq0idb-test-app",
    "SQUARE_LOCATION_ID": "test-location",
}
PRODUCTION = {
    "SQUARE_ENVIRONMENT": "production",
    "SQUARE_ACCESS_TOKEN": "production-token",
    "SQUARE_APPLICATION_ID": "sq0idp-production-app",
    "SQUARE_LOCATION_ID": "production-location",
}


def test_environment_is_required_and_allowlisted():
    with pytest.raises(SquareConfigurationError, match="explicitly set"):
        resolve_square_environment(environ={})
    with pytest.raises(SquareConfigurationError, match="sandbox or production"):
        resolve_square_environment(environ={"SQUARE_ENVIRONMENT": "staging"})


def test_explicit_override_cannot_disagree_with_environment():
    with pytest.raises(SquareConfigurationError, match="conflicts"):
        resolve_square_environment("production", SANDBOX)


@pytest.mark.parametrize("configuration", (SANDBOX, PRODUCTION))
def test_matching_complete_configuration_passes(configuration):
    assert validate_square_configuration(environ=configuration) == configuration[
        "SQUARE_ENVIRONMENT"
    ]


@pytest.mark.parametrize(
    ("environment", "application_id"),
    (
        ("sandbox", "sq0idp-production-app"),
        ("production", "sandbox-sq0idb-test-app"),
    ),
)
def test_application_id_from_other_environment_is_rejected(
    environment, application_id
):
    configuration = dict(SANDBOX)
    configuration.update(
        SQUARE_ENVIRONMENT=environment,
        SQUARE_APPLICATION_ID=application_id,
    )
    with pytest.raises(SquareConfigurationError, match="does not match"):
        validate_square_configuration(environ=configuration)


def test_partial_credentials_are_rejected_without_printing_values():
    configuration = dict(SANDBOX)
    configuration.pop("SQUARE_LOCATION_ID")
    with pytest.raises(SquareConfigurationError) as error:
        validate_square_configuration(environ=configuration)
    assert "SQUARE_LOCATION_ID" in str(error.value)
    assert configuration["SQUARE_ACCESS_TOKEN"] not in str(error.value)


def test_square_adapter_passes_authoritative_environment_to_sdk():
    captured = {}

    class FakeSquareClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    with (
        patch.dict("os.environ", SANDBOX, clear=False),
        patch.object(square_module, "SQUARE_AVAILABLE", True),
        patch.object(square_module, "SDK_CLIENT_KIND", "client"),
        patch.object(square_module, "SquareClient", FakeSquareClient),
    ):
        adapter = square_module.SquareAdapter()

    assert adapter.is_configured is True
    assert adapter.environment == "sandbox"
    assert captured["environment"] == "sandbox"
    assert captured["access_token"] == SANDBOX["SQUARE_ACCESS_TOKEN"]


def test_production_security_validation_requires_coherent_square_config():
    base = {
        "DEBUG": "false",
        "SESSION_COOKIE_SECURE": "true",
        "SECRET_KEY": "gp04-production-secret",
        "JWT_SECRET_KEY": "gp04-production-jwt",
        "SQUARE_MOCK_PAYMENTS": "false",
        "SQUARE_WEBHOOK_SIGNATURE_KEY": "gp04-webhook",
        "SQUARE_WEBHOOK_URL": "https://example.invalid/api/payments/webhook",
        "OAUTH_TOKEN_ENCRYPTION_KEY": "gp04-oauth-key",
        **PRODUCTION,
    }
    with patch.dict("os.environ", base, clear=True):
        validate_production_security_settings()

    mismatched = dict(base, SQUARE_APPLICATION_ID="sandbox-sq0idb-wrong")
    with patch.dict("os.environ", mismatched, clear=True):
        with pytest.raises(SquareConfigurationError, match="does not match"):
            validate_production_security_settings()
