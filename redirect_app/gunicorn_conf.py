# gunicorn_conf.py
import multiprocessing
import os

# ===== 포트 구성 =====
# 443: HTTPS - 루트 경로만 Vercel로 리다이렉트
# 8000: HTTP - /api/v1/* API 엔드포인트 처리

# 환경에 따라 포트 결정
port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"
backlog = 2048

# ===== SSL 설정 (443 포트 사용 시) =====
if port == "443":
    # Docker 환경에서는 /app/certs 경로 사용
    certfile = os.getenv("SSL_CERT_FILE", "/app/certs/mochachat.crt")
    keyfile = os.getenv("SSL_KEY_FILE", "/app/certs/mochachat.key")
    ssl_version = 5  # TLS 1.2+

# ===== 워커 설정 =====
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# ===== 타임아웃 =====
timeout = 30
keepalive = 5
graceful_timeout = 30

# ===== 로깅 =====
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ===== 프로세스 설정 =====
proc_name = "mochachat_api"
preload_app = True
worker_tmp_dir = "/dev/shm"

# ===== 보안 설정 =====
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# ===== 환경별 설정 =====
if os.getenv("ENV") == "development":
    reload = True
    workers = 2
    loglevel = "debug"
