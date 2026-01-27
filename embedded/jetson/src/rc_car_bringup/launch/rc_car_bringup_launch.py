from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration # [수정] 추가
from launch.conditions import IfCondition # [수정] 추가
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # [추가 1] 앱 모드 스위치 (기본값 True)
    # 실행 시 'ros2 launch ... app:=False'라고 하면 미션 매니저는 끄고 로봇만 켭니다.
    app_arg = DeclareLaunchArgument(
        'app', default_value='False',
        description='Run Mission Manager & MQTT Bridge'
    )
    # --- YDLIDAR launch ---
    ydlidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ydlidar_ros2_driver'),
                'launch',
                'ydlidar_launch_view.py'   # 실전에서는 view 제거
            )
        )
    )

    # --- RF2O launch include ---
    rf2o_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rf2o_laser_odometry'),
                'launch',
                'rf2o_laser_odometry.launch.py'
            )
        )
    )



    # --- Ackermann Wheel Odometry ---
    ackermann_odom = Node(
        package='cpp_ackermann_odom',
        executable='ackermann_odom_node',
        name='ackermann_odom_node',
        output='screen',
    )

    mpu_6050 = Node(
        package='mpu6050_cpp_driver',
        executable='mpu6050_node',
        name='mpu6050_node',
        output='screen'
    )

    madgwick = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter_madgwick_node',
        output='screen',
        parameters=[{
            'use_mag': False,          # MPU6050은 지자기 센서가 없으므로 False 필수!
            'publish_tf': False,       # 나중에 EKF가 tf를 발행할 것이므로 여기선 False
            'world_frame': 'enu'       # 방향 기준 (East-North-Up)
        }]
    )

    imu_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_imu',
        arguments=[
            '0.0', '0.0', '0.0',  # X, Y, Z 위치 (미터 단위) - 센서가 로봇 중앙에 있다면 0,0,0
            '0.0', '0.0', '0.0',  # Yaw, Pitch, Roll 회전 (라디안 단위) - 이 값을 수정합니다!
            'base_link',          # 부모 좌표계 (RC카 중심)
            'imu_link'            # 자식 좌표계 (센서)
        ]
    )
    # --- EKF ---
    ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            os.path.join(
                get_package_share_directory('robot_localization'),
                'params',
                'ekf.yaml'
            )
        ],
        remappings=[
            ('/odometry/filtered', '/odom')
        ]
    )

    # --- fake odom ---
    #fake_odom = Node(
    #    package='fake_odom',
    #    executable='fake_odom_node',
    #    name='fake_odom',
    #    output='screen'
    #)

    # --- Nav2 bringup (SLAM mode) ---
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            )
        ),
        launch_arguments={
            'slam': 'True',
            'use_sim_time': 'False',
            'autostart': 'True',
            'use_composition': 'False',
            'map': '/home/jetson/maps/dummy.yaml',
            'params_file': '/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml',
        }.items()
    )

    rc_car = Node(
        package='rc_car_driver',
        executable='rc_car_node',
        name='rc_car_node',
        output='screen',
        parameters=[{
            'cmd_vel_topic': '/cmd_vel',
            'control_rate': 20.0,
            'cmd_timeout': 0.2,
            'motor_channel': 0,
            'servo_pca_address': 0x60,
            'servo_channel': 0,
            'steer_center_deg': 100.0,
            'wheelbase_m': 0.1375,
            'publish_applied_cmd': True,
            'applied_cmd_topic': '/rc_car/applied_cmd_vel',
            }],
        )

    # -------------------------------------------------------------
    # [추가 2] Application Layer (MQTT Bridge & Mission Manager)
    # -------------------------------------------------------------

    # 1. MQTT Bridge Launch 포함 (params.yaml도 여기서 자동 로드됨)
    mqtt_bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('mqtt_bridge_pkg'),
                'launch',
                'bridge_launch.py'
            )
        ),
        condition=IfCondition(LaunchConfiguration('app')) # app:=True일 때만 실행
    )

    # 2. Mission Manager Node (C++)
    mission_manager_node = Node(
        package='mission_manager',
        executable='mission_manager_node',
        name='mission_manager',
        output='screen',
        condition=IfCondition(LaunchConfiguration('app')) # app:=True일 때만 실행
    )

    return LaunchDescription([
        app_arg,            # [추가] 아규먼트 등록
        ydlidar_launch,
        rf2o_launch,
        ackermann_odom,
        #mpu_6050,
        #madgwick,
        #imu_tf,
        ekf,
        rc_car,
        nav2,
        # [추가] 앱 계층 실행
        mqtt_bridge_launch,
        mission_manager_node
    ])

