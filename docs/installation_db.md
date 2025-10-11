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

## MariaDB
### Install
- mariadb install
```
sudo apt update
sudo apt install -y mariadb-server
```

- mariadb acount setting
```
# sudo mysql_secure_installation
Enter current password for root (enter for none): Enter
Enable Unix socket authentication? [Y/n] N
Change the root password? [Y/n] Y
Remove anonymous users? [Y/n] Y
Disallow root login remotely? [Y/n] n
Remove test database and access to it? [Y/n] Y
Reload privilege tables now? [Y/n] Y
```

### DB & User
- create db
```
# mariadb -u root -p
CREATE DATABASE <DB-NAME>;
```

- useradd & remote grant permit
```
# mariadb -u root -p
CREATE USER 'mochachat'@'%' IDENTIFIED BY '<PW>';
grant all privileges on *.* to 'root'@'%' identified by '<pw>';
FLUSH PRIVILEGES;
EXIT;
```

### Config
- bind conf
```
# vim /etc/mysql/mariadb.conf.d/50-server.cnf
bind 127.0.0.1 -> bind 0.0.0.0
```

(optional - secure) default mysql_native_password auth plugin -> auth_ed25519
- 플러그인 설치
```
INSTALL SONAME 'auth_ed25519';
```
- 플러그인 목록 확인
```
show plugins;
```
- 플러그인 적용된 사용자 추가/기존 사용자 변경
```
CREATE USER 'username'@'%' IDENTIFIED VIA ed25519 USING PASSWORD('pw');
```
```
ALTER USER 'username'@'%' IDENTIFIED VIA ed25519 USING PASSWORD('pw');
```

## Elasticsearch
### Elasticsearch install
- elasticsearch install
```
sudo -i
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
sudo apt-get install apt-transport-https
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update && sudo apt-get install elasticsearch
sudo service elasticsearch start
```

- elasticsearch password setting
```
/usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i
```

### Kibana
- kibana install
```
sudo apt-get update && sudo apt-get install kibana
```

- kibana token setting
```
/usr/share/kibana/bin/kibana-setup --enrollment-token $(/usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana)
```

- kibana host setting
```
# vim /etc/kibana/kibana.yml
server.host 주석 해제 및 "0.0.0.0"으로 수정
```

- kibana service start
```
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable kibana.service
sudo systemctl restart kibana.service
```

### nori analyzer plugin install
- nori : 한국어 형태소 분석기 플러그인
```
sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install analysis-nori
sudo service elasticsearch restart
```

- nori 적용 테스트를 위한 인덱스 삽입
```
PUT korean_analyzer1
{
  "settings": {
    "analysis": {
      "tokenizer": {
        "korean_nori_tokenizer": {
          "type": "nori_tokenizer",
          "decompound_mode": "mixed",
          "user_dictionary": "userdict_test.txt"
        }
      },
      "analyzer": {
        "nori_analyzer": {
          "type": "custom",
          "tokenizer": "korean_nori_tokenizer"
        }
      }
    }
  }
}
```
- nori analyzer 테스트
```
POST korean_analyzer1/_analyze
{
  "analyzer":"nori_analyzer",
  "text":"안녕하세요. 블로거입니다."
}
```

### jaso plugin install
- suggest API 사용을 위해서는 엘라스틱서치가 기본적으로 한국어를 지원하지 않기 때문에, 자소 단위(ㄱ, ㄴ, ㅏ, ㅑ)로 분해하는 플러그인도 필요하다.
```
# 관리자 권한에서 진행한다.
sudo -i

# zip, unzip 프로그램 설치
apt install zip unzip -y

# jaso analyzer 8.6.2 다운로드 (최신임)
wget https://github.com/netcrazy/elasticsearch-jaso-analyzer/releases/download/v8.6.2/jaso-analyzer-plugin-8.6.2-plugin.zip

# apt list elasticsearch 명령으로 버전을 확인하여 elasticsearch 버전을 변경
apt list elasticsearch # 8.10.4
unzip jaso-analyzer-plugin-8.6.2-plugin.zip -d jaso-analyzer-plugin-8.10.4
vim jaso-analyzer-plugin-8.10.4/plugin-descriptor.properties
```
