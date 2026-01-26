#!/usr/bin/env python3
"""
AutoBox MQTT Client for Raspberry Pi

라즈베리파이에서 EC2 MQTT 브로커에 직접 연결하는 클라이언트 예시입니다.
브릿지 모드 대신 Python으로 직접 연결할 때 사용합니다.

Usage:
    python3 mqtt_client.py
"""

import json
import os
import ssl
import time
from datetime import datetime
from typing import Callable, Optional

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 설정
EC2_BROKER_HOST = os.getenv("EC2_BROKER_HOST", "43.201.254.235")
EC2_BROKER_PORT = int(os.getenv("EC2_BROKER_PORT", "8883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "raspberry-pi")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
CA_CERT_PATH = os.getenv("CA_CERT_PATH", "/home/pi/autobox/certs/ca.crt")
CLIENT_CERT_PATH = os.getenv("CLIENT_CERT_PATH", "")
CLIENT_KEY_PATH = os.getenv("CLIENT_KEY_PATH", "")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "autobox")
CLIENT_ID = os.getenv("CLIENT_ID", "raspberry-pi-client")


class AutoBoxMQTTClient:
    """AutoBox MQTT 클라이언트 클래스"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self._message_handlers: dict[str, list[Callable]] = {}
    
    def connect(self) -> bool:
        """EC2 MQTT 브로커에 연결"""
        try:
            # MQTT 클라이언트 생성
            self.client = mqtt.Client(
                client_id=CLIENT_ID,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )
            
            # 콜백 설정
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # 인증 설정
            if MQTT_USERNAME and MQTT_PASSWORD:
                self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
            # TLS 설정
            self._configure_tls()
            
            # 연결
            print(f"Connecting to {EC2_BROKER_HOST}:{EC2_BROKER_PORT}...")
            self.client.connect(EC2_BROKER_HOST, EC2_BROKER_PORT, keepalive=60)
            
            # 백그라운드 루프 시작
            self.client.loop_start()
            
            # 연결 대기
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            return self.connected
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def _configure_tls(self):
        """TLS 설정"""
        ssl_context = ssl.create_default_context()
        
        # CA 인증서 로드
        if CA_CERT_PATH and os.path.exists(CA_CERT_PATH):
            ssl_context.load_verify_locations(CA_CERT_PATH)
            print(f"Loaded CA certificate: {CA_CERT_PATH}")
        
        # 클라이언트 인증서 로드 (선택사항)
        if CLIENT_CERT_PATH and CLIENT_KEY_PATH:
            if os.path.exists(CLIENT_CERT_PATH) and os.path.exists(CLIENT_KEY_PATH):
                ssl_context.load_cert_chain(CLIENT_CERT_PATH, CLIENT_KEY_PATH)
                print("Loaded client certificate")
        
        # 자체서명 인증서 사용 시 호스트명 검증 비활성화
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        self.client.tls_set_context(ssl_context)
    
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """연결 콜백"""
        if reason_code == 0:
            self.connected = True
            print("Connected to EC2 MQTT broker successfully!")
            
            # 명령 토픽 구독
            command_topic = f"{TOPIC_PREFIX}/command/#"
            client.subscribe(command_topic)
            print(f"Subscribed to: {command_topic}")
        else:
            print(f"Connection failed: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        """연결 해제 콜백"""
        self.connected = False
        print(f"Disconnected: {reason_code}")
    
    def _on_message(self, client, userdata, msg):
        """메시지 수신 콜백"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"Received [{topic}]: {payload}")
            
            # JSON 파싱
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = {"raw": payload}
            
            # 핸들러 호출
            for pattern, handlers in self._message_handlers.items():
                if self._topic_matches(pattern, topic):
                    for handler in handlers:
                        handler(topic, data)
                        
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """토픽 패턴 매칭"""
        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')
        
        for i, part in enumerate(pattern_parts):
            if part == '#':
                return True
            if part == '+':
                continue
            if i >= len(topic_parts) or part != topic_parts[i]:
                return False
        
        return len(pattern_parts) == len(topic_parts)
    
    def publish(self, topic: str, data: dict, qos: int = 1) -> bool:
        """메시지 발행"""
        if not self.client or not self.connected:
            print("Not connected to broker")
            return False
        
        try:
            full_topic = f"{TOPIC_PREFIX}/{topic}"
            payload = json.dumps(data)
            
            result = self.client.publish(full_topic, payload, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published [{full_topic}]: {payload}")
                return True
            else:
                print(f"Publish failed: {result.rc}")
                return False
                
        except Exception as e:
            print(f"Publish error: {e}")
            return False
    
    def subscribe(self, topic: str, handler: Callable):
        """토픽 구독 및 핸들러 등록"""
        full_topic = f"{TOPIC_PREFIX}/{topic}"
        
        if full_topic not in self._message_handlers:
            self._message_handlers[full_topic] = []
        
        self._message_handlers[full_topic].append(handler)
    
    def disconnect(self):
        """연결 해제"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print("Disconnected from broker")


def handle_command(topic: str, data: dict):
    """명령 처리 핸들러 예시"""
    print(f"Command received: {data}")
    
    command = data.get("command")
    if command == "start":
        print("Starting operation...")
    elif command == "stop":
        print("Stopping operation...")
    elif command == "status":
        print("Reporting status...")


def handle_box_count_command(topic: str, data: dict):
    """
    박스 개수 명령 처리 핸들러
    
    프론트엔드에서 입력한 박스 개수를 처리합니다.
    토픽: autobox/command/box-count
    
    수신 데이터 형식:
    {
        "command_id": "CMD-XXXXXXXX",
        "command_type": "box_count",
        "box_count": 10,
        "vehicle_id": "AGV-001",
        "priority": "normal",
        "timestamp": "2026-01-26T12:00:00"
    }
    """
    print(f"\n{'='*50}")
    print("📦 박스 개수 명령 수신!")
    print(f"{'='*50}")
    
    command_id = data.get("command_id", "UNKNOWN")
    box_count = data.get("box_count", 0)
    vehicle_id = data.get("vehicle_id", "AGV-001")
    priority = data.get("priority", "normal")
    timestamp = data.get("timestamp", "")
    
    print(f"  명령 ID: {command_id}")
    print(f"  박스 개수: {box_count}개")
    print(f"  차량 ID: {vehicle_id}")
    print(f"  우선순위: {priority}")
    print(f"  전송 시간: {timestamp}")
    print(f"{'='*50}")
    
    # TODO: 실제 하드웨어 제어 로직 구현
    # 예: 컨베이어 벨트 제어, 로봇 암 동작 등
    
    # 처리 완료 응답 발행 (선택사항)
    # client.publish("response/box-count", {
    #     "command_id": command_id,
    #     "status": "received",
    #     "box_count": box_count
    # })
    
    return box_count


def handle_vehicle_command(topic: str, data: dict):
    """
    차량 제어 명령 처리 핸들러
    
    차량의 시작, 정지, 일시정지 등 제어 명령을 처리합니다.
    토픽: autobox/command/vehicle
    
    수신 데이터 형식:
    {
        "command_id": "CMD-XXXXXXXX",
        "command_type": "vehicle_control",
        "command": "start",  // start, stop, pause, resume, emergency_stop
        "vehicle_id": "AGV-001",
        "parameters": {},
        "timestamp": "2026-01-26T12:00:00"
    }
    """
    print(f"\n{'='*50}")
    print("🚗 차량 제어 명령 수신!")
    print(f"{'='*50}")
    
    command_id = data.get("command_id", "UNKNOWN")
    command = data.get("command", "")
    vehicle_id = data.get("vehicle_id", "AGV-001")
    parameters = data.get("parameters", {})
    timestamp = data.get("timestamp", "")
    
    print(f"  명령 ID: {command_id}")
    print(f"  명령: {command}")
    print(f"  차량 ID: {vehicle_id}")
    print(f"  파라미터: {parameters}")
    print(f"  전송 시간: {timestamp}")
    print(f"{'='*50}")
    
    # TODO: 실제 차량 제어 로직 구현
    if command == "start":
        print("  ▶️ 차량 시작...")
    elif command == "stop":
        print("  ⏹️ 차량 정지...")
    elif command == "pause":
        print("  ⏸️ 차량 일시정지...")
    elif command == "resume":
        print("  ▶️ 차량 재개...")
    elif command == "emergency_stop":
        print("  🚨 긴급 정지!")
    
    return command


def main():
    """메인 함수"""
    client = AutoBoxMQTTClient()
    
    # 명령 핸들러 등록
    client.subscribe("command/#", handle_command)
    client.subscribe("command/box-count", handle_box_count_command)
    client.subscribe("command/vehicle", handle_vehicle_command)
    
    # 연결
    if not client.connect():
        print("Failed to connect. Exiting.")
        return
    
    try:
        # 테스트 메시지 발행
        client.publish("sensor/data", {
            "device_id": "rpi-001",
            "temperature": 25.5,
            "humidity": 60,
            "timestamp": datetime.now().isoformat()
        })
        
        client.publish("device/status", {
            "device_id": "rpi-001",
            "status": "online",
            "uptime": 12345
        })
        
        # 메시지 대기
        print("\n" + "="*50)
        print("🚀 AutoBox MQTT Client 시작됨")
        print("="*50)
        print("구독 중인 토픽:")
        print("  - autobox/command/#")
        print("  - autobox/command/box-count (박스 개수 명령)")
        print("  - autobox/command/vehicle (차량 제어 명령)")
        print("="*50)
        print("\nWaiting for messages... (Ctrl+C to exit)")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
