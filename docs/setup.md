# Installation
- Nginx, MariaDB, Elasticsearch는 시스템에 설치하고, systemd 데몬으로 구동
- 프론트 NextJS와 백엔드 FastAPI는 docker compose로 배포
- Nginx를 사용해 리버스 프록시 수행

## Architecture
- system architecture
```
[사용자 요청]
    ↓ HTTPS (yourdomain.com)
[nginx systemd] (리버스 프록시, SSL, 캐싱)
    ├─ /api/* → http://127.0.0.1:8000 (FastAPI)
    └─ /* → http://127.0.0.1:3000 (NextJS)
         ↓ (host.docker.internal)
[Docker Network]
├── mochachat_backend (FastAPI 컨테이너)
└── mochachat_frontend (NextJS 컨테이너)
    ↓ 데이터베이스 접근
[Host System Services]
├── MariaDB (systemd) → User 관리, 인증
└── Elasticsearch (systemd) → Blog 검색, RAG
```

## DB
- installation-db.md 참조

## WEB APP
- web app & was api clone
```
git clone ~
```

- docker install
```
sudo apt update
sudo apt install docker.io
```

- docker compose plugin install
```
sudo apt-get install ca-certificates curl gnupg lsb-release
```

## Nginx
- nginx conf
```
server {
        #listen 80 default_server;
        #listen [::]:80 default_server;

        # SSL configuration
        #
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name <domain>;
        server_tokens off;

        # ssl_certificate         /etc/nginx/ssl/selfsigned.crt;
        # ssl_certificate_key     /etc/nginx/ssl/selfsigned.key;

        # --- TLS certs ---
        ssl_certificate           /etc/nginx/ssl/cert.pem;
        ssl_certificate_key       /etc/nginx/ssl/key.pem;

        # --- TLS baseline hardening ---
        ssl_protocols TLSv1.2 TLSv1.3;
        # SSLCipherSuite 등가(대표 안전값, TLS1.2만 지정; TLS1.3은 엔진 고정)
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
        ssl_prefer_server_ciphers off;

        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:10m;
        ssl_session_tickets off;

        # --- OCSP Stapling (권장) ---
        ssl_stapling on;
        ssl_stapling_verify on;
        resolver 1.1.1.1 8.8.8.8 valid=300s;
        resolver_timeout 5s;

        client_max_body_size 800M;

        error_page 400 401 403 404 405 408 413 414 429 500 502 503 504 /errors/default.html;

        location = /errors/default.html {
                root /var/www;
                internal;
                default_type text/html;
                add_header Cache-Control "no-store";
        }

        location /api {
                proxy_pass http://localhost:8000;

                proxy_set_header    X-Real-IP $remote_addr;
                proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header    X-Forwarded-Proto $scheme;
        }

        location / {
                proxy_pass http://localhost:3000;

                proxy_set_header    X-Real-IP $remote_addr;
                proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header    X-Forwarded-Proto $scheme;
        }
}


# HTTP -> HTTPS 리다이렉트
server {
    listen 80;
    listen [::]:80;
    server_name <domain>;
    server_tokens off;
    return 301 https://$host$request_uri;
}
```
