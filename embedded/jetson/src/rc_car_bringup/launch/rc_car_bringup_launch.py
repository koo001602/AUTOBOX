from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

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

    # --- fake odom ---
    fake_odom = Node(
        package='fake_odom',
        executable='fake_odom_node',
        name='fake_odom',
        output='screen'
    )

    # --- SLAM toolbox (map 제공) ---
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            )
        )
    )

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


    return LaunchDescription([
        ydlidar_launch,
        rc_car,
        fake_odom,
        slam,
        nav2,
    ])

