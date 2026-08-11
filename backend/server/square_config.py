"""Single authoritative Square environment contract."""

from __future__ import annotations

import os
from typing import Mapping


VALID_SQUARE_ENVIRONMENTS = frozenset({"sandbox", "production"})
APPLICATION_ID_PREFIX = {
    "sandbox": "sandbox-sq0idb-",
    "production": "sq0idp-",
}
REQUIRED_CREDENTIAL_KEYS = (
    "SQUARE_ACCESS_TOKEN",
    "SQUARE_APPLICATION_ID",
    "SQUARE_LOCATION_ID",
)


class SquareConfigurationError(ValueError):
    """Raised when Square configuration is absent, ambiguous, or inconsistent."""


def resolve_square_environment(
    explicit: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Resolve one explicit environment and reject caller/environment drift."""
    values = os.environ if environ is None else environ
    configured = values.get("SQUARE_ENVIRONMENT", "").strip().lower()
    requested = (explicit or "").strip().lower()
    if requested and configured and requested != configured:
        raise SquareConfigurationError(
            "Square environment override conflicts with SQUARE_ENVIRONMENT"
        )
    environment = requested or configured
    if environment not in VALID_SQUARE_ENVIRONMENTS:
        raise SquareConfigurationError(
            "SQUARE_ENVIRONMENT must be explicitly set to sandbox or production"
        )
    return environment


def validate_square_application_id(environment: str, application_id: str) -> None:
    """Reject frontend/backend application IDs belonging to the other environment."""
    expected_prefix = APPLICATION_ID_PREFIX[environment]
    if not application_id.startswith(expected_prefix):
        raise SquareConfigurationError(
            "SQUARE_APPLICATION_ID does not match SQUARE_ENVIRONMENT"
        )


def validate_square_configuration(
    *,
    explicit_environment: str | None = None,
    environ: Mapping[str, str] | None = None,
    require_credentials: bool = True,
) -> str:
    """Validate environment and credential completeness without exposing values."""
    values = os.environ if environ is None else environ
    environment = resolve_square_environment(explicit_environment, values)
    configured = {
        key: bool(values.get(key, "").strip()) for key in REQUIRED_CREDENTIAL_KEYS
    }
    if require_credentials and not all(configured.values()):
        missing = ", ".join(key for key, present in configured.items() if not present)
        raise SquareConfigurationError(f"Missing required Square configuration: {missing}")
    if configured["SQUARE_APPLICATION_ID"]:
        validate_square_application_id(
            environment, values["SQUARE_APPLICATION_ID"].strip()
        )
    return environment
