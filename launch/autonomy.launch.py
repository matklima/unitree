from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='klimaby',
            executable='perception_node',
            name='perception_node',
            output='screen',
        ),
        Node(
            package='klimaby',
            executable='decision_node',
            name='decision_node',
            output='screen',
        ),
        Node(
            package='klimaby',
            executable='actuation_node',
            name='actuation_node',
            output='screen',
        ),
    ])