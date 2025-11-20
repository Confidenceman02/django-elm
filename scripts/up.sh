# Get the directory where the current script is located
CURRENT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

if [[ "$CI" == "true" ]]; then
  echo "Running in CI mode"
else
  "$CURRENT_DIR"/clipboard_service.sh start
fi

docker compose up -d
