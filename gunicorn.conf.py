# gunicorn.conf.py

bind = "0.0.0.0:7000"

# Number of worker processes
workers = 4

# Threads per worker
threads = 2

# Worker class
worker_class = "gthread"

# Request timeout
timeout = 120

# Graceful shutdown timeout
graceful_timeout = 30

# Maximum requests handled by a worker before restarting
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Avoid loading the application before workers are forked
preload_app = False
