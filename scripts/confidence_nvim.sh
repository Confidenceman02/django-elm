#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <container_name>"
  exit 1
fi

REPO_BASENAME="dot-files"
REPO_URL="git@github.com:Confidenceman02/${REPO_BASENAME}.git"

CONTAINER_NAME="$1"

# Add gitub as known host
docker exec "${CONTAINER_NAME}" /bin/bash -c "mkdir -p /root/.ssh && ssh-keyscan github.com >> /root/.ssh/known_hosts"

# Install neovim
echo ""
echo "Installing neovim..."
docker exec "${CONTAINER_NAME}" /bin/bash -c "./scripts/nvim.sh"

# Clone container
docker exec -w /root "${CONTAINER_NAME}" /bin/bash -c "git clone "${REPO_URL}" && cd ${REPO_BASENAME} && ./scripts/setup_config.sh"

# Set Codeium keys
./codeium_keys.sh "$CONTAINER_NAME"
