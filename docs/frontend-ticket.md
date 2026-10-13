# Frontend ticket: create a task

Read `AGENTS.md` and use its POST `/api/tasks` contract. Work only in `frontend/`. The backend agent is implementing the endpoint independently; use mocked HTTP responses for frontend tests until integration.

Build a small form with labelled Title and Description fields. Title is required and must contain non-whitespace text; send a trimmed title. Description is optional and defaults to an empty string. Submit JSON to `/api/tasks` and accept the HTTP 201 task object. Append that returned task to the list or refetch after success. Clear the form only on success. Preserve entered values on failure.

Acceptance criteria:
- Accessible title input, description field, and submit button.
- Empty/whitespace title prevented with visible validation feedback.
- Pending submit is visible and prevents duplicate submissions.
- Server/network failures are visible and allow retry without losing input.
- Successful creation shows the returned task with unchecked completion state.
- Existing list, toggle, and delete behavior still works.
- Tests cover validation, successful submission, loading, and failure; use mocked POST responses.
- `npm --prefix frontend test` and `npm --prefix frontend run build` pass.
- Diff contains only frontend files, reviewed and committed on the frontend branch.

Do not implement backend code or change the shared API contract. Keep the form and API helper small; no new library is needed.
