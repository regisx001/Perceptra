import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5555")

# Worker processes & threads
workers = int(os.getenv("GUNICORN_WORKERS", 2))
threads = int(os.getenv("GUNICORN_THREADS", 4))
worker_class = "gthread"

# Request timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))

# Worker recycling
max_requests = 1000
max_requests_jitter = 100

# Logging - '-' writes directly to stdout/stderr
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Detailed access log format: client_ip, timestamp, request line, status code, response length, latency in ms
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)sµs "%(a)s"'

# Avoid preloading in dev so changes and workers initialize cleanly
preload_app = False

# Capture stdout/stderr from print and application logs into gunicorn error log
capture_output = True
