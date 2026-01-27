#ifndef MISSION_MANAGER_HPP_
#define MISSION_MANAGER_HPP_

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "nav2_msgs/action/navigate_to_pose.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "std_msgs/msg/bool.hpp"
#include "std_msgs/msg/string.hpp"

// 상태 정의
enum class MissionState {
  IDLE,                 // 1. 대기 (화물 적재 대기)
  NAV_TO_TARGET,        // 2. 배송지로 주행 중
  PARKING_AT_TARGET,    // 3. 배송지 도착 후 정밀 후진 주차 중
  UNLOADING,            // 4. 화물 하차 중
  NAV_TO_HOME,          // 5. 복귀 지점으로 주행 중
  PARKING_AT_HOME       // 6. 복귀 후 정밀 후진 주차 중
};

class MissionManager : public rclcpp::Node {
public:
  using NavigateToPose = nav2_msgs::action::NavigateToPose;
  using GoalHandleNav = rclcpp_action::ClientGoalHandle<NavigateToPose>;

  MissionManager();

private:
  // --- 주기적 상태 체크 ---
  void state_machine_loop();

  // --- 통신 콜백 함수들 ---
  // 라즈베리파이로부터 "적재 완료 + 목적지 좌표"를 받는 토픽
  void rpi_command_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg);
  
  // 외부 주차 노드나 하차 액추에이터로부터 "작업 완료" 신호를 받는 토픽 (가정)
  void parking_done_callback(const std_msgs::msg::Bool::SharedPtr msg);
  void unloading_done_callback(const std_msgs::msg::Bool::SharedPtr msg);

  // --- Nav2 관련 함수들 ---
  void send_nav2_goal(const geometry_msgs::msg::PoseStamped& pose);
  void nav2_result_callback(const GoalHandleNav::WrappedResult & result);

  // --- 내부 변수 ---
  rclcpp::TimerBase::SharedPtr timer_;
  
  // Nav2 Action Client
  rclcpp_action::Client<NavigateToPose>::SharedPtr nav_client_;
  
  // Publishers & Subscribers
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr rpi_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr parking_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr unloading_sub_;
  
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr rpi_status_pub_;   // 상태 보고용
  rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr actuator_pub_;       // 하차 명령용
  rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr reverse_parking_pub_;// 주차 시작 명령용

  // 데이터 저장용
  MissionState current_state_;
  geometry_msgs::msg::PoseStamped target_pose_; // 배송지 좌표
  geometry_msgs::msg::PoseStamped home_pose_;   // 컨베이어벨트 좌표 (고정값)
  
  bool nav2_goal_reached_ = false; // Nav2 도착 여부 플래그
};

#endif // MISSION_MANAGER_HPP_
