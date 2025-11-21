#!/bin/bash
# A simple script to start and stop the clipboard watcher for your Neovim Docker setup.
# This script only supports Wayland sessions on Linux. Consider extending the script if
# you are using an x11 session.

# Follow the instructions on the kick-flip plugin to setup your custom neovim config.
# https://github.com/Confidenceman02/dot-files/tree/master/lua/kick-flip#3-neovim-lua-code-confignvimluakick-flipinitlua

# Set the path to your watcher script

CURRENT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
WATCHER_SCRIPT="${CURRENT_DIR}/kick-flip.sh"
IS_SUPPORTED=false
OS_TYPE=$(uname -s)
START_FILE=~/clipboard_pipe/kick-flip.start

# This ensures we have a clean slate when stopping or starting.
stop() {
  echo "Stopping clipboard watcher..."
  pkill -f "$WATCHER_SCRIPT"
  echo "Watcher stopped."
  if rm "$START_FILE" 2>/dev/null; then
    echo "Cleanup complete."
  else
    echo "No start file found. Skipping cleanup."
  fi
}

# Determine OS and session type
case "$OS_TYPE" in
Linux)
  # On Linux, only Wayland is currently supported
  if [ "$XDG_SESSION_TYPE" == "wayland" ]; then
    if command -v wl-copy &>/dev/null; then
    IS_SUPPORTED=true
    echo "Linux (Wayland) session detected and wl-copy found. Clipboard watcher is supported."
    else
      echo "Error: wl-copy not found. Please install the required library (e.g., 'wl-clipboard'). Skipping watcher." >&2
      IS_SUPPORTED=true
    fi
  else
    echo "Linux session detected, but only Wayland is supported. Skipping watcher."
  fi
  ;;
Darwin)
  # On macOS, Docker works with file systems in a non native way that is incompatible with the clipboard watcher.
  IS_SUPPORTED=false
  echo "macOS detected. Clipboard watcher is not supported."
  exit 1
  ;;
*)
  echo "Unsupported operating system: $OS_TYPE"
  exit 1
  ;;
esac

# Handle start and stop commands based on the determined support
case "$1" in
start)
  if [ "$IS_SUPPORTED" = true ]; then
    echo "Stopping any running watchers..."
    stop
    echo "Starting clipboard watcher in the background..."
    nohup "$WATCHER_SCRIPT" >/dev/null 2>&1 &
    echo "Watcher started with PID: $!"
  else
    echo "Skipping watcher for unsupported session."
  fi
  ;;

stop)
  stop
  ;;

*)
  echo "Usage: $0 {start|stop}"
  exit 1
  ;;
esac

exit 0
