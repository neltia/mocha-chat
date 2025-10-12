# API DOCS

## 공통 응답 규격
- 성공 응답 (단일)
```
{
  "status": "success",
  "result_code": 200,
  "result_msg": "요청이 처리되었습니다",
  "data": {
    "field": "value"
  }
}
```

- 성공 응답 리스트
```
{
  "status": "success",
  "result_code": 200,
  "result_msg": "검색 완료",
  "data": {
    "total": 50,
    "count": 10,
    "results": [...]
  }
}
```

- 에러 응답
```
{
  "status": "error",
  "result_code": 400,
  "result_msg": "잘못된 요청입니다"
}
```

## API 구조 참고
```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                    # 공통 의존성 (DB 세션, 인증 등)
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py            # JWT 인증 엔드포인트
│   │       │   ├── user.py            # User API (MariaDB)
│   │       │   └── blog.py            # Blog API (Elasticsearch)
│   │       ├── __init__.py
│   │       └── router.py              # API 라우터 통합
│   ├── core/
│   │   ├── api_logging_config.py      # API 로깅 설정
│   │   ├── api_logging_middleware.py  # 로깅 미들웨어
│   │   ├── config.py                  # 환경 설정
│   │   ├── logging.py                 # 로깅 설정
│   │   ├── security.py                # JWT 보안
│   │   └── response.py                # 공통 응답 래퍼
│   ├── crud/
│   │   ├── base.py                    # 기본 CRUD 클래스
│   │   ├── __init__.py
│   │   ├── user.py                    # User CRUD (MariaDB)
│   │   └── blog.py                    # Blog CRUD (Elasticsearch)
│   ├── db/
│   │   ├── base.py                    # 데이터베이스 베이스
│   │   ├── session.py                 # MariaDB 세션 관리
│   │   └── elasticsearch.py           # Elasticsearch 클라이언트
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py                    # User SQLAlchemy 모델
│   ├── schemas/
│   │   ├── common.py                  # 공통 응답 스키마
│   │   ├── __init__.py
│   │   ├── user.py                    # User Pydantic 스키마
│   │   ├── blog.py                    # Blog Pydantic 스키마
│   │   └── auth.py                    # Auth Pydantic 스키마
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user.py                    # User 비즈니스 로직 (함수형)
│   │   └── blog.py                    # Blog 비즈니스 로직 (함수형)
│   ├── utils/
│   │   ├── db_check.py                # DB 연결 상태 확인
│   │   ├── error_handler.py           # 글로벌 에러 핸들러
│   │   ├── global_route.py            # 전역 라우트 설정
│   │   ├── header_timing.py           # API 응답 시간 헤더
│   │   ├── __init__.py
│   │   └── state_for_log.py           # 로깅 상태 관리
│   ├── __init__.py
│   └── main.py                        # FastAPI 앱 진입점
├── requirements.txt
├── Dockerfile
├── Dockerfile.prod
├── pyproject.toml
├── main.py                            # 실행 진입점
└── run.py                             # 개발 실행 스크립트
```
