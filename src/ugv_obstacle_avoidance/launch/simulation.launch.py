
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
def generate_launch_description():

    pkg_share = get_package_share_directory('ugv_obstacle_avoidance')
    world_file = os.path.join(pkg_share, 'worlds', 'obstacle_world.world')
    urdf_file  = os.path.join(pkg_share, 'urdf',   'ugv_robot.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')
    gazebo_launch  = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file, 'verbose': 'false'}.items(),
    )
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'ugv_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0',
        ],
    )
    avoidance_node = Node(
        package='ugv_obstacle_avoidance',
        executable='obstacle_avoidance_node',
        name='obstacle_avoidance_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    delayed_avoidance = TimerAction(
        period=3.0,
        actions=[avoidance_node],
    )
    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        delayed_avoidance,
    ])
