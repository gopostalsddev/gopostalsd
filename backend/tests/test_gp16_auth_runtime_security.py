"""GP-16 authentication oracle, runtime, and bootstrap controls."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from server.config import database, validate_production_security_settings
from server.models.auth import Role, User, UserStatus
from server.services.password_service import PasswordService


ROOT = Path(__file__).resolve().parents[2]
SERVER_INIT = (ROOT / "backend/server/__init__.py").read_text(encoding="utf-8")
DOCKERFILE = (ROOT / "backend/Dockerfile").read_text(encoding="utf-8")
COMPOSE = (ROOT / "deploy/gopostal/docker-compose.production.yml").read_text(encoding="utf-8")


def _user(role, email, password_hash, status, verified, locked=False):
    return User(
        first_name="Security",
        last_name="Test",
        email=email,
        password_hash=password_hash,
        status=status,
        email_verified=verified,
        role_id=role.id,
        locked_until=(
            datetime.now(timezone.utc) + timedelta(minutes=30) if locked else None
        ),
    )


def test_wrong_password_is_uniform_for_every_account_state(app):
    password_service = PasswordService()
    correct_hash = password_service.hash_password("Correct-password-1!")

    with app.app_context():
        role = Role(name="GP16Customer", description="GP16 test role")
        database.session.add(role)
        database.session.flush()
        users = (
            _user(role, "active@example.test", correct_hash, UserStatus.ACTIVE, True),
            _user(role, "pending@example.test", correct_hash, UserStatus.PENDING_VERIFICATION, False),
            _user(role, "suspended@example.test", correct_hash, UserStatus.SUSPENDED, True),
            _user(role, "deactivated@example.test", correct_hash, UserStatus.DEACTIVATED, True),
            _user(role, "locked@example.test", correct_hash, UserStatus.ACTIVE, True, locked=True),
            _user(role, "oauth@example.test", None, UserStatus.ACTIVE, True),
        )
        database.session.add_all(users)
        database.session.flush()

        auth_service = app.extensions["auth_service"]
        results = [
            auth_service.login(user.email, "Wrong-password-1!") for user in users
        ]
        results.append(
            auth_service.login("unknown@example.test", "Wrong-password-1!")
        )

    assert {
        (result["error"], result["code"], tuple(sorted(result)))
        for result in results
    } == {
        (
            "Invalid email or password",
            "INVALID_CREDENTIALS",
            ("code", "error", "success"),
        )
    }


def test_account_state_is_disclosed_only_after_correct_password(app):
    password_service = PasswordService()
    password = "Correct-password-1!"

    with app.app_context():
        role = Role(name="GP16VerifiedCaller", description="GP16 state test")
        database.session.add(role)
        database.session.flush()
        pending = _user(
            role,
            "pending-correct@example.test",
            password_service.hash_password(password),
            UserStatus.PENDING_VERIFICATION,
            False,
        )
        database.session.add(pending)
        database.session.flush()

        result = app.extensions["auth_service"].login(pending.email, password)

    assert result["code"] == "EMAIL_NOT_VERIFIED"
    assert result["requires_verification"] is True
    assert result["email"] == "pending-correct@example.test"


def _validate_with_provider_checks_stubbed(environment):
    with (
        patch.dict("os.environ", environment, clear=True),
        patch("server.config.validate_square_configuration"),
        patch("server.config.square_webhook_url"),
        patch("server.config.validate_production_email_settings"),
        patch("server.config.trusted_proxy_hops"),
        patch("server.config.validate_production_storage_settings"),
    ):
        validate_production_security_settings()


def _base_security_environment():
    return {
        "DEBUG": "false",
        "FLASK_DEBUG": "0",
        "ENABLE_SWAGGER_UI": "false",
        "SESSION_COOKIE_SECURE": "true",
        "SECRET_KEY": "gp16-production-secret",
        "JWT_SECRET_KEY": "gp16-production-jwt",
        "SQUARE_MOCK_PAYMENTS": "false",
        "SQUARE_WEBHOOK_SIGNATURE_KEY": "gp16-signature",
        "OAUTH_TOKEN_ENCRYPTION_KEY": "gp16-oauth-key",
    }


@pytest.mark.parametrize(
    "override, message",
    (
        ({"DEBUG": "true"}, "DEBUG"),
        ({"FLASK_DEBUG": "1"}, "FLASK_DEBUG"),
        ({"ENABLE_SWAGGER_UI": "true"}, "Swagger"),
        ({"ADMIN_PASSWORD": "must-not-persist"}, "ADMIN_"),
        ({"ADMIN_EMAIL": "admin@example.test"}, "ADMIN_"),
    ),
)
def test_production_rejects_debug_docs_and_persisted_bootstrap_secrets(override, message):
    environment = {**_base_security_environment(), **override}
    with pytest.raises(ValueError, match=message):
        _validate_with_provider_checks_stubbed(environment)


def test_one_time_bootstrap_requires_explicit_command_and_complete_credentials():
    environment = {
        **_base_security_environment(),
        "RUN_ADMIN_BOOTSTRAP": "true",
        "ADMIN_EMAIL": "admin@example.test",
        "ADMIN_PASSWORD": "one-time-value",
    }
    with patch("sys.argv", ["flask", "bootstrap-admin"]):
        _validate_with_provider_checks_stubbed(environment)

    incomplete = dict(environment)
    incomplete.pop("ADMIN_PASSWORD")
    with (
        patch("sys.argv", ["flask", "bootstrap-admin"]),
        pytest.raises(ValueError, match="requires ADMIN_EMAIL and ADMIN_PASSWORD"),
    ):
        _validate_with_provider_checks_stubbed(incomplete)


def test_production_omits_swagger_spec_and_uses_one_worker():
    assert "swagger.init_app(server, add_specs=config != 'production')" in SERVER_INIT
    assert '"--workers", "1"' in DOCKERFILE
    assert 'DEBUG: "false"' in COMPOSE
    assert 'FLASK_DEBUG: "0"' in COMPOSE
    assert 'ENABLE_SWAGGER_UI: "false"' in COMPOSE
