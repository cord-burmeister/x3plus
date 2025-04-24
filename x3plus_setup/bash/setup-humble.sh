#!/bin/bash

# Make sure you have a locale which supports UTF-8. If you are in a minimal 
# environment (such as a docker container), the locale may be something minimal
#  like POSIX. We test with the following settings. However, it should be fine 
# if you’re using a different UTF-8 supported locale.
locale  # check for UTF-8
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
locale  # verify settings

# First ensure that the Ubuntu Universe repository is enabled.
sudo apt install software-properties-common -y
sudo add-apt-repository universe -y

# Now add the ROS 2 GPG key with apt.
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Then add the repository to your sources list.
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Update your apt repository caches after setting up the repositories.
sudo apt update -y

# ROS 2 packages are built on frequently updated Ubuntu systems. It is always 
# recommended that you ensure your system is up to date before installing new packages.
sudo apt upgrade -y

# Desktop Install (Recommended): ROS, RViz, demos, tutorials.
sudo apt install ros-humble-desktop -y

# Development tools: Compilers and other tools to build ROS packages
sudo apt install ros-dev-tools -y

# Replace ".bash" with your shell if you're not using bash
# Possible values are: setup.bash, setup.sh, setup.zsh
source /opt/ros/humble/setup.bash

 # Add sourcing to your shell startup script
echo "source /opt/ros/humble/setup.bash" >> /home/$USER/.bashrc

# Installing VS Code 
# sudo snap install --classic code -y