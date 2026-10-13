#!/usr/bin/env bash
# macOS: optional Homebrew prerequisites, then the shared setup/dev scripts.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:-setup}"
case "$mode" in setup|dev|install-tools) ;; *) echo 'Usage: bash scripts/macos.sh [setup|dev|install-tools]' >&2; exit 1 ;; esac
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'This entry point is for macOS. Linux/WSL: use scripts/setup.sh and scripts/dev.sh.' >&2
  exit 1
fi
# Support both Homebrew locations without modifying the user's shell profile.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
if [[ "$mode" == install-tools ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    echo 'Homebrew is missing. Install it from https://brew.sh, or use official Node/Python installers in docs/setup-guide.md.' >&2
    exit 1
  fi
  brew install node@22 python@3.13
  if ! git --version >/dev/null 2>&1; then
    brew install git
  fi
  echo 'Prerequisites installed. Next: bash scripts/macos.sh setup'
  exit 0
fi
if command -v brew >/dev/null 2>&1; then
  # Alternate-version formulae are keg-only; keep their PATH changes local.
  for formula in node@22 python@3.13; do
    if formula_prefix="$(brew --prefix "$formula" 2>/dev/null)" && [[ -d "$formula_prefix/bin" ]]; then
      export PATH="$formula_prefix/bin:$PATH"
    fi
  done
fi
exec bash "$project_dir/scripts/$mode.sh"
