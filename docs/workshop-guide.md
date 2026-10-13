# 30-minute workshop

## Facilitator preparation (before the clock starts)

Use the assistant-guided process in [setup-guide.md](setup-guide.md) and the setup prompt in [agent-prompts.md](agent-prompts.md) when a participant lacks dependencies. macOS and native Windows have their own script entry points. Verify readiness before starting the clock; if setup is needed during the activity, allow catch-up time or pair the participant with a ready machine.

Install prerequisites and a participant's preferred coding agent ahead of time. No paid API is required by the application; use an already available coding-agent setup. Run the README's installation, tests, and starter preflight. Confirm each participant can open the app and see seeded tasks. Have the API contract and tickets open. Confirm GitHub authentication and write access to the participant's chosen repository/fork if creating live issues and PRs; the local application itself needs no GitHub credentials. Open two agent sessions that can use the bundled skills and independent review subagents. Keep installations, authentication, and slow host setup outside the timed exercise.

Create the exercise worktrees and install dependencies in each before the timed session when downloads are slow. In the 3–5 minute segment, explain/inspect these pre-created worktrees instead of downloading packages. For a cold setup, allow extra preparation time; installation is not included in the 20 minutes.

```bash
# From the clean, committed original repository
git worktree add -b workshop/frontend ../workshop-frontend HEAD
git worktree add -b workshop/backend ../workshop-backend HEAD
npm --prefix ../workshop-frontend/frontend install
python3.13 -m venv ../workshop-backend/backend/.venv
../workshop-backend/backend/.venv/bin/python -m pip install -r ../workshop-backend/backend/requirements.txt
git worktree list
```

The worktree commands above use Bash. On native Windows, create the worktrees with the same Git commands and run `scripts/windows.ps1 -Action Setup` in each checkout; it installs both halves and verifies them using native paths. macOS can run `bash scripts/macos.sh setup` in each checkout. Use an existing supported Python 3.11/3.12 if 3.13 is not installed.

The frontend worktree only needs npm dependencies; the backend worktree only needs its virtualenv. The original repository needs both for integration. Worktrees use separate databases by default. Avoid checking out the same branch in multiple worktrees. Default service ports are shared: run services in the original integration checkout and rely on mocks/tests in agent checkouts. A frontend POST may fail until the backend branch is merged; that is expected.

## Skill-driven outcome

Participants add a Title/Description form and task submission. They practice `$grill-me` to confirm the brief, `$create-ticket` to create two linked issues, and `$implement-ticket` to implement them in isolated worktrees with review gates and linked PRs. UI UX Pro Max is available for focused form guidance; PR babysitting is a follow-up after publication. Keep the scope to task creation, not a broader task manager redesign.

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
| 0–3 min | Use grill-me to confirm the small brief and create-ticket to create the two linked issues from the prepared documents. Agents read the shared contract. |
| 3–5 min | Create/inspect two worktrees. Assign the real issue URLs to implement-ticket and approve both concrete plans (including milestone scope if desired). |
| 5–12 min | Run implement-ticket in both sessions concurrently. Agents implement only their tickets, test their changes, and run independent security/architecture reviews. |
| 12–16 min | Agents push approved ticket branches and open linked PRs. Review diffs/evidence and combine branches in a separate integration branch. |
| 16–20 min | Run all tests/build, start both services, and verify task submission end-to-end. Record unresolved issues; never claim unverified success. |

Issue creation and PR publication require network/tool access and participant authorization. If remote hosting is blocked, retain local ticket/PR drafts and report those steps incomplete. For a strict 20-minute session, the facilitator can demonstrate grill-me/create-ticket during the conceptual segment and have the resulting issues ready for assignment. Review and approval latency varies; allow extra time rather than waiving review gates silently.

Seven minutes is the target parallel coding window; keep changes to the small form and endpoint so coding plus review stays around ten minutes. If an agent is slow, prioritize contract correctness and the stated acceptance criteria.

## Review and integration

Review both PRs before combining them. From the original repository, with a clean working tree and both committed branches available locally (fetch an approved remote branch if needed):

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
