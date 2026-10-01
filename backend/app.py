from server import create_server
import warnings
from flask import redirect, request, jsonify
import os



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



if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug, host=host, port=port)