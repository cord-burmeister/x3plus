# Copyright 2026 x3plus contributors
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

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction, SetLaunchConfiguration
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import socket


def validate_enum_arg(context, name, valid):
    value = context.launch_configurations[name]
    if value not in valid:
        raise ValueError(
            f"Argument '{name}' must be one of {valid}, got '{value}'"
        )



def resolve_world_for_hostname() -> tuple[str, str, str]:
	"""Resolve the default world package and file for the current hostname."""
	hostname = socket.gethostname()
	normalized_hostname = hostname.split(".")[0].lower()
	package_name, world_name = HOSTNAME_WORLD_MAP.get(normalized_hostname, DEFAULT_WORLD)
	world_package = get_package_share_directory(package_name)
	return hostname, world_package, world_name

def generate_launch_description() -> LaunchDescription:
	"""Generate a ROS 2 launch description skeleton."""
	# Launch arguments
	use_sim_time = LaunchConfiguration("use_sim_time")
	robot_name = LaunchConfiguration("robot_name")
	mode = LaunchConfiguration("mode")
	use_case = LaunchConfiguration("use_case")



	declared_arguments = [
		DeclareLaunchArgument(
			"use_sim_time",
			default_value="true",
			description="Use simulation (Gazebo) clock if true.",
		),
		DeclareLaunchArgument(
			"mode",
			default_value="simulation",
			description="Launch mode: simulation, companion, hil, robot).",
		),
		DeclareLaunchArgument(
			"use_case",
			default_value="slam",
			description="Use case for the robot: drive, slam, explore, explore-lite, explore-roadmap, explore-frontier.",
		),
		DeclareLaunchArgument(
			"robot_name",
			default_value="x3plus_bot",
			description="Robot name namespace/identifier.",
		),

		DeclareLaunchArgument(
			'visualize',
			default_value='True',
			description='Whether to visualize the exploration frontier markers in RViz'),

		DeclareLaunchArgument(
			'use_nav2',
			default_value='True',
			description='Whether to start the Nav2 stack'),
		DeclareLaunchArgument(
			'map',
			default_value=PathJoinSubstitution([FindPackageShare('x3plus_nav2'), 'maps', 'map.yaml']),
			description='Full path to map file to load'),
		DeclareLaunchArgument(
			'params_file',
			default_value=PathJoinSubstitution([FindPackageShare('x3plus_nav2'), 'config', 'nav2_params-MPPIController.yaml']),
			description='Full path to the Nav2 parameters file'),
    	DeclareLaunchArgument(
			'frontier_explore_config_file',
			default_value=PathJoinSubstitution([FindPackageShare('x3plus_nav2'), 'config', 'frontier-exploration-params.yaml']),
			description='Full path to the ROS2 parameters file to use for frontier exploration'), 			
		DeclareLaunchArgument(
			'slam',
			default_value='True',
			description='Whether to run SLAM'),
		DeclareLaunchArgument(
			'autostart',
			default_value='true',
			description='Automatically startup the Nav2 stack'),
		DeclareLaunchArgument(
			'use_composition',
			default_value='False',
			description='Whether to use composed bringup'),
		DeclareLaunchArgument(
			'use_respawn',
			default_value='False',
			description='Whether to respawn if a node crashes'),
	]

	launch_actions = [

		#region Validation of enum arguments
		OpaqueFunction(
            function=lambda context: validate_enum_arg(
                context,
                'mode',
                ['simulation', 'companion', 'hil', 'robot']
            )
        ),
		OpaqueFunction(
            function=lambda context: validate_enum_arg(
                context,
                'use_case',
                ['drive', 'slam', 'explore', 'explore-lite', 'explore-roadmap', 'explore-frontier']
            )
        ),
		OpaqueFunction(
            function=lambda context: validate_enum_arg(
                context,
                'use_ui',
                ['cockpit', 'rviz', 'none']
            )
        ),
		OpaqueFunction(
            function=lambda context: validate_enum_arg(
                context,
                'use_bridge',
                ['none', 'bridge', 'foxglove']
            )
        ),
		# endregion

		#region Include localization launch files
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
				PathJoinSubstitution([
					FindPackageShare("x3plus_localization"),
					"launch",
					"laser_filters_launch.py",
				])
			),
			launch_arguments={
				"use_sim_time": LaunchConfiguration("use_sim_time"),
			}.items(),
			condition=IfCondition(
				PythonExpression(["'", mode, "' in ['simulation', 'companion']"])
			),
		),
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
				PathJoinSubstitution([
					FindPackageShare("x3plus_localization"),
					"launch",
					"wheel_localization_launch.py",
				])
			),
			launch_arguments={
				"use_sim_time": LaunchConfiguration("use_sim_time"),
			}.items(),
			condition=IfCondition(
				PythonExpression(["'", mode, "' in ['simulation', 'companion']"])
			),
		),
		#endregion

		#region Include Nav2 launch file
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
				PathJoinSubstitution([
					FindPackageShare('x3plus_nav2'),
					'launch',
					'nav2_launch.py',
				])
			),
			launch_arguments={
				'use_sim_time':    LaunchConfiguration('use_sim_time'),
				'map':             LaunchConfiguration('map'),
				'params_file':     LaunchConfiguration('params_file'),
				'slam':            LaunchConfiguration('slam'),
				'autostart':       LaunchConfiguration('autostart'),
				'use_composition': LaunchConfiguration('use_composition'),
				'use_respawn':     LaunchConfiguration('use_respawn'),
			}.items(),
			condition=IfCondition(
				PythonExpression(["'", use_case, "' in ['slam', 'explore', 'explore-lite', 'explore-frontier', 'explore-roadmap']",
					" and ",
					"('", mode,"' in ['simulation', 'companion'])"
				])
			),
		),
		#endregion


		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(
				PathJoinSubstitution([
					FindPackageShare('frontier_exploration_ros2'),
					'launch',
					'frontier_explorer.launch.py',
				])
			),
			launch_arguments={
				'use_sim_time':    LaunchConfiguration('use_sim_time'),
				'autostart':       "True",
				'params_file':     LaunchConfiguration('frontier_explore_config_file'),
			}.items(),
			condition=IfCondition(
				PythonExpression([
					"('", use_case, "' in ['explore', 'explore-frontier']) ", 
					" and ",
					"('", mode,"' in ['simulation', 'companion'])",
				])
			),
		),

		#endregion
	
	]

	return LaunchDescription(declared_arguments + launch_actions)
