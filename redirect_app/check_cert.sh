#!/bin/bash

echo "인증서 정보 확인"
echo ""

# 로컬 파일 확인
echo "=== 로컬 인증서 파일 ==="
ls -lh certs/

echo ""
echo "=== 인증서 만료일 ==="
openssl x509 -in certs/mochachat.crt -noout -dates

echo ""
echo "=== 인증서 도메인 ==="
openssl x509 -in certs/mochachat.crt -noout -subject

echo ""
echo "=== Let's Encrypt 인증서 위치 ==="
sudo ls -lh /etc/letsencrypt/live/mochachat.app/

echo ""
echo "=== Certbot 자동 갱신 상태 ==="
sudo systemctl status certbot.timer --no-pager
