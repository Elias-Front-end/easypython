import multiprocessing

# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html#configuration-file

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Logging
accesslog = "-"  # Print to stdout
errorlog = "-"   # Print to stderr
loglevel = "info"

# Timeouts
timeout = 120    # Workers silent for more than this many seconds are killed and restarted
keepalive = 5

# Process naming
proc_name = "django_app"
