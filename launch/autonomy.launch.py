from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='klimaby',
            executable='perception_node',
            parameters=[{'use_sim_time': True}],
            output='screen'
        ),
        Node(
            package='klimaby',
            executable='decision_node',
            parameters=[{'use_sim_time': True}],
            output='screen'
        ),
        Node(
            package='klimaby',
            executable='actuation_node',
            parameters=[{'use_sim_time': True}],
            output='screen'
        ),
    ])