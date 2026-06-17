FROM osrf/ros:humble-desktop-full
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
RUN mkdir -p /ws/src && chown -R $USER_UID:$USER_GID /ws
RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc

# Install Gazebo Classic + TurtleBot3 packages (as root, before USER switch)
RUN apt-get update && apt-get install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-simulations \
    ros-humble-turtlebot3-gazebo \
    ros-humble-teleop-twist-keyboard \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the TurtleBot3 model for all shells
ENV TURTLEBOT3_MODEL=waffle

USER $USERNAME
WORKDIR /ws