# AutoBox 백엔드 Docker 사용 가이드

## 목차
1. [Docker 설치](#1-docker-설치)
2. [빠른 시작](#2-빠른-시작)
3. [환경변수 설정](#3-환경변수-설정)
4. [서비스 실행](#4-서비스-실행)
5. [API 접속](#5-api-접속)
6. [자주 사용하는 명령어](#6-자주-사용하는-명령어)
7. [로컬 개발 환경 (uv)](#7-로컬-개발-환경-uv)
8. [문제 해결](#8-문제-해결)

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

### Linux (Ubuntu/Debian) / WSL2
```bash
# Docker 설치
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Docker GPG 키 추가
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Docker 저장소 추가
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker 서비스 시작
sudo service docker start

# 사용자를 docker 그룹에 추가 (sudo 없이 사용)
sudo usermod -aG docker $USER

# 그룹 권한 적용 (터미널 재시작 또는)
newgrp docker
```

---

## 2. 빠른 시작

### 한 줄 명령으로 전체 실행

```bash
cd backend && docker compose up -d --build
```

이 명령으로 **MySQL 데이터베이스**와 **FastAPI 백엔드 서버**가 동시에 실행됩니다.

### 실행 확인

```bash
# 컨테이너 상태 확인
docker compose ps

# 정상 실행 시 출력 예시:
# NAME              STATUS          PORTS
# autobox-mysql     Up (healthy)    0.0.0.0:3306->3306/tcp
# autobox-backend   Up (healthy)    0.0.0.0:8000->8000/tcp
```

### API 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 응답: {"success":true,"data":{"status":"healthy"}}
```

---

## 3. 환경변수 설정

### .env 파일 생성

`backend` 폴더에 `.env` 파일을 생성하세요 (선택사항 - 기본값 사용 가능).

```bash
cd backend
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/autobox

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF
```

### 환경변수 설명

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `DATABASE_URL` | `mysql+pymysql://root:root@localhost:3306/autobox` | 데이터베이스 연결 문자열 |
| `HOST` | `0.0.0.0` | 서버 바인딩 호스트 |
| `PORT` | `8000` | 서버 포트 |
| `DEBUG` | `true` | 디버그 모드 |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | 허용할 CORS 오리진 |

> ⚠️ `.env` 파일은 민감한 정보를 포함하므로 **Git에 커밋하지 마세요!**

---

## 4. 서비스 실행

### 전체 스택 실행 (권장)

```bash
cd backend

# 빌드 및 실행
docker compose up -d --build

# 로그 확인
docker compose logs -f
```

### 개별 서비스 실행

```bash
# MySQL만 실행
docker compose up -d mysql

# 백엔드만 실행 (MySQL이 실행 중이어야 함)
docker compose up -d backend
```

### 서비스 구성

| 서비스 | 컨테이너명 | 포트 | 설명 |
|--------|-----------|------|------|
| mysql | autobox-mysql | 3306 | MySQL 8.0 데이터베이스 |
| backend | autobox-backend | 8000 | FastAPI 백엔드 서버 |

---

## 5. API 접속

### 접속 정보

| 항목 | URL |
|------|-----|
| API Base URL | `http://localhost:8000/api/v1` |
| Swagger 문서 | `http://localhost:8000/docs` |
| ReDoc 문서 | `http://localhost:8000/redoc` |
| WebSocket | `ws://localhost:8000/ws/dashboard` |
| Health Check | `http://localhost:8000/health` |

### 주요 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/waybills/scan` | 운송장 스캔 시작 |
| PUT | `/api/v1/waybills/{id}/recognition` | OCR 인식 결과 저장 |
| PUT | `/api/v1/waybills/{id}/start-sorting` | 분류 시작 |
| PUT | `/api/v1/waybills/{id}/complete` | 분류 완료 |
| GET | `/api/v1/waybills` | 운송장 목록 조회 |
| GET | `/api/v1/waybills/{id}` | 운송장 상세 조회 |
| GET | `/api/v1/regions` | 구역 목록 조회 |
| GET | `/api/v1/system/status` | 시스템 상태 조회 |
| GET | `/api/v1/stats/regions` | 구역별 통계 |
| GET | `/api/v1/stats/export` | 엑셀 다운로드 |

### API 테스트 예시

```bash
# 운송장 스캔 시작
curl -X POST http://localhost:8000/api/v1/waybills/scan \
  -H "Content-Type: application/json" \
  -d '{"camera_id": "cam-capture"}'

# 운송장 목록 조회
curl http://localhost:8000/api/v1/waybills

# 시스템 상태 조회
curl http://localhost:8000/api/v1/system/status
```

### 데이터베이스 접속

| 항목 | 값 |
|------|-----|
| Host | `localhost` |
| Port | `3306` |
| Database | `autobox` |
| User | `root` |
| Password | `root` |

```bash
# CLI로 접속
docker exec -it autobox-mysql mysql -u root -proot autobox
```

---

## 6. 자주 사용하는 명령어

### 컨테이너 관리

```bash
# 전체 시작
docker compose up -d

# 전체 시작 (재빌드 포함)
docker compose up -d --build

# 전체 중지
docker compose down

# 전체 재시작
docker compose restart

# 특정 서비스만 재시작
docker compose restart backend
```

### 로그 확인

```bash
# 전체 로그
docker compose logs -f

# 백엔드 로그만
docker compose logs -f backend

# MySQL 로그만
docker compose logs -f mysql

# 최근 100줄만
docker compose logs --tail=100 backend
```

### 컨테이너 접속

```bash
# 백엔드 컨테이너 쉘 접속
docker exec -it autobox-backend /bin/bash

# MySQL 컨테이너 접속
docker exec -it autobox-mysql mysql -u root -proot autobox
```

### 데이터 관리

```bash
# 데이터 백업
docker exec autobox-mysql mysqldump -u root -proot autobox > backup.sql

# 데이터 복원
docker exec -i autobox-mysql mysql -u root -proot autobox < backup.sql

# 데이터 완전 초기화 (주의: 모든 데이터 삭제!)
docker compose down -v
docker compose up -d --build
```

### 이미지 관리

```bash
# 이미지 재빌드 (캐시 사용)
docker compose build

# 이미지 재빌드 (캐시 없이)
docker compose build --no-cache

# 사용하지 않는 이미지 정리
docker image prune -f
```

---

## 7. 로컬 개발 환경 (uv)

Docker 대신 로컬에서 직접 개발하려면 **uv**를 사용할 수 있습니다.

### uv 설치

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 쉘 설정 적용
source ~/.bashrc  # 또는 ~/.zshrc
```

### 개발 환경 설정

```bash
cd backend

# MySQL만 Docker로 실행
docker compose up -d mysql

# 가상환경 생성 및 의존성 설치
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 개발 서버 실행 (핫 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### pyproject.toml 사용 (대안)

```bash
cd backend

# uv sync로 의존성 설치
uv sync

# 서버 실행
uv run uvicorn app.main:app --reload
```

---

## 8. 문제 해결

### 포트 충돌

```bash
# 3306 포트 사용 중인 프로세스 확인
sudo lsof -i :3306

# 8000 포트 사용 중인 프로세스 확인
sudo lsof -i :8000

# 해결방법 1: 기존 프로세스 종료
sudo kill -9 <PID>

# 해결방법 2: docker-compose.yml에서 포트 변경
# ports: "3307:3306" 또는 "8001:8000"
```

### 백엔드가 MySQL에 연결되지 않을 때

```bash
# MySQL이 healthy 상태인지 확인
docker compose ps

# MySQL 로그 확인
docker compose logs mysql

# 백엔드 로그에서 에러 확인
docker compose logs backend

# 네트워크 확인
docker network ls
docker network inspect autobox-network
```

### 컨테이너가 시작되지 않을 때

```bash
# 상세 로그 확인
docker compose logs

# 컨테이너 완전 재생성
docker compose down -v
docker compose up -d --build

# 이미지 재빌드
docker compose build --no-cache
docker compose up -d
```

### 초기화 스크립트가 실행되지 않을 때

`database.sql`은 **최초 실행 시에만** 실행됩니다.

```bash
# 볼륨 삭제 후 재시작 (데이터 초기화)
docker compose down -v
docker compose up -d

# 또는 수동으로 SQL 실행
docker exec -i autobox-mysql mysql -u root -proot autobox < database.sql
```

### Docker 빌드 오류

```bash
# Docker 캐시 정리
docker builder prune -f

# 모든 정리 후 재시작
docker compose down -v
docker system prune -f
docker compose up -d --build
```

### WSL2에서 Docker가 안 될 때

```bash
# Docker 서비스 시작
sudo service docker start

# Docker 소켓 권한 확인
sudo chmod 666 /var/run/docker.sock
```

---

## 팀 협업 Tips

1. **동일한 환경 보장**: 모든 팀원이 같은 `docker-compose.yml`을 사용하면 동일한 개발 환경을 가질 수 있습니다.

2. **스키마 변경 시**: `database.sql`을 수정한 후 팀원들에게 알려주세요:
   ```bash
   docker compose down -v
   docker compose up -d --build
   ```

3. **백엔드 코드 변경 시**: 
   - Docker: `docker compose up -d --build`
   - 로컬 개발: 자동 리로드 (`--reload` 옵션)

4. **API 문서 공유**: http://localhost:8000/docs 에서 Swagger UI로 API를 테스트하고 공유하세요.

5. **환경변수 관리**: `.env.example` 파일을 Git에 커밋하고, 실제 `.env`는 `.gitignore`에 추가하세요.
