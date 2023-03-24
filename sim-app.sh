#!/bin/bash

# Definition of variables with image name and Dockerfile path
IMAGE_NAME="karlos98/sim-app-device"
DOCKERFILE_URL="https://raw.githubusercontent.com/Let-s-Code-It/SIM-App-Device/master/Dockerfile"
DOCKERFILE_PATH="$(mktemp --suffix=-Sim-App-Dockerfile)"
SH_FILE_PATH="https://raw.githubusercontent.com/Let-s-Code-It/SIM-App-Device/master/sim-app.sh"

function check_container_running {
  # Check if a container with the image name is already running
  if docker ps -f "ancestor=$IMAGE_NAME" | grep -q "$IMAGE_NAME"; then
    echo "Container is already running."
    return 0
  else
    return 1
  fi
}

function stop_container {
  echo "Stopping the container..."
  docker stop $(docker ps -q --filter ancestor="$IMAGE_NAME")
}

function start_container {
  # Check if the image exists
  if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo "Image doesn't exist. Building..."
    # Build the image
    curl -o "$DOCKERFILE_PATH" "$DOCKERFILE_URL"
    docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
  fi

  if [ -e ~/".sim-env" ]; then
    env="--env-file $(readlink -f ~/.sim-env)"
    echo "Found .sim-env file in home directory."
  else
    env=""
  fi

  # Run the container in detached mode
  docker run --network=host $env -v /etc/localtime:/etc/localtime:ro --restart=always --privileged -v ~/SIM-Data:/SIM-Data -p 8098:8098 -d "$IMAGE_NAME"
}

function update_container {
  if check_container_running; then
    read -p "The container is already running. Do you want to stop it? (yes or no): " choice
    case "$choice" in
      y|Y|yes|YES )
        stop_container
        ;;
      * )
        echo "Aborting update."
        return 1
        ;;
    esac
  fi

  echo "Building the image without cache..."
  # Build the image without using cache
  curl -o "$DOCKERFILE_PATH" "$DOCKERFILE_URL"
  docker build --no-cache -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .

  start_container
}

function check_new_sh_file_version {
  new_version=$(curl -s "$SH_FILE_PATH" | md5sum)
  current_version=$(cat $0 | md5sum)

  if [ "$new_version" != "$current_version" ]; then
    #new .sh file version available!
    echo "Current sh: $current_version"
    echo "New sh: $new_version"
    return 0
  else
    return 1
  fi
}

function upgrade_sh {
  if check_new_sh_file_version; then
    if [ -w "$0" ]; then
        curl -o "$0" "$SH_FILE_PATH"
        echo -e "\033[0;33mA new version has been saved at: $0 \033[0m"
        exit 1
    else
        echo -e "\033[0;31mYou do not have permission to modify the file: $0"
        echo "Try running the command as administrator. Use the sudo command:"
        echo -e "sudo $0 upgrade"
        exit 1
    fi
  else
    echo "The sim-app.sh launcher version is up to date"
  fi
}

# Check arguments
case "$1" in
  start )
    if check_container_running; then
      echo "Container is already running."
    else
      start_container
    fi
    ;;
  stop )
    if check_container_running; then
      stop_container
    else
      echo "Container is already stopped."
    fi
    ;;
  update )
    update_container
    ;;
  upgrade )
    upgrade_sh
    ;;
  status )
    if check_container_running; then
      echo "Container is running."
    else
      echo "Container is stopped."
    fi
    ;;
  * )
    echo -e "\033[0;34mUsage: $0 {start|stop|update|upgrade|status}\033[0m"
    ;;
esac

#check new sh file version
if check_new_sh_file_version; then
  echo -e "\033[0;33mINFO: A new version of sim-app.sh has been detected on github"
  echo -e "INFO: use the command with the 'upgrade' argument to upgrade the sh file\033[0m"
fi