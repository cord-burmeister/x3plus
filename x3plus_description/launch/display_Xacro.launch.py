import os

from ament_index_python.packages import (
    get_package_share_path,
get_package_share_directory,
)


from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    Command,
    PythonExpression,
    FindExecutable,
    PathJoinSubstitution,
    LaunchConfiguration,
)

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

import xacro
from launch.actions import OpaqueFunction


# evaluates LaunchConfigurations in context for use with xacro.process_file(). Returns a list of launch actions to be included in launch description
def evaluate_xacro(context, *args, **kwargs):

    mecanum = LaunchConfiguration('mecanum').perform(context)

    namespace = LaunchConfiguration('namespace').perform(context)

    # Use xacro to process the file
    # xacro_file = os.path.join(get_package_share_directory('x3plus_description'), 'urdf', 'yahboomcar_X3plus.urdf.xacro')
    xacro_file = os.path.join(get_package_share_directory('x3plus_description'), 'urdf', 'yahboomcar_X3plusX.urdf.xacro')

    #robot_description_config = xacro.process_file(xacro_file)
    robot_description_config = xacro.process_file(xacro_file, 
            mappings={  
                "mecanum": mecanum,
                "ns" : namespace
                }).toxml()

 

    robot_state_publisher_node = Node(
      package='robot_state_publisher',
      executable='robot_state_publisher',
      name='robot_state_publisher',
        output='both',
      parameters=[{
        'robot_description': robot_description_config
      }])

    return [robot_state_publisher_node]


def generate_launch_description():
    description_path = get_package_share_path('x3plus_description')
    default_rviz_config_path = description_path / 'config/x3plus_description.rviz'
   
    namespace = LaunchConfiguration("namespace")
    declare_namespace_arg = DeclareLaunchArgument(
        "namespace",
        default_value="",
        description="Namespace for all topics and tfs",
    )

    mecanum = LaunchConfiguration("mecanum")
    declare_mecanum_arg = DeclareLaunchArgument(
        "mecanum",
        default_value="True",
        description=(
            "Whether to use mecanum drive controller (otherwise diff drive controller is used)",
        ),
    )

    gui_arg = DeclareLaunchArgument(name='gui', default_value='true', choices=['true', 'false'],
                                    description='Flag to enable joint_state_publisher_gui')
    rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=str(default_rviz_config_path),
                                     description='Absolute path to rviz config file')


    # Depending on gui parameter, either launch joint_state_publisher or joint_state_publisher_gui
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui'))
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )

    return LaunchDescription([
        declare_namespace_arg,
        declare_mecanum_arg,
        gui_arg,
        rviz_arg,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        #robot_state_publisher_node,
        OpaqueFunction(function=evaluate_xacro),        
        rviz_node
    ])
