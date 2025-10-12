FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv


# Python 환경 설정
ENV UV_SYSTEM_PYTHON=1
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app

# 애플리케이션이 사용할 내부 경로 기본값 (compose에서 override 예정)
ENV STORAGE_DIR=/mnt/storage
ENV RESULT_DIR=/mnt/result

# 의존성 파일 복사 및 설치 (레이어 캐싱 활용)
COPY pyproject.toml uv.lock* /app/
RUN uv sync --frozen --no-dev

# 애플리케이션 코드 복사
COPY . /app/

# 컨테이너 실행 시 실행할 명령
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
