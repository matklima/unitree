import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    klimaby_path = get_package_share_directory('klimaby')
    go2_config_path = get_package_share_directory('go2_config')

    # 1. Tvoj Xacro s laserom
    xacro_file = os.path.join(klimaby_path, 'urdf', 'go2_with_laser.xacro')
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw, 'use_sim_time': True}]
    )

    # Uključi launch iz drugog repozitorija
    go2_gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(go2_config_path, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(go2_config_path, 'worlds', 'outdoor.world'),
            'use_sim_time': 'true',
            'use_rsp': 'false' 
        }.items()
    )

    return LaunchDescription([
        rsp_node,
        go2_gazebo_launch
    ])