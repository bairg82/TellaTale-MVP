"""
Gunicorn configuration file for TellaTale MVP application
"""

# Server bind settings
bind = "0.0.0.0:5000"

# Worker settings
workers = 1
worker_class = "gevent"

# Timeout settings
timeout = 300

# Reload code when it changes
reload = True

# Log settings
loglevel = "info"