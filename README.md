# Agentic Coding Workshop

A small task manager for practicing two coding agents in separate Git worktrees. The 30-minute workshop has a 10-minute presentation and a 20-minute exercise. Listing, completion toggles, deletion, and SQLite persistence are implemented. **Task creation is intentionally not implemented.**

## Install before the workshop
Requires Git, Node.js 22 LTS/npm, and Python 3.11–3.13 with pip/venv. Internet access is needed only to install dependencies. No Docker, paid APIs, database server, or API keys. Use Bash commands below (Windows users can use WSL).

```bash
cd agentic-coding-workshop
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm --prefix frontend install
```

## Run (two terminals)

```bash
cd backend
.venv/bin/python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

```bash
# From repository root in a second terminal
npm --prefix frontend run dev
```

Open http://127.0.0.1:5173. Vite proxies `/api` to port 8000; both services must run. API documentation is at http://127.0.0.1:8000/docs. Three example tasks appear on first startup. Toggle checkboxes and use Delete; changes persist across backend restarts. Once all tasks are deleted, the database stays empty. For fresh demo data, stop the backend and choose a new database path, e.g. `TASKS_DB=/tmp/workshop-demo.sqlite3 .venv/bin/python -m uvicorn app:app --port 8000` (use a path that does not already exist).

## Test

```bash
(cd backend && .venv/bin/python -m pytest -q)
npm --prefix frontend test
npm --prefix frontend run build
```

Backend tests cover seed data, listing, completion, persistence, deletion, empty database restart, missing IDs, and invalid updates. Frontend component tests cover listing, toggle/delete interactions, loading, retry, and failed deletion.

Starter preflight (before participants implement creation):

```bash
curl -i http://127.0.0.1:8000/api/tasks
curl -i -X POST http://127.0.0.1:8000/api/tasks -H 'Content-Type: application/json' -d '{"title":"Should not be created"}'
```

GET should return 200 and POST should return **405 Method Not Allowed**. There is no creation form. After the exercise, POST should return 201 instead.

## Workshop materials

- [Workshop guide](docs/workshop-guide.md): presentation, timed exercise, worktrees, integration
- [Frontend ticket](docs/frontend-ticket.md) and [backend ticket](docs/backend-ticket.md)
- [Agent prompts](docs/agent-prompts.md)
- [AGENTS.md](AGENTS.md): canonical context and API contract; `CLAUDE.md` links to it
- [Validation record](docs/validation.md): checks performed and setup limitations

Each worktree needs its own installed dependencies and database. Preinstall them before the timed exercise using the guide's preparation steps. This demo is for local development; Vite's proxy is a development facility, and deployment/authentication are outside the workshop.

## Optional coding skills

Five reusable skills are bundled: `grill-me`, `create-ticket`, `implement-ticket`, `pr-babysitter`, and `ui-ux-pro-max`. Read the [skills setup and usage guide](docs/skills-guide.md) for local installation, example prompts, approval gates, and PR monitoring. They do not change the starter app or implement task creation.
