import multiprocessing

# Server socket
bind = "0.0.0.0:2906"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
accesslog = "./logs/access.log"
errorlog = "./logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "mcp_server"

# Timeout config
timeout = 120
keepalive = 5

# Server mechanics
daemon = False
pidfile = "./run/gunicorn.pid"
umask = 0o007
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Worker processes
worker_connections = 1000
max_requests = 0
max_requests_jitter = 0

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
