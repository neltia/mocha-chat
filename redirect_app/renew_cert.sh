#!/bin/bash
echo "Let's Encrypt 인증서 갱신 중..."

# 서비스 중지 (Standalone 모드 사용 시)
docker-compose down

# 인증서 갱신
sudo certbot renew

# 새 인증서 복사
sudo cp /etc/letsencrypt/live/mochachat.app/fullchain.pem certs/mochachat.crt
sudo cp /etc/letsencrypt/live/mochachat.app/privkey.pem certs/mochachat.key
sudo chown $USER:$USER certs/mochachat.crt certs/mochachat.key
chmod 644 certs/mochachat.crt
chmod 600 certs/mochachat.key

# 서비스 재시작
docker-compose up -d

echo "인증서 갱신 및 재시작 완료"
