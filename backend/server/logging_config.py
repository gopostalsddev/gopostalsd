"""Container-safe structured stdout logging."""

from datetime import datetime, timezone
import json
import logging
import logging.config
import os
import re
import traceback


_ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_REDACTIONS = (
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"), "Bearer [REDACTED]"),
    (
        re.compile(
            r"(?i)\b(password|authorization|api[_-]?key|secret|token|card[_-]?nonce)"
            r"\s*[:=]\s*[^\s,;]+"
        ),
        r"\1=[REDACTED]",
    ),
    (
        re.compile(r"(?i)([?&](?:token|key|secret|password)=)[^&#\s]+"),
        r"\1[REDACTED]",
    ),
    (
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
        "[EMAIL_REDACTED]",
    ),
)


def redact_log_message(value) -> str:
    """Remove common credentials and direct email identifiers from log text."""
    text = str(value)
    for pattern, replacement in _REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


class SafeJsonFormatter(logging.Formatter):
    """Emit one JSON object per record without exception-message leakage."""

    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_log_message(record.getMessage()),
        }
        if record.exc_info:
            exception_type = record.exc_info[0]
            payload["exception"] = {
                "type": exception_type.__name__ if exception_type else "Exception",
                "frames": [
                    {
                        "file": frame.filename,
                        "line": frame.lineno,
                        "function": frame.name,
                    }
                    for frame in traceback.extract_tb(record.exc_info[2])
                ],
            }
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)


def _log_level(environment: str) -> str:
    fallback = "DEBUG" if environment in {"development", "testing"} else "INFO"
    configured = os.getenv("LOG_LEVEL", fallback).strip().upper()
    if configured not in _ALLOWED_LEVELS:
        raise ValueError(
            "LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )
    return configured


def logging_configuration(environment):
    """Build the stdout-only logging configuration."""
    level = _log_level(environment)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"safe_json": {"()": SafeJsonFormatter}},
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "safe_json",
                "level": level,
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"handlers": ["stdout"], "level": level},
    }


def configure_logging(environment):
    """Configure stdout-only logging suitable for read-only containers."""
    logging.config.dictConfig(logging_configuration(environment))
