#!/usr/bin/env bash
set -euo pipefail

# Stop backend + frontend whether they are running via docker-compose
# or via local dev servers.
# Usage: ./scripts/stop.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[stop] Using project root: $ROOT_DIR"

if command -v docker >/dev/null 2>&1; then
  if docker ps >/dev/null 2>&1; then
    echo "[stop] Deteniendo contenedores docker-compose..."
    docker compose down || true
  fi
else
  echo "[stop] Docker CLI no encontrado, omitiendo docker compose."
fi

echo "[stop] Matando posibles servidores locales (Django/Next)..."
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "node .*next dev" 2>/dev/null || true

echo "[stop] Listo."


