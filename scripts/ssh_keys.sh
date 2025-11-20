#!/bin/bash

# Check if a container name was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <container_name>"
  exit 1
fi

CONTAINER_NAME=$1

# Ensure the .ssh directory exists in the container
docker exec "${CONTAINER_NAME}" mkdir -p /root/.ssh

# Set up github SSH keys
# Find the first .pub file in the ~/.ssh directory
pub_key_file=$(find ~/.ssh -name "id_*.pub" -type f | head -n 1)

if [ -z "$pub_key_file" ]; then
  echo "No public key file found in ~/.ssh directory" >&2
  exit 1
fi

priv_key_file="${pub_key_file%.pub}"
public_key=$(basename "$pub_key_file")
private_key=$(basename "$priv_key_file")

# Move over keys
docker cp "$priv_key_file" "${CONTAINER_NAME}:/root/.ssh/${private_key}"
docker cp "$pub_key_file" "${CONTAINER_NAME}:/root/.ssh/${public_key}"

# Set appropriate permissions for the SSH keys in the container
docker exec "${CONTAINER_NAME}" chmod 600 "/root/.ssh/${private_key}"
docker exec "${CONTAINER_NAME}" chmod 644 "/root/.ssh/${public_key}"

echo "GitHub SSH keys have been copied to the container '${CONTAINER_NAME}'."
