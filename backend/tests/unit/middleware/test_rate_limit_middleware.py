"""Unit tests for rate limit middleware Redis behavior."""

from unittest.mock import Mock

from server.middleware import rate_limit_middleware as rlm


class _RedisModuleStub:
    class Redis:
        from_url = None


def test_redis_counter_limits_after_threshold(app):
    rlm.reset_rate_limit_state()
    app.config['RATE_LIMIT_REDIS_URL'] = 'redis://example:6379/0'

    redis_client = Mock()
    redis_client.incr.side_effect = [1, 2, 3]
    redis_client.ping.return_value = True

    redis_module = _RedisModuleStub()
    redis_module.Redis.from_url = Mock(return_value=redis_client)

    original_redis_module = rlm.redis
    try:
        rlm.redis = redis_module

        with app.app_context():
            assert rlm._redis_is_rate_limited('auth-login:198.51.100.1', 2, 60) is False
            assert rlm._redis_is_rate_limited('auth-login:198.51.100.1', 2, 60) is False
            assert rlm._redis_is_rate_limited('auth-login:198.51.100.1', 2, 60) is True

        redis_client.expire.assert_called_once_with('rate-limit:auth-login:198.51.100.1', 60)
    finally:
        rlm.redis = original_redis_module
        rlm.reset_rate_limit_state()


def test_rate_limit_decorator_uses_redis_store(app):
    rlm.reset_rate_limit_state()
    app.config.update(
        AUTH_RATE_LIMIT_ENABLED=True,
        AUTH_RATE_LIMIT_STORE='redis',
        RATE_LIMIT_REDIS_URL='redis://example:6379/0',
        AUTH_LOGIN_RATE_LIMIT_COUNT=1,
        AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS=60,
    )

    redis_client = Mock()
    redis_client.incr.side_effect = [1, 2]
    redis_client.ping.return_value = True

    redis_module = _RedisModuleStub()
    redis_module.Redis.from_url = Mock(return_value=redis_client)

    original_redis_module = rlm.redis
    try:
        rlm.redis = redis_module

        @rlm.rate_limit_by_ip('AUTH_LOGIN_RATE_LIMIT_COUNT', 'AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS', 'auth-login')
        def protected_endpoint():
            return {'ok': True}, 200

        with app.test_request_context('/api/auth/login', method='POST', headers={'X-Forwarded-For': '198.51.100.2'}):
            first_response = protected_endpoint()

        with app.test_request_context('/api/auth/login', method='POST', headers={'X-Forwarded-For': '198.51.100.2'}):
            second_response = protected_endpoint()

        assert first_response[1] == 200
        assert second_response[1] == 429
        assert second_response[0]['error']['code'] == 'RATE_LIMIT_EXCEEDED'

        # In redis-only mode we should not maintain memory bucket entries.
        assert len(rlm._RATE_LIMIT_BUCKETS) == 0
    finally:
        rlm.redis = original_redis_module
        rlm.reset_rate_limit_state()


def test_auto_store_falls_back_to_memory_when_redis_unavailable(app):
    rlm.reset_rate_limit_state()
    app.config.update(
        AUTH_RATE_LIMIT_ENABLED=True,
        AUTH_RATE_LIMIT_STORE='auto',
        RATE_LIMIT_REDIS_URL='redis://example:6379/0',
        AUTH_LOGIN_RATE_LIMIT_COUNT=1,
        AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS=60,
    )

    redis_client = Mock()
    redis_client.ping.side_effect = RuntimeError('redis down')

    redis_module = _RedisModuleStub()
    redis_module.Redis.from_url = Mock(return_value=redis_client)

    original_redis_module = rlm.redis
    try:
        rlm.redis = redis_module

        @rlm.rate_limit_by_ip('AUTH_LOGIN_RATE_LIMIT_COUNT', 'AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS', 'auth-login')
        def protected_endpoint():
            return {'ok': True}, 200

        with app.test_request_context('/api/auth/login', method='POST', headers={'X-Forwarded-For': '198.51.100.3'}):
            first_response = protected_endpoint()

        with app.test_request_context('/api/auth/login', method='POST', headers={'X-Forwarded-For': '198.51.100.3'}):
            second_response = protected_endpoint()

        assert first_response[1] == 200
        assert second_response[1] == 429
        assert second_response[0]['error']['code'] == 'RATE_LIMIT_EXCEEDED'

        # Auto mode should have persisted attempts in the in-memory fallback.
        assert 'auth-login:198.51.100.3' in rlm._RATE_LIMIT_BUCKETS
    finally:
        rlm.redis = original_redis_module
        rlm.reset_rate_limit_state()
