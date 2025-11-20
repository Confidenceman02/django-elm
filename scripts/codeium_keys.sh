#!/usr/bin/env bash

set -euo pipefail

if [ -z "$1" ]; then
  echo "Usage: $0 <container>" >&2
  exit 1
fi

CONTAINER_NAME="$1"
CODEIUM_CONFIG_PATH=$(find ~ -type f -path "*/.codeium/config.json" 2>/dev/null | head -n 1)

if [ -z "${CODEIUM_CONFIG_PATH}" ]; then
  echo ""
  echo "Error: codeium config file not found." >&2
  exit 1
fi

echo "Found codeium config file: ${CODEIUM_CONFIG_PATH}"

# Make sure the config path exists in the docker container
if ! docker exec "${CONTAINER_NAME}" mkdir -p /root/.codeium; then
  echo ""
  echo "Error: Failed to create directory in container." >&2
  exit 1
fi

# Copy the codeium config with docker and insert into target container
if docker cp "${CODEIUM_CONFIG_PATH}" "${CONTAINER_NAME}:/root/.codeium"; then
  echo ""
  echo "Done!"
else
  echo ""
  echo "Error: Failed to copy config to container." >&2
  exit 1
fi
