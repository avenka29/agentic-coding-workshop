# 30-minute workshop

## Facilitator preparation (before the clock starts)

Install prerequisites and a participant's preferred coding agent ahead of time. No paid API is required by the application; use an already available coding-agent setup. Run the README's installation, tests, and starter preflight. Confirm each participant can open the app and see seeded tasks. Have the API contract and tickets open.

Create the exercise worktrees and install dependencies in each before the timed session when downloads are slow. In the 3–5 minute segment, explain/inspect these pre-created worktrees instead of downloading packages. For a cold setup, allow extra preparation time; installation is not included in the 20 minutes.

```bash
# From the clean, committed original repository
git worktree add -b workshop/frontend ../workshop-frontend HEAD
git worktree add -b workshop/backend ../workshop-backend HEAD
npm --prefix ../workshop-frontend/frontend install
python3 -m venv ../workshop-backend/backend/.venv
../workshop-backend/backend/.venv/bin/python -m pip install -r ../workshop-backend/backend/requirements.txt
git worktree list
```

The frontend worktree only needs npm dependencies; the backend worktree only needs its virtualenv. The original repository needs both for integration. Worktrees use separate databases by default. Avoid checking out the same branch in multiple worktrees. Default service ports are shared: run services in the original integration checkout and rely on mocks/tests in agent checkouts. A frontend POST may fail until the backend branch is merged; that is expected.

## Conceptual presentation: 10 minutes

| Time | Topic |
|---|---|
| 0–2 | Coding agents: assign an outcome, bounded scope, and verification criteria |
| 2–4 | Decompose task creation into frontend/backend tickets; agree on the contract first |
| 4–6 | Worktrees: separate files/branches/dependencies with shared Git history |
| 6–8 | Context engineering: canonical AGENTS.md, CLAUDE.md symlink, ownership and constraints |
| 8–10 | Human review: agent reports are evidence to check; integrate, test, then inspect the app |

Show the starter app and explain that no creation endpoint or form exists. Use the two tickets as the decomposition example. Participants supervise two independent agent sessions; the app itself does not require an agent framework.

## Hands-on: 20 minutes

| Time | Activity |
|---|---|
| 0–3 min | Read tickets and AGENTS.md's API contract. Agree on title trimming, optional description, 201 response, and 422 failures. |
| 3–5 min | Create the two worktrees with the commands above (or inspect prepared ones). Check branch/path and installed dependencies. |
| 5–12 min | Start both agent sessions simultaneously using docs/agent-prompts.md. Check ownership and answer scope questions. |
| 12–16 min | Read diffs and check test reports. Ensure both branches contain commits. Merge into the original checkout. |
| 16–20 min | Run all tests/build, start both services, and test creation end-to-end. |

Seven minutes is the target parallel coding window; keep changes to the small form and endpoint so coding plus review stays around ten minutes. If an agent is slow, prioritize contract correctness and the stated acceptance criteria.

## Review and integration

From the original repository, with a clean working tree:

```bash
git diff HEAD...workshop/frontend --stat
git diff HEAD...workshop/frontend -- frontend
git diff HEAD...workshop/backend --stat
git diff HEAD...workshop/backend -- backend
git switch -c workshop/integration
git merge --no-edit workshop/backend
git merge --no-edit workshop/frontend
(cd backend && .venv/bin/python -m pytest -q)
npm --prefix frontend test
npm --prefix frontend run build
```

The starting HEAD must still be the starter when inspecting these diffs. Check full file lists for out-of-scope changes. Merge order does not matter because ownership is disjoint. If conflicts occur, inspect the overlapping changes and resolve with the participants; don't discard work. Each agent must commit before merging—uncommitted worktree edits do not appear in branch merges.

## End-to-end verification

Start the backend and frontend using README commands. In the browser:
1. Create a task with title and description; it appears once, incomplete, and inputs clear.
2. Create with only a title; description is empty.
3. Submit a blank/whitespace title; visible feedback, no task created.
4. Toggle the new task, reload, and confirm the state persists.
5. Stop/restart the backend; confirm the new task remains.
6. Delete a task and reload; it stays deleted.
7. Stop the backend and submit a task; the UI shows failure and preserves input for retry.

Confirm server validation too (browser validation cannot prove it):

```bash
curl -i -X POST http://127.0.0.1:8000/api/tasks -H 'Content-Type: application/json' -d '{"title":"Finish homework","description":"Complete physics assignment"}'
curl -i -X POST http://127.0.0.1:8000/api/tasks -H 'Content-Type: application/json' -d '{"title":"   "}'
```

Expect 201 for the first request and 422 for the second. Stop the services when finished. Keep branches/worktrees for review; remove them only after confirming all work is committed and integrated. Do not push without approval.
