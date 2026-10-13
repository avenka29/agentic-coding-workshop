# Assistant-guided participant setup

Use this process when a participant asks “set this project up”, “it won't run”, or “install the dependencies”. Read AGENTS.md first. This is environment preparation, not the task creation exercise. Follow the process before the timed activity; if a participant arrives unprepared, help them catch up and tell the facilitator that installation/download time is additional.

## 1. Inspect before changing anything

Confirm the repository path, working directory/branch, existing changes, OS, shell, and whether the assistant's terminal is on the participant's computer or in a restricted/remote environment. Prefer commands over questions for information the environment exposes. Ask only for missing choices/access information that affects setup.

| Check | Linux / macOS / WSL | Native Windows PowerShell |
|---|---|---|
| Repository | `git rev-parse --show-toplevel` and `git status --short` | Same Git commands |
| OS and shell | `uname -s`; on Linux `cat /etc/os-release` | `[Environment]::OSVersion`; `$PSVersionTable.PSVersion` |
| Git | `git --version` | `git --version` |
| Node/npm | `node --version`; `npm --version` | `node --version`; `npm.cmd --version` |
| Python | Try `python3.13`, `python3.12`, `python3.11`, then `python3 --version` | `py -3.13 --version`, `py -3.12 --version`, `py -3.11 --version` |
| Existing environment | `backend/.venv/bin/python --version` if present | `backend\.venv\Scripts\python.exe --version` if present |

Node.js 22 is the recommended workshop version (`.nvmrc`); the scripts accept Node 22 or later. Use Python 3.13, or an existing 3.11/3.12 installation, with venv/pip. SQLite is part of Python: no database server or SQLite CLI is required. Git is needed for worktrees. GitHub CLI and tracker integrations are optional and do not block the local exercise. Use the participant's existing coding assistant; account setup is separate from app setup.

Do not infer that host runtimes are missing solely because an assistant sandbox cannot see them. Check the participant's terminal when the execution environment differs. Loading nvm in an interactive shell does not automatically update an already-running assistant; load its existing `nvm.sh` in that assistant's shell or restart the assistant from the configured terminal. Never print credentials or full environment-variable dumps.

## 2. Select the platform entry point

| Platform | Install project dependencies and verify | Start both services |
|---|---|---|
| Linux / WSL | `bash scripts/setup.sh` | `bash scripts/dev.sh` |
| macOS | `bash scripts/macos.sh setup` | `bash scripts/macos.sh dev` |
| Native Windows | `.\scripts\windows.ps1 -Action Setup` | `.\scripts\windows.ps1 -Action Dev` |

Run from the repository root. Scripts also resolve their own project directory. Setup creates a per-checkout virtualenv, installs backend requirements and frontend dependencies, and runs backend tests, frontend tests, and a frontend build. It uses `npm ci` when a lockfile exists, otherwise `npm install`. A successful first install generates `frontend/package-lock.json`; review/retain it for reproducible subsequent installs. Start runs both services in the same terminal and stops both on Ctrl-C or when one exits.

Normal Setup installs project dependencies, not operating-system tools. The separate InstallTools actions below are opt-in host changes. If the user's setup request already authorizes the needed installation and tools permit it, proceed without repeated approvals. For a permission boundary, explain the exact blocked action and provide the concrete user command; continue independent work. Do not bypass managed policy, ask for passwords, replace system Python, force-link Homebrew formulae, or globally relax PowerShell execution policy.

## 3. Resolve only missing prerequisites

### Linux / WSL: Node

If nvm is already installed, load it and use the repo's version:

```bash
# Load the participant's existing nvm installation if needed:
source "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
nvm install
nvm use
node --version
npm --version
```

If nvm is missing, use the [official nvm install instructions](https://github.com/nvm-sh/nvm#installing-and-updating). The verified installer at the time of writing is:

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
# Load directly; the user's usual shell startup file may differ:
source "$HOME/.nvm/nvm.sh"
nvm install 22
nvm use 22
```

Use these commands only in a POSIX shell; nvm-sh is not a native PowerShell command. An existing supported Node installation can be used without installing nvm.

### Linux / WSL: Python

Detect the distribution before prescribing package commands. Fedora provides parallel interpreters; [its documentation](https://developer.fedoraproject.org/tech/languages/python/multiple-pythons.html) supports installing a specific version without replacing system Python:

```bash
sudo dnf install python3.13
python3.13 --version
PYTHON_BIN=python3.13 bash scripts/setup.sh
```

For other distributions, consult their official package documentation and check available versions first. On Debian/Ubuntu, the selected interpreter may need its matching `python3.X-venv` package. Do not assume the distribution's default Python is within 3.11-3.13, install an arbitrary PPA, or use sudo pip. If a supported interpreter exists, use `PYTHON_BIN=/absolute/path/to/python bash scripts/setup.sh` rather than installing another one.

### macOS

If compatible Node/Python are already installed, just run the macOS Setup command. If Homebrew is installed and the participant wants it to install prerequisites:

```bash
bash scripts/macos.sh install-tools
bash scripts/macos.sh setup
bash scripts/macos.sh dev
```

InstallTools uses Homebrew's [node@22](https://formulae.brew.sh/formula/node@22) and [python@3.13](https://formulae.brew.sh/formula/python@3.13) packages. The wrapper locates Homebrew on Apple Silicon or Intel and exposes its versioned tools only to the script; it does not overwrite shell profiles or force-link packages. Homebrew may prompt for its own prerequisites; let the participant handle any host authorization.

If Homebrew is missing, use the [official Homebrew instructions](https://brew.sh) if the participant chooses it, or the official [Node.js](https://nodejs.org/en/download) and [Python 3.13](https://www.python.org/downloads/release/python-31316/) installers. Check the appropriate architecture. The script does not install Homebrew itself. Git must also be available before workshop worktrees are created.

### Native Windows

Open PowerShell in the checkout. The native script avoids virtualenv activation and calls `npm.cmd`, so running npm does not require permitting npm.ps1.

If prerequisites are missing and WinGet is available:

```powershell
.\scripts\windows.ps1 -Action InstallTools
# Close and reopen PowerShell to refresh PATH, then:
.\scripts\windows.ps1 -Action Setup
.\scripts\windows.ps1 -Action Dev
```

InstallTools installs missing Node (`OpenJS.NodeJS.22`), Python (`Python.Python.3.13`), and Git (`Git.Git`) using exact [WinGet IDs](https://learn.microsoft.com/en-us/windows/package-manager/winget/install). Package installers can require elevation; the participant handles that prompt. The script does not suppress license prompts or silently enable WSL. If WinGet is absent, use the official Node/Python/Git installers instead. Select an existing Python explicitly with `-PythonBin 'C:\path\to\python.exe'`.

If execution of this local script is blocked, inspect the exact error and `Get-ExecutionPolicy -List`. Follow the participant's policy. Where permitted, `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` changes only the current shell. Download-marked files may require unblocking the specific trusted script; do not globally enable Unrestricted or defeat organization policy. WSL users run the Linux path entirely inside WSL instead of mixing Windows and Linux tools.

Git symlinks matter for CLAUDE.md and skill discovery. A native Windows clone needs symlink support (typically Developer Mode or the appropriate privilege) and Git's `core.symlinks` enabled. If links materialized as plain text, guide the participant to a fresh symlink-capable clone or a WSL checkout; don't reset their existing work. Codex can still read AGENTS.md and `.agents/skills` directly, and the app can run independently of Claude's symlinks. Virtualenvs/node_modules must not be shared between native Windows and WSL.

## 4. Troubleshoot from the first failing step

| Symptom | Assistant action |
|---|---|
| Tool installed but “command not found” | Check PATH/current shell; load existing nvm or reopen the terminal. On Windows try the Python launcher. Re-check from the assistant's actual terminal. |
| Existing .venv incompatible/incomplete or copied across OS/worktrees | Preserve it; explain the problem and move it to a named location outside the repository if authorized. Create a fresh environment with the chosen interpreter. Never silently delete it. |
| No pip or ensurepip/venv failure | Check the selected interpreter's venv support. Install its distro-supported venv/pip support or choose the official supported runtime; use the venv's Python for pip. |
| DNS/network/proxy failure | Check connectivity to npm/PyPI from the same terminal. Distinguish sandbox denial from host connectivity. Do not change DNS, certificates, proxy settings, or disable TLS to make installation pass. Provide the exact failed step for the user/facilitator. |
| npm ci lock mismatch | Inspect package.json/lockfile and user changes. Reconcile intentionally with npm install if appropriate, then review the lock diff; never delete the lockfile automatically. |
| Package install/build/test failure | Record command and error; correct the specific prerequisite or code defect within setup scope. Do not silently upgrade all dependencies, run audit --force, or skip checks to claim readiness. |
| Ports 5173/8000 occupied | Identify the existing process and ask its owner to stop it, or reuse the correctly running checkout. Never kill an unknown process. |
| Frontend opens but API fails | Confirm backend startup and GET /api/tasks on port 8000, then through Vite on 5173. Inspect logs and the existing proxy. |
| Test suite unavailable | Report unverified, not passed. Return a concrete command the participant can run and continue any independent checks. |

Retry only after correcting something. If the same failure recurs twice, report the blocker and exact human next step instead of spending the workshop on an automated retry loop. Slow downloads or managed installations go to the facilitator; participants may pair on a machine already verified ready. No external service, paid API, or Docker is required by the app.

## 5. Verify readiness, then hand off

Start both services and wait for their startup messages. Check:

- http://127.0.0.1:5173 renders the task list.
- GET http://127.0.0.1:8000/api/tasks and the proxied http://127.0.0.1:5173/api/tasks return 200 task arrays.
- Backend tests, frontend tests, and build passed in this checkout; test databases are temporary.
- Completion/incompletion persists across a reload; return the demo task to its original state.
- Deletion works. Use a fresh scratch database for destructive demo checks, preserving any participant tasks. Set TASKS_DB to a new SQLite path outside the checkout before starting services; stop and return to the normal database afterward.
- Before the exercise, POST /api/tasks returns 405 and the UI has no creation form. After implementation, use the workshop guide's 201/422 checks instead; do not undo participant code to satisfy the starter preflight.
- Git worktrees are available and each agent worktree has its own dependencies. Linux/macOS use `<worktree>/backend/.venv/bin/python`; Windows uses `<worktree>\backend\.venv\Scripts\python.exe`.

Report a compact handoff: platform/shell, runtime versions, checkout/branch, installed dependencies, actual check results, app/API URLs, start/stop command, and remaining blockers. Say **Ready** only when all required checks actually passed; otherwise **Partially ready** or **Blocked** with the next action. A generated script or a successful syntax check is not evidence of running services.

Keep the task creation feature absent during setup. Preserve unrelated changes and databases. Do not commit generated files/dependencies, publish, or push as part of setup unless instructed.
