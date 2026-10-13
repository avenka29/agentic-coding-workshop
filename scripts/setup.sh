#!/usr/bin/env bash
# Install and verify the starter using already installed local runtimes.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

missing=0
if ! command -v git >/dev/null 2>&1; then
  echo 'Install Git for the workshop worktrees; see docs/setup-guide.md.' >&2
  missing=1
fi
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo 'Install Node.js 22 LTS (including npm), then rerun this script.' >&2
  missing=1
elif ! node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)'; then
  echo 'Use Node.js 22 or later (22 LTS recommended).' >&2
  missing=1
fi

workshop_python="${PYTHON_BIN:-}"
if [[ -z "$workshop_python" ]]; then
  for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)' 2>/dev/null; then
      workshop_python="$candidate"
      break
    fi
  done
fi
if [[ -z "$workshop_python" ]] || ! "$workshop_python" -c 'import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)' 2>/dev/null; then
  echo 'Install Python 3.11–3.13 with venv/pip. Optionally select it with PYTHON_BIN=/path/to/python.' >&2
  missing=1
fi
if [[ "$missing" -ne 0 ]]; then
  echo 'Assistant-guided setup process: docs/setup-guide.md' >&2
  exit 1
fi

if [[ -e backend/.venv ]]; then
  if [[ ! -x backend/.venv/bin/python ]] || ! backend/.venv/bin/python -c 'import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)' 2>/dev/null; then
    echo 'Existing backend/.venv is incompatible. Move it aside before rerunning; it has been preserved.' >&2
    exit 1
  fi
else
  "$workshop_python" -m venv backend/.venv
fi
backend/.venv/bin/python -m pip install -r backend/requirements.txt
if [[ -f frontend/package-lock.json ]]; then
  npm --prefix frontend ci
else
  npm --prefix frontend install
fi
(cd backend && .venv/bin/python -m pytest -q)
npm --prefix frontend test
npm --prefix frontend run build

echo 'Setup and checks passed. Start both services with: bash scripts/dev.sh'
