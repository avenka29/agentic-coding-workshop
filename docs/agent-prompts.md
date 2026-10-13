# Example agent prompts

Run each prompt in a separate coding-agent session rooted in the specified worktree. Participants can use any coding agent they already have installed; configuring an agent account is not part of this exercise.

## Setup assistant (before the timed exercise)

> Read AGENTS.md and docs/setup-guide.md. Inspect my OS, shell, checkout, and installed tools. Set up the app using the matching platform scripts; install prerequisites where already authorized and permitted. Preserve existing environments, databases, and changes. Run tests/build, start both services, and verify starter behavior through the API and browser. Keep task creation unimplemented. Report actual readiness, URLs, versions, and start/stop commands. If a step is blocked, explain why and give me a concrete command instead of claiming success. Do not push.

## Frontend agent (workshop-frontend directory)

> Read AGENTS.md and docs/frontend-ticket.md. Implement that ticket, modifying only frontend/ files. Follow the documented POST /api/tasks contract independently of the backend agent. Add focused mocked component tests for validation, success, pending state, and failure. Run frontend tests and build. Review your diff for scope and commit your changes locally with a descriptive message. Do not push. Report changed files, checks, and any limitations.

## Backend agent (workshop-backend directory)

> Read AGENTS.md and docs/backend-ticket.md. Implement that ticket, modifying only backend/ files. Follow the documented POST /api/tasks contract independently of the frontend agent. Use temporary SQLite databases in tests and test request validation, defaults, IDs, and persistence. Run backend tests. Review your diff for scope and commit your changes locally with a descriptive message. Do not push. Report changed files, checks, and any limitations.

## Integration review (original repository)

> Review the two committed workshop branches and their test results. Confirm each agent stayed within its ownership boundary and both implementations match AGENTS.md. Merge both branches into the integration branch, run backend tests, frontend tests, and the frontend build. Start both services and verify task creation, validation, completion, deletion, and persistence end-to-end. Keep task creation changes; do not revert to the starter. Do not push. Report evidence and any unresolved problems.
