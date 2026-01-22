# AutoBox 통신 아키텍처

## 개요

AutoBox 시스템은 라즈베리파이(Edge Device)와 EC2 서버(Cloud Backend) 간의 양방향 통신을 지원합니다.

## 시스템 구성도

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           데이터아키텍처                                   │
└────────────────────────────────────────────────────────────────────────────┘

                    MQTT (Publish)                 REST API
┌──────────────┐  ──────────────────▶  ┌──────────────────────────────────┐
│              │                       │           EC2 Server             │
│ 라즈베리파이 │                       │  ┌────────────┐  ┌────────────┐  │
│              │                       │  │  Backend   │  │  Frontend  │  │
│ ┌──────────┐ │                       │  │  (FastAPI) │  │  (Vue.js)  │  │
│ │  MQTT    │ │                       │  │  :8000     │  │  :80       │  │
│ │  Broker  │ │  ◀──────────────────  │  └────────────┘  └────────────┘  │
│ │  :1883   │ │      REST API         │                                  │
│ └──────────┘ │                       │         │                        │
│              │                       │         ▼                        │
│ ┌──────────┐ │                       │  ┌────────────────────────────┐  │
│ │   REST   │ │                       │  │      Azure MySQL           │  │
│ │  Server  │ │                       │  │  (External Database)       │  │
│ │  :5000   │ │                       │  └────────────────────────────┘  │
│ └──────────┘ │                       │                                  │
└──────────────┘                       └──────────────────────────────────┘
```

## 통신 방식

### 1. 라즈베리파이 → EC2 (MQTT)

| 항목 | 설명 |
|------|------|
| **프로토콜** | MQTT |
| **방향** | 라즈베리파이 → EC2 Backend |
| **용도** | 센서 데이터, 상태 정보, 이벤트 전송 |
| **Broker 위치** | 라즈베리파이 |
| **포트** | 1883 (기본) / 8883 (SSL) |

**사용 예시:**
- 센서 데이터 실시간 전송
- 디바이스 상태 업데이트
- 알림/이벤트 발생 시 즉시 전달

### 2. EC2 → 라즈베리파이 (REST API)

| 항목 | 설명 |
|------|------|
| **프로토콜** | HTTP REST API |
| **방향** | EC2 Backend → 라즈베리파이 |
| **용도** | 명령 전달, 설정 변경, 제어 요청 |
| **포트** | 5000 (예시) |

**사용 예시:**
- 디바이스 설정 변경 명령
- 특정 동작 실행 요청
- 상태 조회 요청

---

## 설치 및 설정

### 라즈베리파이 설치 항목

#### 1. MQTT Broker (Mosquitto)

```bash
# Mosquitto 설치
sudo apt update
sudo apt install -y mosquitto mosquitto-clients

# 서비스 시작 및 자동 시작 설정
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# 외부 접속 허용 설정
sudo nano /etc/mosquitto/mosquitto.conf
```

`/etc/mosquitto/mosquitto.conf` 설정:
```conf
listener 1883
allow_anonymous true

# 인증 사용 시 (권장)
# allow_anonymous false
# password_file /etc/mosquitto/passwd
```

```bash
# 설정 적용
sudo systemctl restart mosquitto
```

#### 2. MQTT Client (Python)

```bash
pip install paho-mqtt
```

**Publisher 예시 코드:**
```python
import paho.mqtt.client as mqtt
import json
import time

# Broker 설정 (localhost - 같은 라즈베리파이)
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "autobox/sensor/data"

client = mqtt.Client()
client.connect(BROKER_HOST, BROKER_PORT, 60)

# 센서 데이터 발행
data = {
    "device_id": "rpi-001",
    "temperature": 25.5,
    "humidity": 60,
    "timestamp": time.time()
}
client.publish(TOPIC, json.dumps(data))
client.disconnect()
```

#### 3. REST API Server (Flask)

```bash
pip install flask
```

**REST Server 예시 코드:**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/command', methods=['POST'])
def receive_command():
    """EC2로부터 명령 수신"""
    data = request.json
    command = data.get('command')
    
    # 명령 처리 로직
    result = process_command(command)
    
    return jsonify({"status": "success", "result": result})

@app.route('/api/status', methods=['GET'])
def get_status():
    """디바이스 상태 반환"""
    return jsonify({
        "device_id": "rpi-001",
        "status": "online",
        "uptime": get_uptime()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

### EC2 Backend 설치 항목

#### 1. MQTT Client (Python)

`requirements.txt`에 추가:
```
paho-mqtt==1.6.1
# 또는 비동기 버전
aiomqtt==1.2.1
```

**Subscriber 예시 코드:**
```python
import paho.mqtt.client as mqtt
import json

# 라즈베리파이 Broker 설정
BROKER_HOST = "라즈베리파이_IP"  # 예: 192.168.0.100
BROKER_PORT = 1883
TOPIC = "autobox/sensor/#"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"Received: {data}")
    # 데이터 처리 로직 (DB 저장 등)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_forever()
```

#### 2. REST Client (httpx)

**라즈베리파이에 명령 전송 예시:**
```python
import httpx

RASPBERRY_PI_URL = "http://라즈베리파이_IP:5000"

async def send_command(command: str):
    """라즈베리파이에 명령 전송"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RASPBERRY_PI_URL}/api/command",
            json={"command": command}
        )
        return response.json()

async def get_device_status():
    """라즈베리파이 상태 조회"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{RASPBERRY_PI_URL}/api/status")
        return response.json()
```

---

## 네트워크 설정

### 필수 포트

| 서비스 | 포트 | 프로토콜 | 방향 |
|--------|------|----------|------|
| MQTT Broker | 1883 | TCP | EC2 → 라즈베리파이 |
| 라즈베리파이 REST API | 5000 | TCP | EC2 → 라즈베리파이 |
| EC2 Backend | 8000 | TCP | 외부 → EC2 |
| EC2 Frontend | 80 | TCP | 외부 → EC2 |

### 라즈베리파이 네트워크 요구사항

EC2에서 라즈베리파이에 접근해야 하므로 다음 중 하나가 필요합니다:

| 환경 | 설정 방법 |
|------|-----------|
| **공인 IP** | 직접 연결 가능 |
| **공유기/NAT** | 포트 포워딩 설정 (1883, 5000 포트) |
| **DDNS** | 동적 IP 환경에서 도메인으로 접근 |

### 포트 포워딩 설정 예시 (공유기)

```
외부 포트 1883 → 내부 IP(라즈베리파이):1883
외부 포트 5000 → 내부 IP(라즈베리파이):5000
```

### EC2 보안 그룹 설정

EC2 인바운드 규칙:

| 포트 | 프로토콜 | 소스 | 용도 |
|------|----------|------|------|
| 80 | TCP | 0.0.0.0/0 | Frontend |
| 8000 | TCP | 0.0.0.0/0 | Backend API |

---

## MQTT Topic 구조 (권장)

```
autobox/
├── sensor/
│   ├── data          # 센서 데이터
│   └── status        # 센서 상태
├── device/
│   ├── status        # 디바이스 상태
│   └── heartbeat     # 연결 유지 신호
├── alert/
│   └── notification  # 알림 이벤트
└── camera/
    └── detection     # 카메라 감지 이벤트
```

---

## 연결 테스트

### 1. MQTT 연결 테스트

**라즈베리파이에서 (Broker 테스트):**
```bash
# Subscriber 실행
mosquitto_sub -h localhost -t "test/topic"

# 다른 터미널에서 Publisher 실행
mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT"
```

**EC2에서 (라즈베리파이 Broker 연결 테스트):**
```bash
# mosquitto-clients 설치
sudo apt install mosquitto-clients

# 라즈베리파이 Broker에 연결
mosquitto_sub -h 라즈베리파이_IP -t "test/topic"
```

### 2. REST API 연결 테스트

**EC2에서 라즈베리파이 REST API 테스트:**
```bash
curl http://라즈베리파이_IP:5000/api/status
```

---

## 환경 변수

### EC2 Backend (.env)

```env
# MQTT 설정
MQTT_BROKER_HOST=라즈베리파이_IP
MQTT_BROKER_PORT=1883
MQTT_TOPIC_PREFIX=autobox

# 라즈베리파이 REST API
RASPBERRY_PI_URL=http://라즈베리파이_IP:5000
```

### 라즈베리파이

```env
# MQTT Broker
MQTT_BROKER_PORT=1883

# REST API Server
REST_API_PORT=5000

# EC2 Backend (필요시)
EC2_BACKEND_URL=http://43.201.254.235:8000
```

---

## 참고 자료

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [Paho MQTT Python](https://pypi.org/project/paho-mqtt/)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
