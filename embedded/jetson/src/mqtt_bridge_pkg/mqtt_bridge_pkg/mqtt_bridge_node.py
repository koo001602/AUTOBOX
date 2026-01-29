import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import String, Bool
import paho.mqtt.client as mqtt
import json
import math
import yaml
import os

class SmartMqttBridge(Node):
    def __init__(self):
        super().__init__('smart_mqtt_bridge')

        # ---------------------------------------------------------
        # 1. 파라미터 선언 및 불러오기
        # ---------------------------------------------------------
        self.declare_parameter('mqtt_broker_ip', '127.0.0.1')
        self.declare_parameter('mqtt_port', 1883)
        self.declare_parameter('topic_cmd_sub', 'rpi/command')
        self.declare_parameter('topic_status_pub', 'device/rc1/state')
        
        # [추가됨] RPi(컨베이어) 제어를 위한 토픽 파라미터
        # RPi 코드 기준: device/{장치ID}/cmd 형식이어야 함
        self.declare_parameter('topic_rpi_control', 'device/rc1/cmd') 
        self.declare_parameter('waypoint_file_path', '')

        self.broker_ip = self.get_parameter('mqtt_broker_ip').value
        self.mqtt_port = self.get_parameter('mqtt_port').value
        self.topic_sub = self.get_parameter('topic_cmd_sub').value
        self.topic_pub = self.get_parameter('topic_status_pub').value
        
        # [추가됨] 변수에 저장
        self.topic_rpi_control = self.get_parameter('topic_rpi_control').value
        
        waypoint_file = self.get_parameter('waypoint_file_path').value

        # ---------------------------------------------------------
        # 2. 좌표 파일 로딩 (생략 - 기존 동일)
        # ---------------------------------------------------------
        self.waypoints = {}
        try:
            if waypoint_file: # 파일 경로가 있을 때만 로드
                with open(waypoint_file, 'r') as f:
                    self.waypoints = yaml.safe_load(f)
                self.get_logger().info(f"Loaded {len(self.waypoints)} waypoints")
        except Exception as e:
            self.get_logger().error(f"Failed to load waypoints: {e}")

        # ---------------------------------------------------------
        # 3. ROS 2 통신 설정
        # ---------------------------------------------------------
        '''
        self.mission_start_pub = self.create_publisher(PoseStamped, 'mission/start_delivery', 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(String, 'mission/status', self.state_callback, 10)
        self.create_subscription(Bool, 'system/parking_done', self.parking_callback, 10)
        '''
        # 상태 변수
        self.current_speed = 0.0
        self.mission_state = "IDLE"
        self.is_parking_done = False
        
        # [추가됨] 중복 전송 방지를 위한 플래그
        self.conveyor_triggered = False 

        # ---------------------------------------------------------
        # 4. MQTT 연결
        # ---------------------------------------------------------
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "JetsonBridge")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(self.broker_ip, self.mqtt_port, 60)
            self.client.loop_start()
            self.get_logger().info(f"Connected to MQTT Broker: {self.broker_ip}")
        except Exception as e:
            self.get_logger().error(f"MQTT Connection Failed: {e}")

        # 5. 상태 보고 타이머
        self.create_timer(0.5, self.publish_robot_status)

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic_sub)

    def on_message(self, client, userdata, msg):
        # (기존 코드 동일 - 생략)
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            target_name = payload.get("target")

            if target_name in self.waypoints:
                data = self.waypoints[target_name]
                ros_msg = PoseStamped()
                ros_msg.header.frame_id = "map"
                ros_msg.header.stamp = self.get_clock().now().to_msg()
                ros_msg.pose.position.x = float(data[0])
                ros_msg.pose.position.y = float(data[1])
                theta = float(data[2])
                ros_msg.pose.orientation.z = math.sin(theta / 2.0)
                ros_msg.pose.orientation.w = math.cos(theta / 2.0)

                self.mission_start_pub.publish(ros_msg)
                
                # [중요] 새로운 미션 시작 시 플래그 초기화
                self.is_parking_done = False
                self.conveyor_triggered = False 
                
                self.get_logger().info(f"Target '{target_name}' command sent.")
            else:
                self.get_logger().warn(f"Unknown target: {target_name}")

        except Exception as e:
            self.get_logger().error(f"MQTT Parsing Error: {e}")

    def odom_callback(self, msg):
        self.current_speed = msg.twist.twist.linear.x

    def state_callback(self, msg):
        self.mission_state = msg.data

    # [수정됨] 여기가 핵심입니다. 주차가 완료되면 RPi에 데이터를 보냅니다.
    def parking_callback(self, msg):
        self.is_parking_done = msg.data

        # 주차가 완료되었고, 아직 컨베이어 명령을 안 보냈다면
        if self.is_parking_done and not self.conveyor_triggered:
            self.send_conveyor_cmd("PUSH") # RPi로 명령 전송
            self.conveyor_triggered = True # 중복 전송 방지

    # [추가됨] RPi 형식에 맞춰 데이터 전송하는 함수
    def send_conveyor_cmd(self, command):
        # RPi 코드 요구사항: payload에 'cmd' 키가 있어야 함
        payload = {
            "device_id": "rc1",
            "cmd": command,
        }
        json_payload = json.dumps(payload)
        
        # RPi 코드 요구사항: topic은 'device/{id}/cmd' 여야 함
        self.client.publish(self.topic_rpi_control, json_payload)
        self.get_logger().info(f"Sent MQTT to RPi: {self.topic_rpi_control} -> {json_payload}")

    def publish_robot_status(self):
        # (기존 코드 동일)
        status_data = {
            "device_id": "rc1",
            "speed": round(self.current_speed, 2),
            "state": self.mission_state,
            "parking_done": self.is_parking_done
        }
        self.client.publish(self.topic_pub, json.dumps(status_data))

def main(args=None):
    rclpy.init(args=args)
    node = SmartMqttBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
