from server import create_server
import warnings
from flask import redirect, request, jsonify
import os
import signal
import threading



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
    
    # Redirect to the Swagger documentation
    return redirect("/")

@app.route('/shutdown', methods=['POST'])
def shutdown():
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
    app.run(debug=debug, port=5000)