# Containerised ROS 2 Humble + Gazebo (Ignition) Setup Guide

A complete, reproducible guide to setting up a GPU-accelerated, GUI-capable ROS 2 Humble + Gazebo development environment inside Docker on **Ubuntu 22.04 (Jammy)** with an **NVIDIA GPU**.

This was built layer by layer, verifying each before stacking the next. If you reproduce it, follow the same order — it makes debugging tractable.

---

## Prerequisites / Target System

| Component | This setup |
|---|---|
| OS | Ubuntu 22.04.5 LTS (Jammy) |
| GPU | NVIDIA (driver 535, CUDA 12.2) |
| Display server | X11 |
| ROS 2 | Humble (via Docker image, not installed natively) |
| Gazebo | Ignition Fortress 6.16 (ships in the image) |

> The ROS install lives entirely inside a Docker container — nothing is installed natively on the host except Docker and the NVIDIA Container Toolkit.

---

## The Four Layers

The setup is four independent layers. Each was verified on its own before adding the next:

1. **Docker engine** — runs containers.
2. **NVIDIA Container Toolkit** — bridges the host GPU into containers.
3. **ROS 2 Humble image** — the ROS + Gazebo environment.
4. **Display layer (X11)** — gets GUI windows (RViz, Gazebo) onto the host screen.

Then everything is captured in a **Dockerfile + Docker Compose file** so the environment is reproducible and the long launch command never has to be retyped.

---

## Step 0 — Audit the System First

Before installing anything, confirm the starting state.

Check for any existing/residual ROS install:

```bash
apt list --installed 2>/dev/null | grep -i ros   # installed ROS apt packages
ls /opt/ros/                                      # ROS install directories
grep -i ros ~/.bashrc                             # leftover sourcing lines
ls /etc/apt/sources.list.d/ | grep -i ros         # ROS apt source
```

Confirm OS version (must be 22.04 / Jammy for Humble):

```bash
lsb_release -a
```

Confirm the foundation for the container path:

```bash
echo $XDG_SESSION_TYPE   # should be: x11
nvidia-smi               # confirms host NVIDIA driver works
docker --version         # is Docker installed?
```

> **Why `nvidia-smi` matters:** the container reuses the host's NVIDIA driver — it does not install its own. If `nvidia-smi` doesn't work on the host, nothing GPU-related downstream will work.

---

## Layer 1 — Docker Engine

If Docker is already installed (`docker --version` returns a version), verify it works:

```bash
docker run hello-world    # proves Docker can pull + run a container
groups | grep docker      # confirms your user is in the docker group
```

If `docker run hello-world` fails with a permission error, add yourself to the `docker` group:

```bash
sudo usermod -aG docker $USER
newgrp docker             # or log out and back in
```

> **Concept:** The Docker daemon runs as root. Being in the `docker` group lets you run `docker` without `sudo`. (This is effectively root-equivalent access — fine on a personal dev machine.)

---

## Layer 2 — NVIDIA Container Toolkit

This is the bridge that lets containers use the host GPU.

**Phase 1 — Add NVIDIA's apt repository + signing key:**

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

> If prompted to overwrite an existing keyring file, answer `y` — it just refreshes the key.

**Phase 2 — Install the package:**

```bash
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

**Phase 3 — Wire it into Docker (commonly forgotten):**

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

> Installing the package alone is not enough — `nvidia-ctk runtime configure` registers the NVIDIA runtime in Docker's daemon config, and the daemon must be restarted to apply it.

**Verify (the key milestone):**

```bash
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

Success = the same GPU table you saw from the host `nvidia-smi`, but generated **from inside the container**.

> **The apt-repo pattern** (seen here and with ROS): (1) fetch + dearmor a GPG key into `/usr/share/keyrings/`, (2) add a source line with `signed-by=` pointing to that key. It generalises to any third-party apt repo.

---

## Layer 3 — ROS 2 Humble Image

ROS images come in tiers of increasing size:

| Tier | Contains |
|---|---|
| `ros-core` | Bare ROS |
| `ros-base` | + build tools (colcon, rosdep) |
| `humble-desktop` | + RViz, GUI, demos |
| `humble-desktop-full` | + **Gazebo and simulation packages** |

For Gazebo-heavy work, pull `desktop-full`:

```bash
docker pull osrf/ros:humble-desktop-full
```

> This is a large image (several GB) because it bundles Gazebo. Images are stacks of cached layers; shared layers aren't re-downloaded across images.

**Verify ROS runs (headless — no display needed yet):**

```bash
docker run --rm osrf/ros:humble-desktop-full ros2 run demo_nodes_cpp talker
```

Success = it prints `Publishing: 'Hello World: 1'`, `2`, `3`... Stop with `Ctrl+C`.

---

## Layer 4 — Display (X11)

Gets GUI windows out of the container onto the host screen. Three pieces:

1. `-e DISPLAY=$DISPLAY` — tells apps which display to draw to.
2. `-v /tmp/.X11-unix:/tmp/.X11-unix:rw` — mounts the actual display channel (the X11 socket).
3. `xhost +local:root` — grants the container permission to connect (run on the **host**).

Plus a Qt fix: `-e QT_X11_NO_MITSHM=1` disables a shared-memory extension that misbehaves across the container boundary (needed for RViz and other Qt apps).

**Grant X11 access (once per host login session):**

```bash
xhost +local:root
```

**Test RViz (raw `docker run`, before Compose exists):**

```bash
docker run -it --rm \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  osrf/ros:humble-desktop-full \
  rviz2
```

Success = the RViz window opens (empty 3D grid with a left-hand panel).

**Test Gazebo (the heavier GPU case):**

```bash
docker run -it --rm \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  osrf/ros:humble-desktop-full \
  ign gazebo
```

Success = a 3D world window opens and the camera pans/rotates smoothly (smooth = GPU rendering working).

> **Note on the launch command:** this image ships the **new Gazebo (Ignition / `ign gazebo`)**, which is **Gazebo Fortress 6.16** — *not* Gazebo Classic. The command is `ign gazebo`, not `gazebo`.

---

## Gazebo Naming Reference

A common source of confusion. The same software has been renamed twice:

| Name | Launch command | Status |
|---|---|---|
| Gazebo Classic | `gazebo` | End-of-life (Jan 2025) |
| Ignition / Gazebo Fortress | `ign gazebo` | **What this image uses** (LTS, ~2028) |
| New Gazebo (latest) | `gz sim` | Current naming for newer versions |

The `ros_ign_*` package prefix in `ros2 pkg list` is the tell that you're on the Ignition-era naming.

---

## Custom Image — The Dockerfile

The raw `osrf/ros` image works, but it runs as **root**, doesn't auto-source ROS, and has no project workspace set up. Patching those at runtime (every session) doesn't stick because containers are disposable. The durable fix is a small **Dockerfile** that bakes the fixes into a custom image built *on top of* the OSRF base.

It solves four recurring papercuts at once:

1. **Auto-sources ROS** in every shell (no manual `source /opt/ros/humble/setup.bash`).
2. **Creates a named user** matching the host UID/GID, so files created in the mounted code are owned by *you*, not root (no more `EACCES: permission denied` when editing from the host, and no `I have no name!` prompt).
3. **Creates and owns the workspace** (`/ws`), so `colcon build` can write `build/`, `install/`, `log/`.
4. **Sets a sensible working directory** so shells start in the workspace.

Save as `Dockerfile` (no extension) in the repo root:

```dockerfile
FROM osrf/ros:humble-desktop-full

ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

# Create a non-root user matching the host UID/GID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Create the workspace and give it to that user
RUN mkdir -p /ws/src && chown -R $USER_UID:$USER_GID /ws

# Auto-source ROS in every shell for the new user
RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc

USER $USERNAME
WORKDIR /ws
```

> **Why the order matters:** the user-creation `RUN` steps need root, so they come *before* the `USER` directive switches to the non-root user. After `USER`, the container runs as `ros`.

> **Why the workspace is `/ws`, not `/root/ros2_ws`:** `/root` is root's home directory — a non-root user can't write there. Moving the workspace to `/ws` (owned by the `ros` user) is what lets the non-root container build and edit code.

### Find your host UID/GID

The Dockerfile defaults to 1000/1000 (the first user on a machine). Confirm yours:

```bash
id        # look for uid=NNNN and gid=NNNN
```

If they differ from 1000, pass them in via the `.env` file below.

---

## Final Step — Docker Compose File

Compose tells Docker to **build the Dockerfile** (not pull the base image directly), runs the container as your user, and captures all the runtime flags. Save as `docker-compose.yml` in the repo root.

```yaml
services:
  ros:
    build:
      context: .
      args:
        USER_UID: ${UID:-1000}
        USER_GID: ${GID:-1000}
    user: "${UID:-1000}:${GID:-1000}"
    network_mode: host
    command: sleep infinity
    environment:
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./src:/ws/src
    stdin_open: true
    tty: true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

**Key settings explained:**

| Setting | What it does |
|---|---|
| `build.context: .` + `args` | Builds the local `Dockerfile`, passing in the host UID/GID |
| `user: "${UID}:${GID}"` | Runs the container as your user (file ownership matches the host) |
| `network_mode: host` | Container shares the host network — makes ROS 2 DDS discovery work across multiple terminals |
| `command: sleep infinity` | Keeps the container alive in the background so terminals can attach to it |
| `volumes: ./src:/ws/src` | Mounts your code (in Git on the host) into the workspace; code persists on host, container stays disposable |
| `stdin_open` + `tty` | Equivalent of `-it` (interactive terminal) |
| `deploy...devices` | The `--gpus all` equivalent (GPU access) |

### The `.env` file

Compose auto-reads a `.env` file in the same directory. Put your UID/GID there so the `${UID}`/`${GID}` variables resolve:

```bash
echo "UID=$(id -u)" > .env
echo "GID=$(id -g)" >> .env
```

> **Gitignore `.env`** — it's machine-specific. The Dockerfile/Compose defaults (1000) mean the setup still works for anyone who clones without a `.env`.

---

## Daily Usage

The workflow uses **one persistent container** with **multiple terminals attached** — this is how real ROS development works, because all nodes then share one DDS network and can see each other's topics.

From the directory containing `docker-compose.yml`:

**1. Allow GUI apps (once per login session):**

```bash
xhost +local:root
```

**2. Start the environment (once per work session):**

```bash
docker compose up -d        # starts the container in the background
docker compose ps           # confirm the 'ros' service shows "running"
```

> First run (or after editing the Dockerfile) needs `docker compose up -d --build` to (re)build the image.

**3. Open as many terminals as you need — each enters the same container:**

```bash
docker compose exec ros bash
```

Inside, ROS is already sourced and you start in `/ws`. Your code is at `/ws/src`. Examples:

```bash
ign gazebo                          # launch the simulator
rviz2                               # launch RViz
ros2 run demo_nodes_cpp talker      # run a node
ros2 topic list                     # inspect topics
colcon build                        # build the workspace (run from /ws)
```

**4. Stop the environment (end of session):**

```bash
docker compose down         # stops and removes the container
```

> The container is disposable — your code is safe on the host in `src/`. Stopping it loses nothing that matters.

---

## Key Concepts to Remember

- **Image vs container:** the image is the reusable blueprint; a container is a running instance. Containers are disposable — reproducibility lives in the Dockerfile + Compose file, not in keeping a container alive.
- **Verify each layer independently** before stacking the next. Read error text precisely — `exec: gazebo: not found` is a *missing command*, not a display failure.
- **The GPU bridge** reuses the host driver; it never installs one in the container — so host `nvidia-smi` must work first.
- **GUI from a container** = `DISPLAY` + X11 socket mount + `xhost` permission (+ the Qt MITSHM fix).
- **Bind-mount your code** from the host so it lives in Git and the container stays throwaway.
- **Run the container as your host user** (via the Dockerfile + `user:`) so files it creates are owned by you, not root.
- **Source ROS in every shell** — baked into the Dockerfile here, but the underlying rule is: installing ROS ≠ activating it. `ros2: command not found` almost always means a shell that hasn't sourced.
- **`xhost +local:root`** must be re-run once per login session (e.g. after a reboot) before GUI apps will open.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `cannot connect to display` | `xhost` not run this session, or `DISPLAY`/socket missing | Re-run `xhost +local:root`; check the `-e DISPLAY` and `-v /tmp/.X11-unix` settings |
| `exec: <cmd>: not found` | Command doesn't exist in the image | Verify the executable: `docker compose exec ros bash` then `which <cmd>` |
| `ros2: command not found` | Shell hasn't sourced ROS | Should be auto-sourced by the Dockerfile; otherwise `source /opt/ros/humble/setup.bash` |
| `--gpus all` errors | NVIDIA toolkit not wired into Docker | Re-run `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker` |
| `EACCES: permission denied` editing files from host | Files owned by root (container ran as root) | Rebuild with the Dockerfile (runs as your user); one-time fix for old files: `sudo chown -R $USER:$USER src` |
| `I have no name!` prompt | Container UID has no matching user in the image | Cosmetic; the Dockerfile's named user fixes it |
| `colcon build` can't write build/install/log | Workspace dir not owned by the container user | Ensure workspace is `/ws` (created + owned in the Dockerfile), build from `/ws` |
| GUI fails after reboot | `xhost` permission resets per session | Re-run `xhost +local:root` |
| RViz crashes / renders glitchy | Qt shared-memory issue | Ensure `-e QT_X11_NO_MITSHM=1` / the `environment:` entry is set |