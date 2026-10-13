#!/usr/bin/env bash
# Run both local services; stop both when either exits or the user interrupts.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

if ! command -v node >/dev/null 2>&1 || [[ ! -f frontend/node_modules/vite/bin/vite.js ]] || [[ ! -x backend/.venv/bin/python ]]; then
  echo 'Dependencies are missing. Run: bash scripts/setup.sh' >&2
  exit 1
fi
if ! backend/.venv/bin/python -c 'import fastapi, uvicorn' >/dev/null 2>&1; then
  echo 'Backend dependencies are missing. Run: bash scripts/setup.sh' >&2
  exit 1
fi
backend/.venv/bin/python - <<'PY'
import socket
import sys
for port in (8000, 5173):
    with socket.socket() as connection:
        try:
            connection.bind(('127.0.0.1', port))
        except OSError:
            sys.exit(f'Port {port} is occupied. Stop its existing service before starting this checkout.')
PY

backend_pid=''
frontend_pid=''
cleanup() {
  trap - EXIT
  for service_pid in "$backend_pid" "$frontend_pid"; do
    if [[ -n "$service_pid" ]]; then
      kill "$service_pid" 2>/dev/null || true
    fi
  done
  for service_pid in "$backend_pid" "$frontend_pid"; do
    if [[ -n "$service_pid" ]]; then
      wait "$service_pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

(cd backend && exec .venv/bin/python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000) &
backend_pid=$!
(cd frontend && exec node node_modules/vite/bin/vite.js) &
frontend_pid=$!
echo 'Starting app: http://127.0.0.1:5173'
echo 'API docs: http://127.0.0.1:8000/docs'
echo 'Wait for the service startup messages. Press Ctrl-C to stop both.'

while kill -0 "$backend_pid" 2>/dev/null && kill -0 "$frontend_pid" 2>/dev/null; do
  sleep 1
done
if ! kill -0 "$backend_pid" 2>/dev/null; then
  wait "$backend_pid"
else
  wait "$frontend_pid"
fi
