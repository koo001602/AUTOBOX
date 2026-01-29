import paho.mqtt.client as mqtt
from conveyer_belt_control import ConveyerController
import ssl
import time
import json
import os

conveyer = ConveyerController()
conveyer.servo_set()

# --- 로컬 리스너 (젯슨 -> 라즈베리파이) ---

def on_local_message(client, userdata, msg):
    client_local.publish("device/rp","check")
    topic = msg.topic
    
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[LOCAL] {topic}: {payload}") # 예: {'cmd': 'PUSH', 'speed': 50}
    except json.JSONDecodeError:
        print(f"[LOCAL] JSON 형식이 아닙니다: {msg.payload}")
        return

    parts = topic.split('/')
    
    
    if len(parts) < 3:
        return

    device_id = parts[1] #  'rc1',  'rc2'  ,  'rc3'   현재 프로젝트에선 1개만 존재.
    msg_type = parts[2]  #  'cmd',  'state',  'event'

    
    if msg_type == "cmd":
       
        if payload.get("cmd") == "PUSH":
            print(f" load to [{device_id}]")

            conveyer.servo_push()
            time.sleep(1)
            conveyer.servo_pull()
            
            event_data = {
                "event": "push_done",
                "device_id": device_id,
                "status": "success",
                "timestamp": time.time()
            }

            client_server.publish("server/factory/event", json.dumps(event_data))

    elif msg_type == "state":
        print(f"[{device_id}] 상태 업데이트: {payload}")
        # 서버로 그대로 토스 (중계)
        # payload에 device_id를 추가해서 보내주면 서버가 좋아함

        #payload['device_id'] = device_id 
        #client_server.publish("server/factory/state", json.dumps(payload))

    elif msg_type == "event":
        print(f"[{device_id}] 이벤트 발생: {payload}")
        # 서버로 중계
        #client_server.publish("server/factory/event", json.dumps(payload))


# --- 서버 리스너 (EC2 -> 라즈베리파이) ---


def on_server_message(client, userdata, msg):
    topic = msg.topic

    try:
        payload = json.loads(msg.payload.decode())
        print(f"[SERVER 수신] {topic}: {payload}")
    except json.JSONDecodeError:
        return

    
    if topic == "server/factory/cmd":
        if payload.get("control") == "run":
            print("컨베이어 벨트 가동")
            conveyer.belt_run()




# --- 클라이언트 설정  ---

# 1. 라즈베리파이 - 로컬 객체
client_local = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client_local.on_message = on_local_message
client_local.connect("mqtt-broker", 1883)
client_local.subscribe("device/+/+") # device/{아무거나}/{아무거나} 다 받음


# 2. 서버 - 라즈베리파이 객체
def on_server_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("✅ EC2 서버 연결 성공 (TLS)")
        client.subscribe("server/factory/cmd")
        client.subscribe("server_msg/#")
        client.subscribe("command/#")
        client.subscribe("factory_msg/command/#")
    else:
        print(f"❌ 서버 연결 실패: {rc}")

client_server = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client_server.on_connect = on_server_connect
client_server.on_message = on_server_message

#  계정 정보 설정 (EC2 passwd 파일에 등록한 정보) 필요한 경우 나중에 ec2에서 동시 변경
client_server.username_pw_set("factory1", "p_factory1") 

#------------------


# 1. 인증서 경로 (Docker 내부 경로)
ca_cert = "/certs/ca.crt"
client_cert = "/certs/client.crt"
client_key = "/certs/client.key"

# 2. 파일 존재 여부 확인 (디버깅용 로그)
if os.path.exists(ca_cert):
    print(f"✅ 인증서 발견: {ca_cert}")
else:
    print(f"🚨 파일 없음: {ca_cert} (Docker 볼륨 마운트 확인 필요)")

# 3. TLS 설정 (단 한 번만 호출해야 함!)
try:
    client_server.tls_set(
        ca_certs=ca_cert,
        certfile=client_cert,
        keyfile=client_key,
        cert_reqs=ssl.CERT_NONE,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    print("insecur확인")
    client_server.tls_insecure_set(True)
    print("✅ TLS 설정 완료")
except ValueError:
    print("⚠️ 이미 TLS가 설정되어 있어 건너뜁니다.")
except Exception as e:
    print(f"🚨 TLS 설정 에러: {e}")

client_server.subscribe("command/#") # device/{아무거나}/{아무거나} 다 받음
client_server.subscribe("factory_msg/command/#")

# 4. 연결
client_server.connect("43.201.254.235", 8883)




# ------ 실행 --------
client_local.loop_start()  
client_server.loop_start() 


try:
    while True:
        time.sleep(1) 
except KeyboardInterrupt:
    print("종료")
    conveyer.cleanup()
    client_local.loop_stop()
    client_server.loop_stop()
