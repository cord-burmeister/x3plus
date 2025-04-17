# X3plus

Starting a new robot project. Using one repository for all packages.

## Prerequisites

* Installed ROS 2 humble distribution
* Installed gazebo harmonic distribution
* Setting *export GZ_VERSION=harmonic* (best in bashrc) to define target gazebo version

## Installation via bash script

``` bash
wget -O x3plus_ws.repos https://raw.githubusercontent.com/cord-burmeister/x3plus/main/x3plus.repos
```

## Manual Installation

First install required development tools

``` bash
sudo apt install python3-vcstool python3-colcon-common-extensions git wget
```

Then create a new workspace and load the git repositories which are required.

``` bash
mkdir -p ~/x3plus_ws/src
cd ~/x3plus_ws/src
wget -O x3plus_ws.repos https://raw.githubusercontent.com/cord-burmeister/x3plus/main/x3plus.repos
vcs import < x3plus_ws.repos
```

### Install dependencies

``` bash
cd ~/x3plus_ws
source /opt/ros/$ROS_DISTRO/setup.bash
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -i -y --rosdistro $ROS_DISTRO
```

### Build the project

``` bash
colcon build 
```

### Source the workspace

``` bash
. ~/x3plus_ws/install/setup.sh
```


## Starting commands

### Display XACRO robot description

There is a launch file which is starting the **RViz2** application to view the URDF model.

``` bash
ros2 launch x3plus_description display_Xacro.launch.py
```

### Adding keyboard teleoperation

One of the first possibilities to control a definitions of a robot is to operate it remotely with a teleoperation. There is a package which converts console input into twist messages. Note that the command with the default topic will be mapped to the robot topic.

``` bash
ros2 run  teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=master3_drive/cmd_vel
```

### Adding tele-operation with X-Box One S pad

``` bash
ros2 launch x3plus_teleop joystick_xbox.launch.py 
```

## Packages

| Name | Description |
|------|-------------|
| x3plus_setup | This is an empty ROS package which contains some installation scripts to setup the workspace |
| x3plus_description | The URDF and XACRO description of the robot |
