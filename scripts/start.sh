#!/usr/bin/env bash
set -euo pipefail

# Start backend (Django) and frontend (Next.js) in local dev mode.
# This does NOT use Docker. It runs the two servers in the background and
# writes logs to .logs/backend.log and .logs/frontend.log.
#
# Usage:
#   ./scripts/start.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/.logs"

mkdir -p "$LOG_DIR"

echo "[start] Using project root: $ROOT_DIR"

echo "[start] Stopping any existing local servers..."
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "next dev -p 3000" 2>/dev/null || true

echo "[start] Starting backend (Django) on :8000..."
(
  cd "$BACKEND_DIR"
  export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-dev-secret}"
  export DJANGO_API_KEY="${DJANGO_API_KEY:-dev-secret-key}"
  python3 manage.py migrate --settings=project.settings
  python3 manage.py runserver 0.0.0.0:8000 --settings=project.settings
) >>"$LOG_DIR/backend.log" 2>&1 &
BACK_PID=$!
echo "$BACK_PID" >"$LOG_DIR/backend.pid"
echo "[start] Backend PID: $BACK_PID (log: $LOG_DIR/backend.log)"

echo "[start] Starting frontend (Next.js) on :3000..."
(
  cd "$FRONTEND_DIR"
  export NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN="${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN:-http://127.0.0.1:8000}"
  export NEXT_PUBLIC_PLATFORM_API_KEY="${NEXT_PUBLIC_PLATFORM_API_KEY:-dev-secret-key}"
  # Bypass npm script to avoid shell interpreting the next CLI shim incorrectly
  node node_modules/next/dist/bin/next dev -p 3000
) >>"$LOG_DIR/frontend.log" 2>&1 &
FRONT_PID=$!
echo "$FRONT_PID" >"$LOG_DIR/frontend.pid"
echo "[start] Frontend PID: $FRONT_PID (log: $LOG_DIR/frontend.log)"

echo
echo "[start] Servers running:"
echo "  Backend:  http://localhost:8000 (PID $BACK_PID)"
echo "  Frontend: http://localhost:3000 (PID $FRONT_PID)"
echo "Use './scripts/stop.sh' to stop them."


