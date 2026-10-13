# Starter validation record

Validation attempted on 2026-10-13 in the repository setup environment.

## Passed

- Python syntax compilation for app and backend tests.
- JSON parsing for package.json and tsconfig.json.
- Static route inspection: GET, PATCH, DELETE are declared; no POST route.
- SQLite smoke check using SQL literals extracted from app.py: seed three tasks, list, toggle, reopen database to check persistence, toggle back, and delete. This does not exercise FastAPI or the frontend.
- CLAUDE.md is a real working symbolic link to AGENTS.md; staged Git mode is 120000.
- Git whitespace check and ignore rules for virtualenvs, dependencies, build output, caches, databases, and environment files.

## Blocked in this environment

The host has Python 3.14.8, no Node.js/npm, and external host resolution is unavailable (curl could not resolve nodejs.org). A backend virtualenv was created, but pip could not obtain FastAPI from the configured package source. FastAPI, Uvicorn, and pytest are unavailable.

Consequently, dependency installation, running both services, frontend tests/build, backend pytest, browser checks, and live HTTP verification could not be completed. Commands were attempted and failed due to missing tooling/dependencies. No runtime pass is claimed. Use the documented Python 3.11–3.13 and Node.js 22 prerequisites on a machine with package-registry access, then run README installation, tests, and preflight before presenting this workshop.

The npm lockfile could not be generated without npm. Direct frontend dependencies are pinned; the first successful `npm install` creates frontend/package-lock.json. Keep that lockfile and use `npm ci` in subsequent checkouts once it is committed. Python direct dependencies are pinned in requirements.txt; transitive dependencies are resolved during installation.

## Remaining facilitator verification

1. Install dependencies in the original checkout and prepared agent worktrees.
2. Run backend pytest, frontend tests, and frontend build.
3. Run both services; verify list, completion/incompletion, deletion, and persistence in the browser.
4. Confirm starter POST returns 405 and no creation form exists.
5. Complete the hands-on exercise using the guide, then verify 201/422 and creation persistence.

Application scope: local demo only. Installation/download time and configuring a coding agent are preparation activities outside the 30-minute workshop.

## Skills bundle validation

Added the five skills after starter setup. All five passed the skill-creator validator and their UI metadata parsed successfully. Fourteen offline repository tests passed for install/idempotence/conflict preservation, symlink portability, upstream hashes, PR snapshot pagination/versioning, runner arguments/retries, locking, stop conditions, and failure exit codes. The UI UX Pro Max data validator and 68 standalone upstream tests passed (39 core, 26 design-system mode, 3 stack handling). Search and design-system generation also ran successfully offline.

All 74 upstream files were initially verified byte-for-byte against commit `7246805992a42b7bba37d4cac83b01416f0c6c44`; the documented local adaptation changes only SKILL.md's script path guidance. All other upstream files remain hash-identical. `.claude/skills` is a portable relative symlink to `.agents/skills`.

The offline installer successfully copied all five skills to `/home/avenka29/dev/agentic-skills/.agents/skills`; a second install confirmed identical files without overwriting them. User-wide skill directories are outside the permitted writable roots, so global discovery still requires the user's installation command in docs/skills-guide.md. Authenticated live PR polling/agent scheduling and tracker publication were not tested: gh is unavailable in this environment and no target PR was requested. No live monitor was created. These offline checks do not validate LLM behavior, actual UI availability, or every upstream maintenance test.

Whitespace verification passed for locally authored changes. The full staged whitespace check flags existing trailing whitespace in upstream `scripts/design_system.py`; it is intentionally retained to preserve the pinned source hashes.

## Local run convenience scripts

Added `scripts/setup.sh` (dependency installation plus app tests/build) and `scripts/dev.sh` (both foreground services with shutdown cleanup and port checks). Bash syntax checks passed. Setup and start were attempted: prerequisite checks correctly reported missing Node/npm and supported Python/dependencies. The unused Python 3.14 virtualenv from the failed original setup contained only pip and was moved outside the checkout to a temporary backup, preserving it while leaving setup free to create a compatible environment.

The app is still not running in this session. Node/npm are absent, only Python 3.14 is installed, and registry host resolution still fails. Actual service startup/shutdown, port checks, frontend/backend suites, and end-to-end HTTP/UI checks remain unverified here. Run the README quick setup from a terminal with Node.js 22 LTS, Python 3.11–3.13, and registry access.

## Assistant-guided cross-platform setup

Added docs/setup-guide.md, setup routing in AGENTS.md, a participant setup prompt, macOS Homebrew-aware wrapper, native Windows PowerShell setup/start/optional WinGet installer, and .nvmrc recommending Node 22. Bash syntax checks and all 17 offline repository tests passed. The macOS tests use fake Darwin/Homebrew commands to verify platform routing, versioned-tool paths (including paths with spaces), and explicit-only host installation; they do not validate a real macOS installation. The real Linux invocation rejects the macOS wrapper correctly.

Prerequisites have since become visible in this session: Node 24.21.0/npm 11.19.0 and Python 3.13.16. Linux setup passed those checks and created a Python 3.13 virtualenv, then failed downloading FastAPI because package-host DNS still fails. No app tests/build or live service verification is claimed for that attempted setup. macOS/Homebrew installation and Windows/WinGet/PowerShell parsing/runtime/shutdown remain unverified; this session has no macOS host or PowerShell interpreter. The new guide requires assistants to report those distinctions rather than claiming readiness.
