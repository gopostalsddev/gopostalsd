"""GP-12 tests for stdout-only safe logs and database-aware readiness."""

import json
import logging
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask
import pytest

from server.logging_config import SafeJsonFormatter, _log_level, logging_configuration
from server.routes import misc_routes


class _Result:
    def scalar_one(self):
        return 1


class _Connection:
    def __init__(self, statements):
        self.statements = statements

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, statement, parameters=None):
        self.statements.append((str(statement), parameters or {}))
        return _Result()


class _Engine:
    def __init__(self, dialect="postgresql", failure=None):
        self.dialect = SimpleNamespace(name=dialect)
        self.failure = failure
        self.statements = []

    def connect(self):
        if self.failure:
            raise self.failure
        return _Connection(self.statements)


def _health_app():
    app = Flask(__name__)
    app.config["START_TIME"] = "test"
    app.register_blueprint(misc_routes.api)
    return app


@pytest.mark.parametrize("level", ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"))
def test_documented_log_levels_are_honored(level):
    with patch.dict("os.environ", {"LOG_LEVEL": level}, clear=True):
        assert _log_level("production") == level


def test_invalid_log_level_fails_closed():
    with patch.dict("os.environ", {"LOG_LEVEL": "everything"}, clear=True):
        with pytest.raises(ValueError, match="LOG_LEVEL"):
            _log_level("production")


def test_runtime_logging_has_no_file_handler_or_file_path():
    with patch.dict("os.environ", {"LOG_LEVEL": "INFO"}, clear=True):
        configuration = logging_configuration("production")
    serialized = json.dumps(configuration, default=str)
    assert list(configuration["handlers"]) == ["stdout"]
    assert "FileHandler" not in serialized
    assert "app.log" not in serialized


def test_safe_json_formatter_redacts_credentials_email_and_exception_message():
    secret = "provider-secret-value"
    try:
        raise RuntimeError(secret)
    except RuntimeError:
        record = logging.LogRecord(
            "gopostal.test",
            logging.ERROR,
            __file__,
            1,
            "Authorization=Bearer abc123 token=reset-value customer@example.test",
            (),
            __import__("sys").exc_info(),
        )

    rendered = SafeJsonFormatter().format(record)
    payload = json.loads(rendered)

    assert payload["level"] == "ERROR"
    assert "Bearer abc123" not in rendered
    assert "reset-value" not in rendered
    assert "customer@example.test" not in rendered
    assert secret not in rendered
    assert payload["exception"]["type"] == "RuntimeError"


def test_liveness_does_not_call_database():
    app = _health_app()
    with patch.object(
        misc_routes, "_database_ready", side_effect=AssertionError("DB was called")
    ):
        response = app.test_client().get("/health/live")
    assert response.status_code == 200
    assert response.get_json() == {
        "service": "gopostalsd-backend",
        "status": "alive",
    }


def test_readiness_succeeds_only_after_database_select_one():
    app = _health_app()
    with patch.object(misc_routes, "_database_ready", return_value=True):
        response = app.test_client().get("/health/ready")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ready"


def test_readiness_failure_is_a_safe_503():
    app = _health_app()
    with patch.object(misc_routes, "_database_ready", return_value=False):
        response = app.test_client().get("/health/ready")
    assert response.status_code == 503
    assert response.get_json() == {
        "service": "gopostalsd-backend",
        "status": "not_ready",
    }


def test_postgres_readiness_probe_is_bounded_and_read_only():
    app = _health_app()
    app.config["READINESS_DB_TIMEOUT_MS"] = 1750
    engine = _Engine()
    with app.app_context():
        assert misc_routes._database_ready(engine) is True

    assert len(engine.statements) == 2
    assert "set_config('statement_timeout'" in engine.statements[0][0]
    assert engine.statements[0][1] == {"timeout_ms": "1750"}
    assert engine.statements[1][0].strip() == "SELECT 1"
    forbidden = ("INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP")
    assert not any(
        keyword in statement.upper()
        for statement, _parameters in engine.statements
        for keyword in forbidden
    )


def test_database_failure_details_are_not_returned_or_logged(caplog):
    secret = "postgresql://user:password@private/db"
    app = _health_app()
    with app.app_context(), caplog.at_level(logging.WARNING):
        assert misc_routes._database_ready(_Engine(failure=RuntimeError(secret))) is False
    assert secret not in caplog.text


def test_legacy_health_path_remains_shallow_liveness():
    response = _health_app().test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "alive"
