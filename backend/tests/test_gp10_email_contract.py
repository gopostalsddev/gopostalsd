"""GP-10 contract tests for deterministic email delivery and action links."""

import logging
from unittest.mock import Mock, patch

from flask import Flask
import pytest

from server.email_config import (
    EmailConfigurationError,
    load_email_settings,
    validate_production_email_settings,
)
from server.services.email_service import EmailService
from server.thirdparty.mailersend import MailerSendAdapter
from server.thirdparty.smtp import SMTPAdapter


BASE = {
    "ENVIRONMENT": "production",
    "EMAIL_PROVIDER": "mailersend",
    "EMAIL_FROM_ADDRESS": "support@gopostalsd.com",
    "EMAIL_FROM_NAME": "Go Postal SD",
    "MAILERSEND_API_KEY": "mock-mailersend-key",
    "PUBLIC_BASE_URL": "https://launch.example.test",
}


def test_approved_mailersend_configuration_is_explicit_and_complete():
    with patch.dict("os.environ", BASE, clear=True):
        settings = load_email_settings(required=True)
        validate_production_email_settings()

    assert settings.provider == "mailersend"
    assert settings.from_address == "support@gopostalsd.com"
    assert settings.public_base_url == "https://launch.example.test"


def test_smtp_can_be_selected_with_the_same_canonical_sender_vocabulary():
    smtp = {
        "ENVIRONMENT": "production",
        "EMAIL_PROVIDER": "smtp",
        "EMAIL_FROM_ADDRESS": "support@gopostalsd.com",
        "EMAIL_FROM_NAME": "Go Postal SD",
        "PUBLIC_BASE_URL": "https://launch.example.test",
        "SMTP_HOST": "smtp.example.test",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "mock-user",
        "SMTP_PASSWORD": "mock-password",
    }
    with patch.dict("os.environ", smtp, clear=True):
        settings = load_email_settings(required=True)
    assert settings.provider == "smtp"


@pytest.mark.parametrize(
    ("removed", "message"),
    (
        ("EMAIL_PROVIDER", "EMAIL_PROVIDER"),
        ("EMAIL_FROM_ADDRESS", "EMAIL_FROM_ADDRESS"),
        ("EMAIL_FROM_NAME", "EMAIL_FROM_NAME"),
        ("MAILERSEND_API_KEY", "MAILERSEND_API_KEY"),
        ("PUBLIC_BASE_URL", "PUBLIC_BASE_URL"),
    ),
)
def test_missing_production_email_configuration_fails_closed(removed, message):
    environment = dict(BASE)
    environment.pop(removed)
    with patch.dict("os.environ", environment, clear=True):
        with pytest.raises(EmailConfigurationError, match=message):
            load_email_settings(required=True)


def test_conflicting_provider_credentials_are_rejected():
    environment = dict(
        BASE,
        SMTP_HOST="smtp.example.test",
        SMTP_USERNAME="mock-user",
        SMTP_PASSWORD="mock-password",
    )
    with patch.dict("os.environ", environment, clear=True):
        with pytest.raises(EmailConfigurationError, match="Conflicting"):
            load_email_settings(required=True)


@pytest.mark.parametrize(
    "public_url",
    (
        "http://launch.example.test",
        "https://launch.example.test/a-path",
        "https://user:password@launch.example.test",
    ),
)
def test_production_public_origin_rejects_unsafe_or_noncanonical_values(public_url):
    environment = dict(BASE, PUBLIC_BASE_URL=public_url)
    with patch.dict("os.environ", environment, clear=True):
        with pytest.raises(EmailConfigurationError, match="PUBLIC_BASE_URL"):
            load_email_settings(required=True)


def test_service_selects_mailersend_and_uses_approved_sender():
    fake_adapter = Mock()
    fake_adapter.is_configured = True
    with (
        patch.dict("os.environ", BASE, clear=True),
        patch("server.services.email_service.MailerSendAdapter", return_value=fake_adapter),
    ):
        service = EmailService()
        service.init_app(Flask(__name__))

    assert service.provider == "mailersend"
    assert service.client is fake_adapter


def test_mailersend_adapter_uses_the_approved_sender_identity():
    with (
        patch.dict("os.environ", BASE, clear=True),
        patch("server.thirdparty.mailersend.MailerSendClient"),
    ):
        adapter = MailerSendAdapter()
    assert adapter.get_from_email() == "support@gopostalsd.com"
    assert adapter.get_from_name() == "Go Postal SD"


@pytest.mark.parametrize(
    ("method", "expected_path"),
    (
        ("send_verification_email", "/#/verify-email?token=token-value"),
        ("send_password_reset_email", "/#/reset-password?token=token-value"),
    ),
)
def test_account_action_links_use_confirmed_same_origin_hash_routes(
    method, expected_path
):
    with patch.dict("os.environ", BASE, clear=True):
        service = EmailService()
    service.client = Mock()
    service.client.send_email.return_value = {"success": True}

    result = getattr(service, method)(
        "customer@example.test", "Customer", "token-value"
    )

    assert result == {"success": True}
    positional = service.client.send_email.call_args.args
    assert f"https://launch.example.test{expected_path}" in positional[2]
    assert f"https://launch.example.test{expected_path}" in positional[3]


def test_mailersend_failure_does_not_log_or_return_provider_secret(caplog):
    secret = "super-secret-provider-detail"
    with (
        patch.dict("os.environ", BASE, clear=True),
        patch("server.thirdparty.mailersend.MailerSendClient") as client_type,
    ):
        client_type.return_value.emails.send.side_effect = RuntimeError(secret)
        adapter = MailerSendAdapter()
        with caplog.at_level(logging.ERROR):
            result = adapter.send_email(
                "customer@example.test", "Subject", "Text", "<p>Text</p>"
            )

    assert result["success"] is False
    assert result["error"] == "MailerSend delivery failed"
    assert secret not in caplog.text
    assert secret not in str(result)


def test_smtp_failure_does_not_log_or_return_provider_secret(caplog):
    secret = "super-secret-smtp-detail"
    smtp_environment = {
        "SMTP_HOST": "smtp.example.test",
        "SMTP_USERNAME": "mock-user",
        "SMTP_PASSWORD": "mock-password",
        "EMAIL_FROM_ADDRESS": "support@gopostalsd.com",
        "EMAIL_FROM_NAME": "Go Postal SD",
    }
    with (
        patch.dict("os.environ", smtp_environment, clear=True),
        patch("server.thirdparty.smtp.smtplib.SMTP") as smtp_type,
    ):
        smtp_type.return_value.__enter__.return_value.login.side_effect = RuntimeError(
            secret
        )
        adapter = SMTPAdapter()
        with caplog.at_level(logging.ERROR):
            result = adapter.send_email("customer@example.test", "Subject", "Text")

    assert result["success"] is False
    assert result["error"] == "SMTP delivery failed"
    assert secret not in caplog.text
    assert secret not in str(result)
