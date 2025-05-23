"""
Custom server script for TellaTale using gevent WSGI server
with longer timeout settings to handle streaming responses.
"""
import os
from gevent.pywsgi import WSGIServer
from main import app

# Port configuration - use the port specified by Replit or default to 8080
port = int(os.environ.get('PORT', 8080))

if __name__ == '__main__':
    print(f"Starting TellaTale application with gevent WSGIServer on port {port}...")
    print("Using gevent worker with 120 second timeout for streaming support")
    
    # Create WSGIServer with longer timeout settings
    http_server = WSGIServer(('0.0.0.0', port), app, timeout=120)
    
    # Start the server
    http_server.serve_forever()