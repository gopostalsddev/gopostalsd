"""Canonical email and public-link configuration.

Production deliberately fails closed: the provider, sender identity, and public
origin must all be chosen explicitly.  This prevents a deploy from silently
sending through stale credentials or embedding an obsolete Render hostname in
account-action emails.
"""

from dataclasses import dataclass
import os
from urllib.parse import urlsplit


SUPPORTED_EMAIL_PROVIDERS = {"mailersend", "smtp"}
INTENDED_SENDER_ADDRESS = "support@gopostalsd.com"
DEFAULT_SENDER_NAME = "Go Postal SD"


class EmailConfigurationError(ValueError):
    """Raised when the email delivery contract is incomplete or ambiguous."""


@dataclass(frozen=True)
class EmailSettings:
    provider: str
    from_address: str
    from_name: str
    public_base_url: str


def _is_production() -> bool:
    return os.getenv("ENVIRONMENT", "development").strip().lower() == "production"


def _public_base_url(*, required: bool) -> str:
    value = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if not value:
        if required:
            raise EmailConfigurationError(
                "PUBLIC_BASE_URL must be set in production to the confirmed canonical launch origin"
            )
        return "http://localhost:5173"

    parsed = urlsplit(value)
    if (
        parsed.scheme not in ({"https"} if required else {"http", "https"})
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        requirement = "an HTTPS origin" if required else "an HTTP(S) origin"
        raise EmailConfigurationError(f"PUBLIC_BASE_URL must be {requirement} without a path")
    return value


def load_email_settings(*, required: bool | None = None) -> EmailSettings | None:
    """Load and validate the single supported email-provider configuration."""
    if required is None:
        required = _is_production()

    provider = os.getenv("EMAIL_PROVIDER", "").strip().lower()
    if not provider:
        if required:
            raise EmailConfigurationError("EMAIL_PROVIDER must be set in production")
        return None
    if provider not in SUPPORTED_EMAIL_PROVIDERS:
        raise EmailConfigurationError(
            "EMAIL_PROVIDER must be one of: mailersend, smtp"
        )

    from_address = os.getenv("EMAIL_FROM_ADDRESS", "").strip()
    from_name = os.getenv("EMAIL_FROM_NAME", "").strip()
    if required and not from_address:
        raise EmailConfigurationError("EMAIL_FROM_ADDRESS must be set in production")
    if required and not from_name:
        raise EmailConfigurationError("EMAIL_FROM_NAME must be set in production")
    from_address = from_address or INTENDED_SENDER_ADDRESS
    from_name = from_name or DEFAULT_SENDER_NAME

    mailersend_configured = bool(os.getenv("MAILERSEND_API_KEY", "").strip())
    smtp_configured = bool(
        os.getenv("SMTP_USERNAME", "").strip()
        or os.getenv("SMTP_PASSWORD", "").strip()
    )
    if mailersend_configured and smtp_configured:
        raise EmailConfigurationError(
            "Conflicting email credentials are configured; keep only the selected provider"
        )
    if provider == "mailersend" and required and not mailersend_configured:
        raise EmailConfigurationError("MAILERSEND_API_KEY must be set for MailerSend")
    if provider == "smtp":
        missing = [
            key for key in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD")
            if not os.getenv(key, "").strip()
        ]
        if required and missing:
            raise EmailConfigurationError(
                "Missing required SMTP configuration: " + ", ".join(missing)
            )
        if required and mailersend_configured:
            raise EmailConfigurationError(
                "MAILERSEND_API_KEY conflicts with EMAIL_PROVIDER=smtp"
            )

    return EmailSettings(
        provider=provider,
        from_address=from_address,
        from_name=from_name,
        public_base_url=_public_base_url(required=required),
    )


def validate_production_email_settings() -> None:
    """Validate production email configuration without contacting a provider."""
    load_email_settings(required=True)
