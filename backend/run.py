from server import create_server
import warnings

# Suppress warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module='flask_restx')
server = create_server()
if __name__ == "__main__":
    server.run(debug=True)