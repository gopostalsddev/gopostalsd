import os
from flask import current_app, send_from_directory, Blueprint, jsonify
from server.startup import verify_database_health, ensure_database_structures, check_database_tables_exist


api = Blueprint("misc", __name__)

@api.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "gopostalsd-backend",
        "timestamp": current_app.config.get('START_TIME', 'unknown')
    })


@api.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    # send_from_directory uses safe_join internally, which prevents path traversal.
    upload_folder = os.path.join(current_app.root_path, "uploads")
    return send_from_directory(upload_folder, filename)