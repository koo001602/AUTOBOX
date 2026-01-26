# AutoBox 라즈베리파이 설정 가이드

라즈베리파이를 Edge 디바이스로 설정하여 오린 나노와 EC2 간의 브릿지 역할을 수행합니다.

## 아키텍처

```
┌──────────────┐      로컬 MQTT       ┌──────────────────────────────┐
│  오린 나노   │ ◀──────────────────▶ │        라즈베리파이          │
│ (자율주행차) │     localhost:1883   │                              │
└──────────────┘                      │  ┌────────────────────────┐  │
                                      │  │ 로컬 Mosquitto 브로커  │  │
                                      │  │      (Port 1883)       │  │
                                      │  └───────────┬────────────┘  │
                                      │              │               │
                                      │              ▼               │
                                      │  ┌────────────────────────┐  │
                                      │  │     Bridge Module      │  │
                                      │  │  (EC2로 메시지 전달)   │  │
                                      │  └───────────┬────────────┘  │
                                      └──────────────┼───────────────┘
                                                     │
                                        TLS 8883 (Outbound)
                                                     │
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │     EC2 MQTT Broker          │
                                      │    43.201.254.235:8883       │
                                      └──────────────────────────────┘
```

## 설치

### 1. Mosquitto 설치

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients python3-pip

# 서비스 시작
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

### 2. 인증서 복사

EC2에서 생성된 인증서를 라즈베리파이로 복사합니다:

```bash
# EC2에서 라즈베리파이로 복사 (EC2에서 실행)
scp mqtt/certs/ca.crt pi@<RPI_IP>:/home/pi/autobox/certs/
scp mqtt/certs/client.crt pi@<RPI_IP>:/home/pi/autobox/certs/
scp mqtt/certs/client.key pi@<RPI_IP>:/home/pi/autobox/certs/

# 라즈베리파이에서 권한 설정
chmod 644 /home/pi/autobox/certs/ca.crt
chmod 644 /home/pi/autobox/certs/client.crt
chmod 600 /home/pi/autobox/certs/client.key
```

### 3. Mosquitto 브릿지 설정

```bash
# 설정 파일 복사
sudo cp mosquitto-bridge.conf /etc/mosquitto/conf.d/bridge.conf

# EC2 IP 수정
sudo nano /etc/mosquitto/conf.d/bridge.conf
# EC2_IP를 실제 IP로 변경

# Mosquitto 재시작
sudo systemctl restart mosquitto
```

### 4. Python 클라이언트 설정

```bash
# 의존성 설치
pip3 install paho-mqtt

# 환경변수 설정
cp .env.example .env
nano .env
# EC2_IP, USERNAME, PASSWORD 설정
```

## 파일 설명

| 파일 | 설명 |
|------|------|
| `mosquitto-bridge.conf` | Mosquitto 브릿지 설정 |
| `mqtt_client.py` | Python MQTT 클라이언트 예시 |
| `mqtt_publisher.py` | 센서 데이터 발행 예시 |
| `.env.example` | 환경변수 템플릿 |

## 사용법

### 브릿지 모드 (권장)

Mosquitto 브릿지를 사용하면 자동으로 메시지가 EC2로 전달됩니다.

```bash
# 로컬에서 메시지 발행 → 자동으로 EC2로 전달
mosquitto_pub -h localhost -t "autobox/sensor/data" -m '{"temp": 25.5}'
```

### Python 클라이언트 모드

직접 Python 코드로 EC2에 연결할 수도 있습니다.

```bash
python3 mqtt_publisher.py
```

## 테스트

### 로컬 브로커 테스트

```bash
# 터미널 1: 구독
mosquitto_sub -h localhost -t "autobox/#" -v

# 터미널 2: 발행
mosquitto_pub -h localhost -t "autobox/test" -m "Hello Local"
```

### EC2 연결 테스트

```bash
# EC2 브로커에 직접 연결 테스트
mosquitto_sub -h EC2_IP -p 8883 \
  --cafile /home/pi/autobox/certs/ca.crt \
  -u raspberry-pi -P your_password \
  -t "autobox/#" -v
```

### 브릿지 동작 확인

```bash
# 라즈베리파이에서 로컬 발행
mosquitto_pub -h localhost -t "autobox/sensor/data" -m '{"test": true}'

# EC2에서 수신 확인
docker exec -it autobox-mqtt mosquitto_sub -h localhost -t "autobox/#" -v
```

## 문제 해결

### 브릿지 연결 실패

```bash
# Mosquitto 로그 확인
sudo journalctl -u mosquitto -f

# 일반적인 원인:
# 1. EC2 보안그룹에서 8883 포트 미개방
# 2. 인증서 경로 또는 권한 문제
# 3. Username/Password 불일치
```

### 인증서 오류

```bash
# 인증서 확인
openssl x509 -in /home/pi/autobox/certs/ca.crt -text -noout

# 서버 연결 테스트
openssl s_client -connect EC2_IP:8883 -CAfile /home/pi/autobox/certs/ca.crt
```

## Topic 구조

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
├── camera/
│   └── detection     # 카메라 감지 이벤트
└── command/          # EC2 → 라즈베리파이 명령 (수신)
```
