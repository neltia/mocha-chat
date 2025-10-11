# mocha-chat
"모카챗"은 커피챗처럼 즐길 수 있는 개발자용 웹 서비스입니다.

<p align="center">
<img src="docs/logo_mochachat.png" alt="logo_mochachat" width="220" height="200"/>
</p>

- '모아보는 대화': MochaChat은 '수많은 기술 블로그의 정보를 한곳에 모아 사용자와 대화하는 서비스'라는 메시지를 내세웁니다.
- '커피챗': 개발자 커뮤니티에서 자주 쓰이는 '커피챗(Coffee Chat)' 개념을 활용합니다. "MochaChat에서 편하게 커피챗하며 최신 기술과 지식을 얻어가세요"라는 슬로건을 사용해, 가볍고 친근하게 정보를 얻을 수 있는 플랫폼이라는 이미지를 강조합니다.
- 로고의 돋보기는 정보를 찾고, 커피잔은 모으는 행위를, 그리고 채팅 버블은 이 모든 것을 사용자에게 '대화하듯 전달'한다는 의미입니다.

## Project Arch
```
mochachat/
├── app/                  # NextJS 애플리케이션 (FSD Lite)
│   ├── src/
│   │   ├── app/               # NextJS App Router
│   │   ├── shared/            # 공통 모듈
│   │   ├── entities/          # 도메인 엔티티
│   │   ├── features/          # 기능 단위
│   │   ├── widgets/           # UI 위젯
│   │   └── components/        # UI 컴포넌트
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── Dockerfile.prod
├── backend/                   # FastAPI 애플리케이션 (Layered)
│   ├── app/
│   │   ├── api/               # API 라우터
│   │   ├── core/              # 설정, 보안, 응답
│   │   ├── crud/              # CRUD 로직
│   │   ├── db/                # 데이터베이스 연결
│   │   ├── models/            # SQLAlchemy 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   ├── services/          # 비즈니스 로직
│   │   ├── utils/             # 유틸리티
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml         # 개발환경
├── docker-compose.prod.yml    # 프로덕션환경
├── deploy.sh                  # 배포 스크립트
└── .env                       # 환경 변수
```
