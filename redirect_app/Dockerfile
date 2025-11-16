FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app.py .
COPY gunicorn_conf.py .

# SSL 인증서 디렉토리 생성
RUN mkdir -p /etc/ssl/certs /etc/ssl/private && \
    chmod 755 /etc/ssl/certs && \
    chmod 755 /etc/ssl/private

# 포트 노출
EXPOSE 8000 443

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# 애플리케이션 시작
CMD ["gunicorn", "app:app", "--config", "gunicorn_conf.py"]
