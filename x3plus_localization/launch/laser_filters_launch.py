# Copyright (c) 2025 Cord Burmeister
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Launch file for the laser_filters scan_to_scan_filter_chain node."""

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    use_sim_time = LaunchConfiguration('use_sim_time')

    laser_filters_cmd = Node(
        package='laser_filters',
        executable='scan_to_scan_filter_chain',
        parameters=[
            PathJoinSubstitution([
                get_package_share_directory('x3plus_bringup'),
                'config', 'laser_filters.yaml',
            ]),
            {'use_sim_time': use_sim_time},
        ],
        remappings=[
            ('/scan', '/scan_raw'),
            ('/scan_filtered', '/scan'),
        ]
    )

    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(laser_filters_cmd)

    return ld
