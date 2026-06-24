from server import create_server
import warnings
from flask import redirect, request, jsonify
import os
import signal
import threading
import hmac



# Suppress warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module='flask_restx')

# Get the environment from .env or default to 'development'
environment = os.getenv("ENVIRONMENT", "development")
debug = os.getenv("DEBUG", "false").lower() == "true"

# Pass the environment explicitly to the factory function
app = create_server(config=environment)

# Create the root route
@app.route("/api")
def api():
    if environment == "production":
        return jsonify({"error": "Not found"}), 404

    # Redirect to API documentation in non-production environments.
    return redirect("/docs")

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if environment == "production":
        return jsonify({"error": "Not found"}), 404

    remote_addr = request.remote_addr or ""
    if remote_addr not in {"127.0.0.1", "::1"}:
        return jsonify({"error": "Forbidden"}), 403

    shutdown_token = os.getenv("SHUTDOWN_TOKEN")
    provided_token = request.headers.get("X-Shutdown-Token", "")
    if not shutdown_token or not hmac.compare_digest(provided_token, shutdown_token):
        return jsonify({"error": "Forbidden"}), 403

    app.logger.info("Shutting down Flask server...")

    def shutdown_server():
        """Gracefully shuts down Flask after sending response."""
        import time
        time.sleep(1)  # ✅ Short delay to ensure response is sent
        os.kill(os.getpid(), signal.SIGTERM)

    # ✅ Start shutdown in a separate thread to allow response to be sent
    threading.Thread(target=shutdown_server).start()

    return "Server shutting down..."

  
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug, host=host, port=port)