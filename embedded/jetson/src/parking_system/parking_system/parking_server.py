import time
import math
import numpy as np
import cv2
import cv2.aruco as aruco

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor

# [NEW] 속도 명령 메시지 임포트
from geometry_msgs.msg import Twist

# Action 인터페이스
from custom_interfaces.action import Parking

# 같은 폴더에 있는 라이브러리 (rc_car_driver는 제거됨)
import parking_system.stanley_control as sc

class ParkingActionServer(Node):

    def __init__(self):
        super().__init__('parking_server_node')

        # ----------------------------------------
        # 1. 통신 설정 (Action Server & CMD Publisher)
        # ----------------------------------------
        self._action_server = ActionServer(
            self,
            Parking,
            'parking_action',
            self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        # [NEW] 모터 제어 대신 cmd_vel_parking 토픽 발행
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel_parking', 10)

        # ----------------------------------------
        # 2. 파라미터 설정
        # ----------------------------------------
        self.WHEEL_BASE = 0.1375
        self.MAX_STEER = np.radians(20.0)
        
        # 마커 설정
        self.MARKER_SIZE = 0.10
        self.MARKER_GAP = 0.155
        
        # 제어 파라미터
        self.STOP_DISTANCE = 0.50
        self.SLOW_DISTANCE = 1.0
        self.FAST_SPEED = -0.15
        self.SLOW_SPEED = -0.1

        # ----------------------------------------
        # 3. 카메라 설정
        # ----------------------------------------
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.cam_matrix = np.array([[1155, 0, 640], [0, 1155, 360], [0, 0, 1]], dtype=float)
        self.dist_coeffs = np.zeros(5)

        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.parameters)

        # ----------------------------------------
        # 4. 상태 변수
        # ----------------------------------------
        self.state = sc.State(x=0.0, y=0.0, yaw=0.0, v=0.0)
        self.LATERAL_TOLERANCE = 0.03
        self.HEADING_TOLERANCE = np.radians(5.0)
        self.correction_mode = False

        self.get_logger().info("Parking Action Server Ready (Publishing to /cmd_vel_parking)")

    # --- Action Callbacks ---

    def goal_callback(self, goal_request):
        self.get_logger().info('Received Goal Request')
        if goal_request.start_parking:
            return GoalResponse.ACCEPT
        return GoalResponse.REJECT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received Cancel Request')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing Parking Sequence...')
        
        feedback_msg = Parking.Feedback()
        result = Parking.Result()
        parking_complete = False

        try:
            while rclpy.ok() and not parking_complete:
                # 1. 취소 요청 확인
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.stop_car()
                    self.get_logger().info('Parking Canceled')
                    return result

                # 2. 영상 처리
                ret, frame = self.cap.read()
                if not ret:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners, ids, rejected = self.detector.detectMarkers(gray)

                detected = False
                control_steer = 0.0
                control_speed = 0.0
                
                if ids is not None:
                    poses_x, poses_y, poses_yaw = [], [], []
                    ids_flat = ids.flatten()
                    
                    for i, m_id in enumerate(ids_flat):
                        if m_id in [0, 1]:
                            obj_pts = np.array([[-self.MARKER_SIZE/2, self.MARKER_SIZE/2, 0],
                                                [self.MARKER_SIZE/2, self.MARKER_SIZE/2, 0],
                                                [self.MARKER_SIZE/2, -self.MARKER_SIZE/2, 0],
                                                [-self.MARKER_SIZE/2, -self.MARKER_SIZE/2, 0]], dtype=np.float32)
                            
                            _, rvec, tvec = cv2.solvePnP(obj_pts, corners[i][0], self.cam_matrix, self.dist_coeffs)
                            px, py, pyaw = self.get_pose_from_marker(rvec, tvec, m_id)
                            poses_x.append(px)
                            poses_y.append(py)
                            poses_yaw.append(pyaw)

                    if poses_x:
                        detected = True
                        self.state.x = np.mean(poses_x)
                        self.state.y = np.mean(poses_y)
                        self.state.yaw = np.mean(poses_yaw)

                        # (A) 가상 경로 설정
                        if self.state.y > 0:
                            path_y = np.arange(self.state.y, -0.2, -0.05)
                            path_x = np.zeros_like(path_y)
                            path_yaw = np.zeros_like(path_y)
                        else:
                            path_y = np.array([0.0])
                            path_x = np.array([0.0])
                            path_yaw = np.array([0.0])

                        dist = self.state.y
                        current_gear = -1
                        
                        feedback_msg.distance = float(dist)
                        goal_handle.publish_feedback(feedback_msg)

                        # (B) 상태 결정
                        if self.correction_mode:
                            if dist > 0.9:
                                self.correction_mode = False
                                control_speed = 0.0
                            else:
                                control_speed = 0.15
                                current_gear = 1
                        
                        elif dist < self.STOP_DISTANCE:
                            is_lat_ok = abs(self.state.x) < self.LATERAL_TOLERANCE
                            is_head_ok = abs(self.state.yaw) < self.HEADING_TOLERANCE
                            
                            if is_lat_ok and is_head_ok:
                                control_speed = 0.0
                                parking_complete = True
                                self.get_logger().info("PARKING SUCCESS!")
                            else:
                                self.correction_mode = True
                                control_speed = 0.0
                                self.get_logger().warn("Retry needed")

                        elif dist < self.SLOW_DISTANCE:
                            control_speed = self.SLOW_SPEED
                        else:
                            control_speed = self.FAST_SPEED

                        # (C) Stanley Control
                        if control_speed != 0.0:
                            self.state.v = control_speed
                            delta, _ = sc.stanley_control(
                                self.state, path_x, path_y, path_yaw, 0, gear=current_gear
                            )
                            if current_gear == 1:
                                delta = -delta
                            control_steer = delta
                        else:
                            control_steer = 0.0
                        
                        # [NEW] Twist 메시지 발행
                        vel_w = (control_speed / self.WHEEL_BASE)*math.tan(-control_steer)
                        self.publish_cmd_vel(control_speed, vel_w)

                if not detected:
                    self.stop_car()

                time.sleep(0.05)

        except Exception as e:
            self.get_logger().error(f"Error: {e}")
            self.stop_car()
            goal_handle.abort()
            result.success = False
            return result

        self.stop_car()
        
        if parking_complete:
            goal_handle.succeed()
            result.success = True
            result.message = "Parking Complete"
        
        return result

    # --- Helper Functions ---
    def publish_cmd_vel(self, speed, steer):
        """속도와 조향각을 Twist 메시지로 발행"""
        msg = Twist()
        msg.linear.x = float(speed)
        msg.angular.z = float(steer) # 받는 쪽에서 이를 조향각(rad)으로 해석해야 함
        self.cmd_vel_pub.publish(msg)

    def stop_car(self):
        """정지 명령 발행"""
        self.publish_cmd_vel(0.0, 0.0)

    def get_pose_from_marker(self, rvec, tvec, marker_id):
        # (기존 코드와 동일)
        R, _ = cv2.Rodrigues(rvec)
        cam_pos = -np.dot(R.T, tvec)
        x = cam_pos[0][0]
        z = cam_pos[2][0]
        cam_z = R.T[:, 2]
        yaw = math.atan2(cam_z[0], cam_z[2]) 
        yaw = self.normalize_angle(yaw + math.pi)
        offset = -self.MARKER_GAP/2.0 if marker_id == 0 else self.MARKER_GAP/2.0
        return x + offset, z, yaw

    def normalize_angle(self, angle):
        while angle > math.pi: angle -= 2.0 * math.pi
        while angle < -math.pi: angle += 2.0 * math.pi
        return angle

def main(args=None):
    rclpy.init(args=args)
    parking_server = ParkingActionServer()
    executor = MultiThreadedExecutor()
    rclpy.spin(parking_server, executor=executor)
    parking_server.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
