---
name: grill-me
description: Clarify an idea or brief through iterative questions, tradeoffs, and recommendations until the user confirms shared understanding. Use when asked to grill, interview, or pressure-test requirements.
---

# Grill me

Read supplied context and relevant project files before asking questions. Identify the outcome, users, constraints, scope, success criteria, and consequential unknowns. Challenge contradictions and unsupported assumptions without turning the interview into a generic questionnaire.

## Question loop

- Always use the host's question/answer UI when a suitable tool is available in the active mode. Never call a plan-only question tool outside Plan mode. Prefer multiple choice: 2–3 distinct choices, the recommended option first and marked `(Recommended)`, plus a short rationale/tradeoff. Preserve the UI's built-in custom/free-text answer option; do not add a duplicate Other option. If the UI has no custom-answer support, explicitly allow a custom response.
- If no question UI is available, disclose that once and use a numbered question with the same choices and `Custom answer:` in chat. Do not invent a working UI or install an app to provide one.
- Ask one decision at a time, or at most three tightly related questions. Each question must be self-contained and include the recommendation and why it fits the current brief.
- Keep a compact decision log: confirmed facts, decisions, assumptions, unresolved questions. Read each reply, update understanding, and choose the next most consequential unknown. Do useful independent research while an async question is pending; do not answer it for the user.
- Continue until consequential ambiguities are resolved and the user explicitly confirms the summarized brief. No fixed number of rounds. Do not re-ask settled questions. If the user wants to stop or proceed with assumptions, honor that and mark remaining assumptions.
- A preselected option, no response, or elapsed time is not agreement. Required decisions stay pending; optional questions can use clearly stated assumptions under the host's rules.

## Finish

Present a concise brief with goal, target users, in/out of scope, constraints, observable success criteria, confirmed decisions, and any agreed assumptions. Use the Q/A UI for the final understanding check (e.g. Confirm brief / Revise scope, with a custom answer). This confirms understanding only: it does not authorize publishing tickets, coding, or external changes. Once confirmed, offer the recommended next step appropriate to the request, such as drafting a ticket.
