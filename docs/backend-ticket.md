# Backend ticket: create a task

Read `AGENTS.md` and use its POST `/api/tasks` contract. Work only in `backend/`. Implement in the existing FastAPI app factory; use the existing SQLite connection and schema. No migration or new dependency is needed.

Acceptance criteria:
- POST `/api/tasks` accepts JSON title and optional description.
- Missing, empty, and whitespace-only titles return 422. Reject non-string and null titles; store a trimmed title.
- Omitted description becomes `""`; supplied description is preserved. Null/non-string descriptions return 422.
- Persist the task using parameterized SQL and return HTTP 201 with generated `id`, stored `title`, `description`, and `completed: false`.
- Caller-supplied IDs or completion cannot override the generated values.
- New tasks appear in GET and survive app restart; existing operations remain functional.
- Tests use temporary databases and cover valid creation, omitted description, validation cases, distinct generated IDs, default completion, listing, and persistence after restart.
- `(cd backend && .venv/bin/python -m pytest -q)` passes.
- Diff contains only backend files, reviewed and committed on the backend branch.

Do not build a frontend form or change shared docs. The starter has no automated assertion that POST must stay absent; the manual starter preflight becomes a creation check after implementation.
