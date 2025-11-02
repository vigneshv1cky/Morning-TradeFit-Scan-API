#!/usr/bin/env bash
# Activate virtual environment and run the FastAPI app

set -euo pipefail
cd "$(dirname "$0")"

VENV_DIR="${VENV_DIR:-env_emotionalshieldai}"
APP_MODULE="${APP_MODULE:-app.main:app}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

# Create virtual environment if it does not exist
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Virtual environment not found: $VENV_DIR. Creating..."
  python3 -m venv "$VENV_DIR" || { echo "Failed to create virtual environment. Exiting."; exit 1; }
fi

# Activate venv
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# Install dependencies if needed
if [[ -f requirements.txt ]]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
fi

# Banner (uses heredoc so no need for \n)
cat <<'BANNER'

=========================================
  Morning TradeFit Scan API Launcher
=========================================

API Endpoints:
  GET    /           - API info and available endpoints
  GET    /your_psychology     - Liveness check (status, time)
  POST   /scan       - Perform a new scan (JSON body required)
  GET    /scans      - List previous scans (pagination, filter)
  GET    /scans/{id} - Get details of a specific scan
  GET    /docs       - Custom API documentation (JSON)

Interactive Swagger UI: http://127.0.0.1:8000/docs
=========================================

BANNER

echo "Starting FastAPI app on $HOST:$PORT..."
uvicorn "$APP_MODULE" --reload --host "$HOST" --port "$PORT"
# python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000