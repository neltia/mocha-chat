#!/bin/bash

DOMAIN="domain"      # 실제 도메인으로 변경 필요
EMAIL="changeme@naver.com"  # 실제 이메일로 변경 필요

echo "Let's Encrypt 인증서 설정 시작..."

# Certbot 설치 확인
if ! command -v certbot &> /dev/null; then
    echo "Certbot 설치 중..."
    sudo apt-get update
    sudo apt-get install -y certbot
fi

# 기존 서비스 중지 (80, 443 포트 비우기)
echo "기존 서비스 중지..."
docker-compose down 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

# Certbot Standalone 모드로 인증서 발급
echo "인증서 발급 중..."
sudo certbot certonly --standalone \
  -d $DOMAIN \
  --non-interactive \
  --agree-tos \
  --email $EMAIL \
  --preferred-challenges http

# 인증서가 성공적으로 발급되었는지 확인
if [ $? -eq 0 ]; then
    echo "인증서 발급 완료"

    # certs 디렉토리 생성
    mkdir -p certs

    # 인증서 복사 (Docker에서 사용하기 위해)
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem certs/mochachat.crt
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem certs/mochachat.key

    # 권한 설정
    sudo chown $USER:$USER certs/mochachat.crt certs/mochachat.key
    chmod 644 certs/mochachat.crt
    chmod 600 certs/mochachat.key

    echo "인증서가 ./certs/ 로 복사되었습니다"
    ls -lh certs/

    # 자동 갱신 설정
    echo "자동 갱신 설정 중..."

    # 갱신 후크 스크립트 생성
    sudo tee /etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh > /dev/null <<EOF
#!/bin/bash
# 인증서 갱신 후 Docker용 인증서 복사
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /home/$USER/redire_app/certs/mochachat.crt
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /home/$USER/redire_app/certs/mochachat.key
chown $USER:$USER /home/$USER/redire_app/certs/*
cd /home/$USER/redire_app && docker-compose restart https
EOF

    sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/copy-to-docker.sh

    # Certbot 자동 갱신 타이머 확인
    sudo systemctl enable certbot.timer
    sudo systemctl start certbot.timer

    echo "auto renewal setup complete (checks twice daily)"

else
    echo "cert issue failed"
    echo ""
    echo "문제 해결:"
    echo "1. 도메인이 이 서버를 가리키는지 확인: dig $DOMAIN"
    echo "2. 80 포트가 열려있는지 확인: sudo netstat -tlnp | grep :80"
    echo "3. 방화벽 설정 확인: sudo ufw status"
    exit 1
fi

echo ""
echo "success:"
echo "   docker-compose up -d"
