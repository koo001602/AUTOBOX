# AutoBox 데이터베이스 Docker 사용 가이드

## 목차
1. [Docker 설치](#1-docker-설치)
2. [환경변수 설정](#2-환경변수-설정)
3. [데이터베이스 실행](#3-데이터베이스-실행)
4. [데이터베이스 접속](#4-데이터베이스-접속)
5. [자주 사용하는 명령어](#5-자주-사용하는-명령어)
6. [문제 해결](#6-문제-해결)

---

## 1. Docker 설치

### Windows
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치
2. 설치 완료 후 Docker Desktop 실행
3. 시스템 트레이에서 Docker 아이콘이 "Running" 상태인지 확인

### Mac
```bash
# Homebrew로 설치
brew install --cask docker

# 또는 Docker Desktop 직접 다운로드
# https://www.docker.com/products/docker-desktop/
```

### Linux (Ubuntu/Debian)
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo apt-get install docker-compose-plugin

# 사용자를 docker 그룹에 추가 (sudo 없이 사용하기 위해)
sudo usermod -aG docker $USER

# 로그아웃 후 다시 로그인
```

---

## 2. 환경변수 설정

### .env 파일 생성

`backend` 폴더에 `.env` 파일을 생성하고 아래 내용을 입력하세요.

```bash
# backend/.env 파일 생성
cd backend
```

### .env 파일 내용

```env
# ================================
# AutoBox 환경변수 설정
# ================================

# MySQL Docker 컨테이너 설정
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=autobox

# 애플리케이션 DB 연결 정보
DB_HOST=localhost
DB_PORT=3306
DB_NAME=autobox
DB_USER=root
DB_PASSWORD=root

# 전체 DATABASE_URL (SQLAlchemy용)
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/autobox

# 비동기 DATABASE_URL (aiomysql용)
DATABASE_URL_ASYNC=mysql+aiomysql://root:root@localhost:3306/autobox

# 타임존
TZ=Asia/Seoul
```

### 환경변수 설명

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `MYSQL_ROOT_PASSWORD` | `root` | MySQL root 계정 비밀번호 |
| `MYSQL_DATABASE` | `autobox` | 생성할 데이터베이스 이름 |
| `DB_HOST` | `localhost` | 데이터베이스 호스트 |
| `DB_PORT` | `3306` | MySQL 포트 |
| `DB_NAME` | `autobox` | 데이터베이스 이름 |
| `DB_USER` | `root` | 접속 계정 |
| `DB_PASSWORD` | `root` | 접속 비밀번호 |
| `DATABASE_URL` | 위 참조 | SQLAlchemy 연결 문자열 |
| `TZ` | `Asia/Seoul` | 타임존 설정 |

### 주의사항

> ⚠️ `.env` 파일은 민감한 정보를 포함하므로 **절대 Git에 커밋하지 마세요!**

`.gitignore`에 아래 내용이 포함되어 있는지 확인하세요:

```gitignore
# 환경변수 파일
.env
.env.local
.env.*.local
```

---

## 3. 데이터베이스 실행

### 처음 시작하기

```bash
# backend 폴더로 이동
cd backend

# 컨테이너 시작 (백그라운드 실행)
docker-compose up -d

# 로그 확인 (초기화 진행 상황)
docker-compose logs -f mysql
```

### 실행 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 정상 실행 시 출력 예시:
# NAME            STATUS          PORTS
# autobox-mysql   Up (healthy)    0.0.0.0:3306->3306/tcp
```

---

## 4. 데이터베이스 접속

### 접속 정보

| 항목 | 값 |
|------|-----|
| Host | `localhost` |
| Port | `3306` |
| Database | `autobox` |
| User | `root` |
| Password | `root` |

### CLI로 접속

```bash
# Docker 컨테이너 내부 MySQL CLI 접속
docker exec -it autobox-mysql mysql -u root -proot autobox
```

### GUI 도구로 접속

**DBeaver, MySQL Workbench, DataGrip** 등에서:
- Host: `localhost`
- Port: `3306`
- Username: `root`
- Password: `root`
- Database: `autobox`

### 애플리케이션 연결 문자열

```python
# Python (SQLAlchemy)
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/autobox"

# Python (aiomysql - 비동기)
DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/autobox"
```

```javascript
// Node.js
const config = {
  host: 'localhost',
  port: 3306,
  user: 'root',
  password: 'root',
  database: 'autobox'
};
```

---

## 5. 자주 사용하는 명령어

### 컨테이너 관리

```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 컨테이너 재시작
docker-compose restart

# 로그 확인 (실시간)
docker-compose logs -f mysql

# 컨테이너 상태 확인
docker-compose ps
```

### 데이터 관리

```bash
# 데이터 백업
docker exec autobox-mysql mysqldump -u root -proot autobox > backup.sql

# 데이터 복원
docker exec -i autobox-mysql mysql -u root -proot autobox < backup.sql

# 데이터 완전 초기화 (주의: 모든 데이터 삭제됨!)
docker-compose down -v
docker-compose up -d
```

### 데이터베이스 직접 조작

```bash
# SQL 파일 실행
docker exec -i autobox-mysql mysql -u root -proot autobox < your_script.sql

# 특정 쿼리 실행
docker exec autobox-mysql mysql -u root -proot -e "SELECT * FROM logistics_item LIMIT 5;" autobox
```

---

## 6. 문제 해결

### 포트 충돌 (3306 포트가 이미 사용 중)

```bash
# 방법 1: 기존 MySQL 서비스 중지
# Windows: 서비스 관리자에서 MySQL 중지
# Mac/Linux: 
sudo systemctl stop mysql

# 방법 2: docker-compose.yml에서 포트 변경
# ports: "3307:3306" 으로 수정 후 재시작
```

### 컨테이너가 시작되지 않을 때

```bash
# 로그 확인
docker-compose logs mysql

# 컨테이너 완전 재생성
docker-compose down -v
docker-compose up -d
```

### 초기화 스크립트가 실행되지 않을 때

초기화 스크립트(`database.sql`)는 **최초 실행 시에만** 실행됩니다.
이미 데이터가 있는 상태에서 스키마를 변경하려면:

```bash
# 방법 1: 볼륨 삭제 후 재시작 (데이터 초기화)
docker-compose down -v
docker-compose up -d

# 방법 2: 수동으로 SQL 실행
docker exec -i autobox-mysql mysql -u root -proot autobox < database.sql
```

### Windows에서 줄바꿈 문제

Git에서 CRLF 설정 문제로 SQL 파일이 제대로 실행되지 않을 수 있습니다:

```bash
# .gitattributes 파일에 추가
*.sql text eol=lf
```

---

## 팀 협업 Tips

1. **동일한 환경 보장**: 모든 팀원이 같은 `docker-compose.yml`을 사용하면 동일한 DB 환경을 가질 수 있습니다.

2. **스키마 변경 시**: `database.sql`을 수정한 후 팀원들에게 알려주세요. 팀원들은 다음 명령으로 업데이트할 수 있습니다:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

3. **테스트 데이터**: 공유할 테스트 데이터가 있다면 `seed.sql` 파일을 만들어 `docker-entrypoint-initdb.d`에 추가하세요.

4. **비밀번호 관리**: 실제 운영 환경에서는 `.env` 파일을 사용하고, `.gitignore`에 추가하세요.
