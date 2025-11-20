#!/bin/bash
# File: clipboard_watcher.sh

# Path to the named pipe
FIFO_DIR=~/clipboard_pipe
FIFO_PIPE="${FIFO_DIR}/nvim_clipboard"

mkdir -p "$FIFO_DIR"
# Check if the FIFO pipe exists, if not create it
if [ ! -p "$FIFO_PIPE" ]; then
  mkfifo "$FIFO_PIPE"
fi
touch "${FIFO_DIR}/kick-flip.start"

# The outer loop keeps the script running indefinitely
while true; do
  # The 'cat' command will read all content from the pipe and then exit.
  # It will block here until a writer sends data.
  cat "$FIFO_PIPE" | wl-copy
  # A short delay to prevent a busy-loop
  sleep 0.1
done
