---
name: create-ticket
description: Turn a brief, discussion, or bug report into a scoped engineering ticket with a clear description, acceptance criteria, dependencies, and verification. Supports local drafts and authorized GitHub, Linear, or Jira publication.
---

# Create ticket

Read the available brief, project instructions, relevant code, and existing tickets. Identify the user-visible problem, desired behavior, and ownership boundary. Clarify only missing decisions that materially affect scope; use the host's Q/A UI with recommended choices and custom answers when available. Otherwise label reasonable assumptions rather than inventing facts.

Read [the ticket template](references/ticket-template.md) when drafting. Make the ticket small enough for one coherent change and PR. If it spans independent boundaries, split it into linked tickets, each with a single owner and testable outcome; document a shared contract before parallel execution. Separate genuine dependencies from changes that can proceed with a mocked contract.

Write an action-oriented title, concrete before/after description, explicit in/out of scope, numbered observable acceptance criteria, verification commands/scenarios, dependencies, and known risks or decisions. Do not invent an assignee, priority, estimate, or project identifier. Include only implementation pointers needed to locate the change; avoid prescribing incidental details. Acceptance criteria describe outcomes, including relevant failure/default states, rather than restating implementation steps.

Draft the complete title/body before any publication. A request to draft or create a local ticket does not authorize sending it to a remote tracker. If the user explicitly asked to create an issue in a named tracker/project, publication is already authorized: use its available connector/CLI without another confirmation. Resolve an unknown tracker or target before publishing. If approval is needed, show the concrete draft first and explain that the missing authorization concerns external publication. Check for duplicates before creation, and re-check after an ambiguous timeout instead of posting twice.

Use native structured fields for GitHub/Linear/Jira. With `gh`, use `--body-file` for Markdown. If credentials or tools are missing, save a local Markdown draft in the requested path (default `docs/tickets/<slug>.md`) and report that it was not published. Return the ticket URL/key when published, or the local file path and assumptions when drafted. Do not start implementation unless requested.
