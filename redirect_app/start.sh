#!/bin/bash

export ENV=${ENV:-production}
export LOG_LEVEL=${LOG_LEVEL:-info}
export PORT=443
export SSL_CERT_FILE=${SSL_CERT_FILE:-/etc/ssl/certs/mochachat.crt}
export SSL_KEY_FILE=${SSL_KEY_FILE:-/etc/ssl/private/mochachat.key}

# 인증서 확인
if [ ! -f "$SSL_CERT_FILE" ] || [ ! -f "$SSL_KEY_FILE" ]; then
    echo "SSL 인증서를 찾을 수 없습니다."
    echo "sudo ./generate_cert.sh 를 먼저 실행하세요."
    exit 1
fi

# root 권한 확인
if [ "$EUID" -ne 0 ]; then
    echo "443 포트는 sudo 권한이 필요합니다."
    exit 1
fi

echo "Starting HTTPS Server on port 443..."
gunicorn app:app --config gunicorn_conf.py
