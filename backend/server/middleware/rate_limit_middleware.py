"""Per-IP rate limiting decorators with optional Redis backing."""

import logging
import time
from collections import defaultdict, deque
from functools import wraps
from threading import Lock

from flask import current_app, request

try:
    import redis
except ImportError:  # pragma: no cover - handled via in-memory fallback
    redis = None


logger = logging.getLogger(__name__)

_RATE_LIMIT_BUCKETS = defaultdict(deque)
_RATE_LIMIT_LOCK = Lock()
_REDIS_CLIENT = None
_REDIS_CLIENT_URL = None
_REDIS_CLIENT_LOCK = Lock()


def _get_client_ip() -> str:
    """Return best-effort client IP, preferring the first forwarded address."""
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip() or 'unknown'
    return request.remote_addr or 'unknown'


def _rate_limit_response():
    """Return a structured 429 payload without importing route modules."""
    return {
        'error': {
            'message': 'Too many requests. Please try again later.',
            'code': 'RATE_LIMIT_EXCEEDED',
            'category': 'security',
            'severity': 'low',
            'retryable': True,
        }
    }, 429


def _memory_is_rate_limited(bucket_key: str, limit: int, window_seconds: int, now: float) -> bool:
    """Use in-process memory buckets for rate limiting."""
    with _RATE_LIMIT_LOCK:
        attempts = _RATE_LIMIT_BUCKETS[bucket_key]
        cutoff = now - window_seconds
        while attempts and attempts[0] <= cutoff:
            attempts.popleft()

        if len(attempts) >= limit:
            return True

        attempts.append(now)
        return False


def _get_redis_client():
    """Return a cached Redis client when configured and available."""
    global _REDIS_CLIENT, _REDIS_CLIENT_URL

    if redis is None:
        return None

    redis_url = current_app.config.get('RATE_LIMIT_REDIS_URL', '')
    if not redis_url:
        return None

    with _REDIS_CLIENT_LOCK:
        if _REDIS_CLIENT is not None and _REDIS_CLIENT_URL == redis_url:
            return _REDIS_CLIENT

        try:
            client = redis.Redis.from_url(redis_url, decode_responses=True)
            client.ping()
            _REDIS_CLIENT = client
            _REDIS_CLIENT_URL = redis_url
            return _REDIS_CLIENT
        except Exception:
            logger.warning('Redis rate limit backend unavailable; falling back to in-memory store', exc_info=True)
            _REDIS_CLIENT = None
            _REDIS_CLIENT_URL = None
            return None


def _redis_is_rate_limited(bucket_key: str, limit: int, window_seconds: int) -> bool:
    """Use Redis atomic counters for distributed rate limiting."""
    client = _get_redis_client()
    if not client:
        return False

    redis_key = f'rate-limit:{bucket_key}'
    try:
        request_count = client.incr(redis_key)
        if request_count == 1:
            client.expire(redis_key, window_seconds)
        return request_count > limit
    except Exception:
        logger.warning('Redis rate limit operation failed; falling back to in-memory store', exc_info=True)
        return False


def reset_rate_limit_state() -> None:
    """Reset in-memory limiter state (used by tests)."""
    global _REDIS_CLIENT, _REDIS_CLIENT_URL
    with _RATE_LIMIT_LOCK:
        _RATE_LIMIT_BUCKETS.clear()
    with _REDIS_CLIENT_LOCK:
        _REDIS_CLIENT = None
        _REDIS_CLIENT_URL = None


def rate_limit_by_ip(
    limit_config_key: str,
    window_config_key: str,
    key_prefix: str,
):
    """Rate limit requests by client IP using configured limit/window values."""
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_app.config.get('AUTH_RATE_LIMIT_ENABLED', True):
                return func(*args, **kwargs)

            limit = int(current_app.config.get(limit_config_key, 10))
            window_seconds = int(current_app.config.get(window_config_key, 60))
            if limit <= 0 or window_seconds <= 0:
                return func(*args, **kwargs)

            client_ip = _get_client_ip()
            now = time.time()
            bucket_key = f"{key_prefix}:{client_ip}"
            store = str(current_app.config.get('AUTH_RATE_LIMIT_STORE', 'memory')).lower()

            is_rate_limited = False
            if store in {'redis', 'auto'}:
                is_rate_limited = _redis_is_rate_limited(bucket_key, limit, window_seconds)

            if not is_rate_limited:
                should_use_memory = store == 'memory' or store == 'auto'
                if should_use_memory:
                    is_rate_limited = _memory_is_rate_limited(bucket_key, limit, window_seconds, now)

            if is_rate_limited:
                return _rate_limit_response()

            return func(*args, **kwargs)

        return wrapped

    return decorator
