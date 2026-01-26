#!/usr/bin/env python3
"""
AutoBox MQTT Publisher for Raspberry Pi

센서 데이터를 주기적으로 발행하는 예시 스크립트입니다.
로컬 Mosquitto 브로커에 발행하면 브릿지를 통해 EC2로 전달됩니다.

Usage:
    python3 mqtt_publisher.py
"""

import json
import os
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 설정 (로컬 브로커 사용)
BROKER_HOST = os.getenv("LOCAL_BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("LOCAL_BROKER_PORT", "1883"))
DEVICE_ID = os.getenv("DEVICE_ID", "rpi-001")
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", "5"))  # 초


class SensorPublisher:
    """센서 데이터 발행 클래스"""
    
    def __init__(self):
        self.client = mqtt.Client(
            client_id=f"{DEVICE_ID}-publisher",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.connected = False
        
        # 콜백 설정
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            print(f"Connected to local broker at {BROKER_HOST}:{BROKER_PORT}")
        else:
            print(f"Connection failed: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected = False
        print(f"Disconnected: {reason_code}")
    
    def connect(self) -> bool:
        """로컬 브로커에 연결"""
        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            self.client.loop_start()
            
            # 연결 대기
            timeout = 5
            while not self.connected and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            return self.connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def publish_sensor_data(self):
        """센서 데이터 발행"""
        data = {
            "device_id": DEVICE_ID,
            "temperature": round(random.uniform(20, 30), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "pressure": round(random.uniform(1000, 1020), 1),
            "timestamp": datetime.now().isoformat()
        }
        
        topic = "autobox/sensor/data"
        payload = json.dumps(data)
        
        result = self.client.publish(topic, payload, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Published: {data}")
        else:
            print(f"Publish failed: {result.rc}")
    
    def publish_device_status(self, status: str = "online"):
        """디바이스 상태 발행"""
        data = {
            "device_id": DEVICE_ID,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        topic = "autobox/device/status"
        payload = json.dumps(data)
        
        self.client.publish(topic, payload, qos=1, retain=True)
        print(f"Device status: {status}")
    
    def publish_alert(self, alert_type: str, message: str):
        """알림 발행"""
        data = {
            "device_id": DEVICE_ID,
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        topic = f"autobox/alert/{alert_type}"
        payload = json.dumps(data)
        
        self.client.publish(topic, payload, qos=2)
        print(f"Alert: [{alert_type}] {message}")
    
    def disconnect(self):
        """연결 해제"""
        self.publish_device_status("offline")
        self.client.loop_stop()
        self.client.disconnect()


def main():
    """메인 함수"""
    publisher = SensorPublisher()
    
    if not publisher.connect():
        print("Failed to connect to broker. Exiting.")
        return
    
    try:
        # 온라인 상태 발행
        publisher.publish_device_status("online")
        
        print(f"\nPublishing sensor data every {PUBLISH_INTERVAL} seconds...")
        print("Press Ctrl+C to stop\n")
        
        counter = 0
        while True:
            # 센서 데이터 발행
            publisher.publish_sensor_data()
            
            # 10회마다 상태 갱신
            counter += 1
            if counter % 10 == 0:
                publisher.publish_device_status("online")
            
            # 특정 조건에서 알림 발행 (예시)
            if counter % 20 == 0:
                publisher.publish_alert("info", "System check completed")
            
            time.sleep(PUBLISH_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        publisher.disconnect()
        print("Publisher stopped")


if __name__ == "__main__":
    main()
