#!/bin/bash

# Definition of variables with image name and Dockerfile path
IMAGE_NAME="karlos98/sim-app-device"
DOCKERFILE_URL="https://raw.githubusercontent.com/Let-s-Code-It/SIM-App-Device/master/Dockerfile"
DOCKERFILE_PATH="Sim-App-Dockerfile"

# Check if "update" argument is passed
if [ "$1" == "update" ]; then
  echo "Building the image without cache..."
  # Build the image without using cache
  curl -o "$DOCKERFILE_PATH" "$DOCKERFILE_URL"
  docker build --no-cache -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
else
  # Check if the image exists
  if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo "Image doesn't exist. Building..."
    # Build the image
    curl -o "$DOCKERFILE_PATH" "$DOCKERFILE_URL"
    docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
  fi
fi

# Run the container
docker run --restart=always --privileged  -v ~/SIM-Data:/SIM-Data -p 8098:8098 -it "$IMAGE_NAME"