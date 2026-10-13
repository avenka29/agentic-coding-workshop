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
