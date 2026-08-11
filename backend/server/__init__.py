# Import required Flask extensions and modules
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from server.config import DevelopmentConfig, TestingConfig, ProductionConfig, validate_production_security_settings
from server.config import database, migrate, sinalite, swagger, filestorage
from server.models import * # So that they can be detected by migrations
from server.email_config import public_base_url, trusted_proxy_hops
import logging
import os
import sys

logger = logging.getLogger(__name__)


def _is_running_db_migrate() -> bool:
    if os.getenv("RUN_DB_MIGRATE"):
        return True
    return "db" in sys.argv


def _configure_proxy_boundary(server, config: str, migration_mode: bool) -> int:
    """Apply the explicit ingress trust boundary and return its hop count."""
    proxy_hops = trusted_proxy_hops(
        required=config == "production" and not migration_mode
    )
    if proxy_hops:
        server.wsgi_app = ProxyFix(
            server.wsgi_app,
            x_for=proxy_hops,
            x_proto=proxy_hops,
            x_host=proxy_hops,
        )
    return proxy_hops


def _resolve_cors_origins(config: str, migration_mode: bool) -> list[str]:
    """Resolve credentialed browser origins without provider-host fallbacks."""
    if config == "production" and not migration_mode:
        return [public_base_url(required=True)]
    if config == "production":
        return []

    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    render_frontend_url = os.getenv('RENDER_FRONTEND_URL')
    render_external_url = os.getenv('RENDER_EXTERNAL_URL')
    env_origins = [
        origin
        for origin in (frontend_url, render_frontend_url, render_external_url)
        if origin
    ]
    origins = [
        'http://localhost:5173',
        'http://localhost:3000',
        'http://localhost:8080',
        'https://localhost:5173',
    ]
    for origin in env_origins:
        if origin not in origins:
            origins.append(origin)
    return origins


def create_server(config="development", *, migration_mode=None):
    """
    Factory function to create and configure the Flask application.
    
    Args:
        config (str): Configuration environment to use ('development', 'testing', or 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    if migration_mode is None:
        migration_mode = _is_running_db_migrate()

    # Create Flask application instance
    server = Flask(__name__)
    server.config['MIGRATION_MODE'] = migration_mode

    # Runtime production is reachable through exactly one ingress proxy. Tests,
    # development, and one-shot migrations trust no forwarded headers by default.
    _configure_proxy_boundary(server, config, migration_mode)

    # Configure CORS with allowed origins
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    cors_origins = _resolve_cors_origins(config, migration_mode)

    if not cors_origins and not migration_mode:
        raise ValueError("No CORS origins configured for this environment")
    
    # Extract base domain for Codespaces (e.g., curly-spoon-jj57pprxw5q93qjwq)
    if config != "production" and frontend_url and 'github.dev' in frontend_url:
        # Extract the subdomain part
        import re
        match = re.search(r'https?://([^.]+)\.app\.github\.dev', frontend_url)
        if match:
            subdomain = match.group(1)
            # Add both port 5173 (frontend) and 5000 (backend) with this subdomain
            cors_origins.append(f'https://{subdomain}-5173.app.github.dev')
            cors_origins.append(f'https://{subdomain}-5000.app.github.dev')
    
    cors_config = {
        'origins': cors_origins,
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-CSRF-Token'],
        'supports_credentials': True,
        'max_age': 3600,
        'expose_headers': ['Content-Type', 'Authorization']
    }
    # Match all API endpoints (e.g., /api/auth/me), not just repeated slash paths.
    CORS(server, resources={r"/api/.*": cors_config})
    server.config['_CORS_ORIGINS'] = cors_origins

    # Enforce CSRF validation for authenticated state-changing requests.
    from server.middleware.auth_middleware import enforce_csrf_protection
    server.before_request(enforce_csrf_protection)

    @server.after_request
    def _add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        # API responses are JSON; CSP has no effect on them but does harden the
        # HTML error pages Flask renders for 404/500 etc.
        response.headers.setdefault('Content-Security-Policy', "default-src 'none'")
        return response
    
    # Add startup timestamp for health checks
    from datetime import datetime, timezone
    server.config['START_TIME'] = datetime.now(timezone.utc).isoformat()

    # Load configuration based on environment
    if config == "testing":
        server.config.from_object(TestingConfig)
    elif config == "production":
        # A one-shot migration never serves traffic and should not require
        # payment/webhook secrets merely to initialize Alembic. Runtime boot
        # still validates the complete production security contract.
        if not migration_mode:
            validate_production_security_settings()
        server.config.from_object(ProductionConfig)
    else:  # Default to development configuration
        server.config.from_object(DevelopmentConfig)

    # Log the loaded environment and Sinalite URL
    logger.info(f"Loaded Environment: {config}")
    logger.info(f"Sinalite: {server.config['SINALITE_BASE_URL']}")

    # Initialize database support
    database.init_app(server)

    # Initialize migration support. Models are imported at module load so
    # Alembic metadata is available without initializing routes/integrations.
    migrate.init_app(server, database)

    from server.cli import register_commands
    register_commands(server)

    if migration_mode:
        return server

    # Initialize sinalite api support
    sinalite.init_app(server)

    # Initialize swagger documentation
    swagger.init_app(server)

    # Initialize file storage for image storing
    filestorage.init_app(server)
    logger.info(f"File Storage: {filestorage.current_backend}")
    
    # Initialize services using factory pattern
    from server.factories.main_factory import MainFactory
    from server.thirdparty.sinalite import SinaliteAdapter
    
    # Create main factory and services
    main_factory = MainFactory()
    sinalite_adapter = SinaliteAdapter(server)
    pricing_service = main_factory.get_pricing_service(sinalite_adapter)
    cart_service = main_factory.get_cart_service(pricing_service, sinalite_adapter)
    email_service = main_factory.get_email_service()
    email_service.init_app(server)  # Initialize email service with Flask app
    password_service = main_factory.get_password_service()
    role_service = main_factory.get_role_service()
    auth_service = main_factory.get_auth_service()
    
    # Store in Flask app context for use in API routes
    server.extensions['main_factory'] = main_factory
    server.extensions['sinalite_adapter'] = sinalite_adapter
    server.extensions['pricing_service'] = pricing_service
    server.extensions['cart_service'] = cart_service
    server.extensions['email_service'] = email_service
    server.extensions['password_service'] = password_service
    server.extensions['role_service'] = role_service
    server.extensions['auth_service'] = auth_service
    
    # Warn when running production without a shared rate-limit store.
    # In-memory counters are per-worker and won't enforce limits across Gunicorn workers.
    if config == 'production':
        rate_store = os.getenv('AUTH_RATE_LIMIT_STORE', 'memory').lower()
        if rate_store == 'memory':
            logger.warning(
                "AUTH_RATE_LIMIT_STORE is 'memory' in production. "
                "Rate limits are not shared across Gunicorn workers. "
                "Set AUTH_RATE_LIMIT_STORE=redis and RATE_LIMIT_REDIS_URL."
            )

    # Register API routes
    from server.routes import register_routes
    register_routes(server)

    # Initialize centralized error handling and severity categorization.
    try:
        from server.exceptions.error_handler import ErrorHandler
        ErrorHandler(server)
    except ImportError:
        logger.warning("Advanced error handler dependencies are unavailable; continuing with default handlers")

    return server
