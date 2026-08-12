"""Request-size limits applied before route services read request bodies."""

import os

from flask import jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge


DEFAULT_MULTIPART_LIMIT = 6 * 1024 * 1024
DEFAULT_JSON_LIMIT = 1024 * 1024


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be a positive integer") from error
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def configure_request_limits(app) -> None:
    multipart_limit = _positive_int("MAX_REQUEST_BYTES", DEFAULT_MULTIPART_LIMIT)
    json_limit = _positive_int("MAX_JSON_REQUEST_BYTES", DEFAULT_JSON_LIMIT)
    if json_limit > multipart_limit:
        raise ValueError("MAX_JSON_REQUEST_BYTES must not exceed MAX_REQUEST_BYTES")

    app.config["MAX_CONTENT_LENGTH"] = multipart_limit
    app.config["MAX_JSON_REQUEST_BYTES"] = json_limit

    @app.before_request
    def _reject_oversized_request():
        if (
            request.content_length is not None
            and request.content_length > multipart_limit
        ):
            raise RequestEntityTooLarge()
        if (
            request.mimetype == "application/json"
            and request.content_length is not None
            and request.content_length > json_limit
        ):
            raise RequestEntityTooLarge()

    @app.errorhandler(RequestEntityTooLarge)
    def _request_too_large(_error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "code": "REQUEST_TOO_LARGE",
                        "message": "Request body exceeds the allowed size",
                    },
                }
            ),
            413,
        )
