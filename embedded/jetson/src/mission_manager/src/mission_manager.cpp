#include "mission_manager/mission_manager.hpp"

using namespace std::chrono_literals;

MissionManager::MissionManager() : Node("mission_manager_node") {
  // 1. 초기화
  current_state_ = MissionState::IDLE;
  nav2_goal_reached_ = false;

  // 컨베이어 벨트 위치 (Home) 설정 - 실제 맵 좌표로 수정 필요!
  home_pose_.header.frame_id = "map";
  home_pose_.pose.position.x = 0.0;
  home_pose_.pose.position.y = 0.0;
  home_pose_.pose.orientation.w = 1.0;

  // 2. 통신 설정
  // Nav2 클라이언트
  nav_client_ = rclcpp_action::create_client<NavigateToPose>(this, "navigate_to_pose");

  // Subscriber: 라즈베리파이 명령 (적재 완료 & 목적지 수신)
  rpi_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
      "mission/start_delivery", 10,
      std::bind(&MissionManager::rpi_command_callback, this, std::placeholders::_1));

  // Subscriber: 외부 모듈 완료 신호 (주차, 하차)
  parking_sub_ = this->create_subscription<std_msgs::msg::Bool>(
      "system/parking_done", 10,
      std::bind(&MissionManager::parking_done_callback, this, std::placeholders::_1));
  unloading_sub_ = this->create_subscription<std_msgs::msg::Bool>(
      "system/unloading_done", 10,
      std::bind(&MissionManager::unloading_done_callback, this, std::placeholders::_1));

  // Publisher
  rpi_status_pub_ = this->create_publisher<std_msgs::msg::String>("mission/status", 10);
  actuator_pub_ = this->create_publisher<std_msgs::msg::Bool>("system/actuator_cmd", 10);
  reverse_parking_pub_ = this->create_publisher<std_msgs::msg::Bool>("system/start_parking", 10);

  // 3. 상태 머신 루프 시작 (0.1초마다 실행)
  timer_ = this->create_wall_timer(
      100ms, std::bind(&MissionManager::state_machine_loop, this));

  RCLCPP_INFO(this->get_logger(), "Mission Manager Ready. Waiting for Cargo...");
}

// =================================================================================
// 핵심: 상태 머신 루프
// =================================================================================
void MissionManager::state_machine_loop() {
  std_msgs::msg::String status_msg;

  switch (current_state_) {
    case MissionState::IDLE:
      // 라즈베리파이로부터 start_delivery 토픽이 오면 콜백에서 NAV_TO_TARGET으로 변경됨
      break;

    case MissionState::NAV_TO_TARGET:
      if (nav2_goal_reached_) {
        RCLCPP_INFO(this->get_logger(), "[2->3] Arrived near target. Starting Reverse Parking...");
        nav2_goal_reached_ = false;
        
        // 주차 노드에 시작 신호 보냄
        std_msgs::msg::Bool msg; msg.data = true;
        reverse_parking_pub_->publish(msg);
        
        current_state_ = MissionState::PARKING_AT_TARGET;
      }
      break;

    case MissionState::PARKING_AT_TARGET:
      // parking_done_callback에서 신호를 받으면 UNLOADING으로 넘어감
      break;

    case MissionState::UNLOADING:
      // 하차 시작 명령 (최초 1회 전송 로직이 필요할 수 있음)
      {
        static bool cmd_sent = false;
        if (!cmd_sent) {
            std_msgs::msg::Bool msg; msg.data = true; // 하차 시작
            actuator_pub_->publish(msg);
            cmd_sent = true;
            RCLCPP_INFO(this->get_logger(), "[3->4] Parking Done. Starting Unloading...");
        }
        // unloading_done_callback에서 신호를 받으면 다음으로 넘어감
        // 넘어갈 때 cmd_sent = false로 초기화 해줘야 함 (콜백 참조)
      }
      break;

    case MissionState::NAV_TO_HOME:
      if (nav2_goal_reached_) {
        RCLCPP_INFO(this->get_logger(), "[5->6] Arrived near Home. Starting Reverse Parking...");
        nav2_goal_reached_ = false;
        
        // 주차 노드에 시작 신호 보냄
        std_msgs::msg::Bool msg; msg.data = true;
        reverse_parking_pub_->publish(msg);
        
        current_state_ = MissionState::PARKING_AT_HOME;
      }
      break;

    case MissionState::PARKING_AT_HOME:
       // parking_done_callback에서 신호를 받으면 IDLE로 복귀
      break;
  }
}

// =================================================================================
// 콜백 함수들
// =================================================================================

// 1. 라즈베리파이 -> 미션 시작 명령 (적재 완료 & 좌표 수신)
void MissionManager::rpi_command_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
  if (current_state_ == MissionState::IDLE) {
    RCLCPP_INFO(this->get_logger(), "[1->2] Cargo Loaded! Destination received. Navigating...");
    target_pose_ = *msg; // 목적지 저장
    
    // Nav2 주행 시작
    send_nav2_goal(target_pose_);
    current_state_ = MissionState::NAV_TO_TARGET;
    
    // 상태 보고
    std_msgs::msg::String status; status.data = "DELIVERING";
    rpi_status_pub_->publish(status);
  } else {
    RCLCPP_WARN(this->get_logger(), "Ignored command. Robot is busy.");
  }
}

// 2. 외부 주차 노드 -> 주차 완료 신호
void MissionManager::parking_done_callback(const std_msgs::msg::Bool::SharedPtr msg) {
  if (msg->data) {
    if (current_state_ == MissionState::PARKING_AT_TARGET) {
      // 하차 단계로 진입
      current_state_ = MissionState::UNLOADING; 
    } 
    else if (current_state_ == MissionState::PARKING_AT_HOME) {
      // 모든 미션 완료! 다시 대기
      RCLCPP_INFO(this->get_logger(), "[6->1] Mission Complete! Ready for next cargo.");
      
      std_msgs::msg::String status; status.data = "IDLE_READY";
      rpi_status_pub_->publish(status);
      
      current_state_ = MissionState::IDLE;
    }
  }
}

// 3. 액추에이터 노드 -> 하차 완료 신호
void MissionManager::unloading_done_callback(const std_msgs::msg::Bool::SharedPtr msg) {
  if (msg->data && current_state_ == MissionState::UNLOADING) {
    RCLCPP_INFO(this->get_logger(), "[4->5] Unloading Done. Returning to Conveyor...");
    
    // Home으로 복귀 주행 시작
    send_nav2_goal(home_pose_);
    current_state_ = MissionState::NAV_TO_HOME;
  }
}

// 4. Nav2 액션 전송
void MissionManager::send_nav2_goal(const geometry_msgs::msg::PoseStamped& pose) {
  if (!nav_client_->wait_for_action_server(std::chrono::seconds(2))) {
    RCLCPP_ERROR(this->get_logger(), "Nav2 Action Server not available!");
    return;
  }

  auto goal_msg = NavigateToPose::Goal();
  goal_msg.pose = pose;

  auto send_goal_options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
  send_goal_options.result_callback = 
      std::bind(&MissionManager::nav2_result_callback, this, std::placeholders::_1);

  nav_client_->async_send_goal(goal_msg, send_goal_options);
}

// 5. Nav2 도착 확인
void MissionManager::nav2_result_callback(const GoalHandleNav::WrappedResult & result) {
  if (result.code == rclcpp_action::ResultCode::SUCCEEDED) {
    RCLCPP_INFO(this->get_logger(), "Nav2 Goal Reached!");
    nav2_goal_reached_ = true;
  } else {
    RCLCPP_ERROR(this->get_logger(), "Nav2 Failed or Canceled.");
    // 실패 시 처리는 프로젝트 요건에 따라 추가 (예: 재시도, 비상정지 등)
  }
}

// 메인 함수
int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MissionManager>());
  rclcpp::shutdown();
  return 0;
}
