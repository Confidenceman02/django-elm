#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Dynamically locate the project root directory
# (Finds the directory where this script lives, then goes up one level)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOCKET_FILE="$PROJECT_ROOT/.nvim.sock"

echo "Checking environment..."

# 2. Verify Neovim is installed in the container
if ! command -v nvim &> /dev/null; then
    echo "ERROR: Neovim is not installed in this container."
    echo "Please install it using your package manager (e.g., apt install neovim)."
    exit 1
fi

# 3. Check if a Neovim server is already running for this exact socket path
if pgrep -f "nvim --headless --listen $SOCKET_FILE" &> /dev/null; then
    echo "✓ Neovim headless server is already running for this project."
    
    # Just in case permissions got messed up, reset them
    if [ -S "$SOCKET_FILE" ]; then
        chmod 777 "$SOCKET_FILE"
    fi
    exit 0
fi

# 4. Clean up stale/dead socket files if the process crashed previously
if [ -e "$SOCKET_FILE" ] || [ -S "$SOCKET_FILE" ]; then
    echo "Found a stale socket file at project root. Cleaning up..."
    rm -f "$SOCKET_FILE"
fi

echo "Starting Neovim headless server at project root..."

# 5. Start the headless Neovim server in the background
# We run it from the PROJECT_ROOT directory so the editor working directory matches perfectly
cd "$PROJECT_ROOT"
setsid nvim --headless --listen "$SOCKET_FILE" > /tmp/nvim-server.log 2>&1 &

# 6. Wait briefly for Neovim to initialize and create the socket file
RETRIES=5
while [ ! -S "$SOCKET_FILE" ]; do
    sleep 0.2
    RETRIES=$((RETRIES - 1))
    if [ "$RETRIES" -le 0 ]; then
        echo "ERROR: Neovim failed to start or create the socket file."
        echo "Check logs at /tmp/nvim-server.log"
        exit 1
    fi
done

# 7. Ensure the host user has absolute read/write permissions to the socket
chmod 777 "$SOCKET_FILE"

echo "🚀 Neovim server is running and listening on $SOCKET_FILE"
