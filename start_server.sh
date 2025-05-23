#!/bin/bash
# Custom shell script to start the TellaTale application with gevent worker and proper timeout

# Kill any existing gunicorn processes
pkill -f gunicorn || true

# Start the server with gevent worker class and 120s timeout
echo "Starting TellaTale application with gevent worker and 120s timeout..."
exec gunicorn --worker-class gevent --timeout 120 --bind 0.0.0.0:5000 main:app