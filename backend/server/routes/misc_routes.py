import os
from flask import current_app, send_from_directory, Blueprint, abort


api = Blueprint("misc", __name__)

@api.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):

    # Prevent traversal attacks

    if "..." in filename or filename.startswith('/'):
        abort(400, "Invalid filename")

    upload_folder = os.path.join(current_app.root_path, "uploads")
    return  send_from_directory(os.path.join(upload_folder), filename)