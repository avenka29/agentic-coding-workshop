# Example agent prompts

Use the skills explicitly: the workshop is about applying them to a small task creation feature. In Codex use `$skill-name`; in clients with another invocation syntax select the same skill, or ask the assistant to read its SKILL.md. Replace `OWNER/REPO` and issue/PR placeholders with your own authorized repository and real URLs. Do not paste placeholder references as if they were existing issues.

## Setup assistant (before the timed exercise)

> Read AGENTS.md and docs/setup-guide.md. Inspect my OS, shell, checkout, and installed tools. Use the matching scripts to set up both frontend and backend and start both services. Install prerequisites where already authorized and permitted. Preserve environments, databases, and changes. Run tests/build and verify starter behavior. Keep task creation unimplemented. Check that the workshop skills are discoverable. Report actual readiness, URLs, versions, and start/stop commands; give concrete user commands for blocked steps. Do not push.

## Clarify the task creation experience

> Use $grill-me. We want people to add a task by entering a title and optional description, submitting it, and seeing it in the list. Read the existing brief in AGENTS.md. I may be nontechnical: ask about what the user should experience, recommend sensible choices, and keep implementation detail with the agents unless I ask about it. Use the question UI with choices and custom answers when available. Keep scope small and confirm the final brief. Don't implement yet.

## Create the two issues

> Use $create-ticket. In OWNER/REPO, create two linked GitHub issues for the agreed task creation feature, based on docs/frontend-ticket.md and docs/backend-ticket.md. Include description, scope, acceptance criteria, verification, and the shared API contract from AGENTS.md. Frontend owns only frontend/; backend owns only backend/. Check for existing matching issues before publishing. You may publish these issues to that repository. Return both URLs. Don't implement yet.

If publication is unavailable, ask for local drafts and record the limitation. Ensure the participant actually owns/can write to the target; other participants can use their own forks.

## Frontend agent (workshop-frontend directory)

> Use $implement-ticket for FRONTEND_ISSUE_URL. Read AGENTS.md and docs/frontend-ticket.md. Propose a short milestone plan for approval, then work only in frontend/ in this assigned worktree/branch. Build the title/description form, validation, POST submission, list update, loading, and error/retry states using the shared contract. Test with mocked backend responses until integration. Run frontend tests and build. Use $ui-ux-pro-max for a focused form accessibility check if helpful, keeping the existing React/CSS design. Run the independent security and architecture review gates before publication. You may commit, push this ticket branch to OWNER/REPO, and open a PR linking the issue after the gates pass. Do not merge. Report the PR URL, checks, and limitations.

## Backend agent (workshop-backend directory)

> Use $implement-ticket for BACKEND_ISSUE_URL. Read AGENTS.md and docs/backend-ticket.md. Propose a short milestone plan for approval, then work only in backend/ in this assigned worktree/branch. Implement POST /api/tasks exactly as contracted and write tests using temporary SQLite databases for validation, defaults, IDs, listing, and persistence. Run backend tests. Run the independent security and architecture review gates before publication. You may commit, push this ticket branch to OWNER/REPO, and open a PR linking the issue after the gates pass. Do not merge. Report the PR URL, checks, and limitations.

The participant can approve both concrete plans together and explicitly preapprove their listed milestones, or review each milestone separately. A delegated agent reports gates to its main agent. Keep both sessions active concurrently. The publication permission above is intentional; omit it if you want local-only work, in which case expect local commits and reviewable PR drafts rather than live PRs.

## Integration review (original repository)

> Review FRONTEND_PR_URL and BACKEND_PR_URL and their checks. Confirm ownership boundaries and the AGENTS.md contract. Combine their committed branches in a separate integration branch/worktree, preserving the starter branch. Run backend tests, frontend tests, and the build. Start both services and verify successful form submission, missing description, blank-title rejection, network failure/retry, completion, deletion, and persistence end-to-end. Do not merge remote PRs or push the integration branch without my instruction. Report evidence and unresolved problems.

## PR follow-up (outside the timed exercise)

> Use $pr-babysitter for PR_URL every 15 minutes. Verify the scheduler or agent runner is available before claiming monitoring is active. Triage feedback into defer with reasons, bounded AI fixes, and human decisions. You may push in-scope fixes to this PR branch and reply to relevant feedback. Keep significant fixes behind the skill's review gates. Do not merge. Report the monitor's identity/status or the concrete setup blocker.
