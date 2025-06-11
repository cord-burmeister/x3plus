import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        ExecuteProcess(
            cmd=["plotjuggler", "--nosplash --layout", os.path.join(get_package_share_directory('x3plus_monitor'), "config",  "imu_data.xml")],
            output="screen"
        )
    ])
