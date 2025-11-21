#!/bin/bash

NVIM_VERSION=v0.11.2

echo "Installing neovim dependencies..."
apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  ninja-build \
  ripgrep \
  gettext \
  cmake \
  unzip && \
  apt-get clean && rm -rf /var/lib/apt/lists/*;

# Clone and build Neovim
echo ""
echo "Cloning Neovim version ${NVIM_VERSION}..."
git clone --branch ${NVIM_VERSION} https://github.com/neovim/neovim.git /tmp/neovim && \
  cd /tmp/neovim && \
  echo "Building Neovim..." && \
  make CMAKE_BUILD_TYPE=RelWithDebInfo && \
  make install && \
  rm -rf /tmp/neovim;

echo "Neovim installation complete!"
