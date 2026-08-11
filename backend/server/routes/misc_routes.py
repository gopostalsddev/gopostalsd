import os

from flask import Blueprint, current_app, jsonify, send_from_directory
from sqlalchemy import text

from server.config import database


api = Blueprint("misc", __name__)


def _database_ready(engine=None) -> bool:
    """Perform a bounded, read-only connectivity probe outside the ORM session."""
    engine = engine or database.engine
    try:
        with engine.connect() as connection:
            if engine.dialect.name == "postgresql":
                timeout_ms = int(
                    current_app.config.get("READINESS_DB_TIMEOUT_MS", 2000)
                )
                connection.execute(
                    text("SELECT set_config('statement_timeout', :timeout_ms, true)"),
                    {"timeout_ms": str(timeout_ms)},
                )
            result = connection.execute(text("SELECT 1")).scalar_one()
            return result == 1
    except Exception:
        current_app.logger.warning("Database readiness probe failed")
        return False


@api.get('/health/live')
def health_live():
    """Process liveness only; no database or provider dependency."""
    return jsonify({"status": "alive", "service": "gopostalsd-backend"})


@api.get('/health/ready')
def health_ready():
    """Database-aware readiness; external providers are deliberately excluded."""
    ready = _database_ready()
    return (
        jsonify(
            {
                "status": "ready" if ready else "not_ready",
                "service": "gopostalsd-backend",
            }
        ),
        200 if ready else 503,
    )


@api.get('/health')
def health_compatibility():
    """Backward-compatible shallow health endpoint."""
    return health_live()


@api.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    # send_from_directory uses safe_join internally, which prevents path traversal.
    upload_folder = os.path.join(current_app.root_path, "uploads")
    return send_from_directory(upload_folder, filename)
