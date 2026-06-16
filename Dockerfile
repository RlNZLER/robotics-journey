FROM osrf/ros:humble-desktop-full

ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN mkdir -p /ws/src && chown -R $USER_UID:$USER_GID /ws

RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc

USER $USERNAME
WORKDIR /ws