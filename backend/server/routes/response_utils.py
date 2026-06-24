"""Shared API response helpers for consistent structured payloads."""

from typing import Any, Dict, Optional


def _default_code(status_code: int) -> str:
    if status_code == 400:
        return 'BAD_REQUEST'
    if status_code == 401:
        return 'UNAUTHORIZED'
    if status_code == 403:
        return 'FORBIDDEN'
    if status_code == 404:
        return 'NOT_FOUND'
    if status_code == 409:
        return 'CONFLICT'
    if status_code >= 500:
        return 'INTERNAL_ERROR'
    return 'REQUEST_ERROR'


def _default_severity(status_code: int) -> str:
    if status_code >= 500:
        return 'high'
    if status_code in (401, 403):
        return 'medium'
    return 'low'


def error_response(
    message: str,
    status_code: int = 400,
    code: Optional[str] = None,
    category: str = 'validation',
    retryable: bool = False,
    details: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    payload: Dict[str, Any] = {
        'error': {
            'message': message,
            'code': code or _default_code(status_code),
            'category': category,
            'severity': _default_severity(status_code),
            'retryable': retryable,
        }
    }
    if details:
        payload['error']['details'] = details

    if headers:
        return payload, status_code, headers
    return payload, status_code
