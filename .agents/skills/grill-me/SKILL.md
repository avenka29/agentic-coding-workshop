---
name: grill-me
description: Clarify an idea or brief through iterative questions, tradeoffs, and recommendations until the user confirms shared understanding. Use when asked to grill, interview, or pressure-test requirements.
---

# Grill me

Read supplied context and relevant project files before asking questions. Identify the outcome, users, constraints, scope, success criteria, and consequential unknowns. Challenge contradictions and unsupported assumptions without turning the interview into a generic questionnaire.

## Match the user's language

Assume the user may be nontechnical. Start with plain-language questions about their goals, audience, experience, and desired outcomes. Apply this to question wording, choice labels, recommendations, explanations, and the final brief. Describe tradeoffs in terms of what the user will notice: ease of use, time, cost, reliability, or effort.

Keep implementation details, acronyms, and engineering jargon out of the interview unless the user asks technical questions or requests that level of detail. When they do, answer at the depth they ask for and briefly explain unfamiliar terms; do not turn the rest of the interview technical automatically. Resolve routine technical choices from project context yourself rather than asking the user to choose technologies.

When a technical constraint requires a user decision, translate it into a concrete outcome and recommend an option. For example, ask “Should tasks still be there when you reopen the app?” rather than “Which persistence layer should we use?” If technical detail is essential, introduce only enough to explain the decision. Stay respectful and precise without talking down to the user.

## Question loop

- Always use the host's question/answer UI when a suitable tool is available in the active mode. Never call a plan-only question tool outside Plan mode. Prefer multiple choice: 2–3 distinct choices, the recommended option first and marked `(Recommended)`, plus a short rationale/tradeoff. Preserve the UI's built-in custom/free-text answer option; do not add a duplicate Other option. If the UI has no custom-answer support, explicitly allow a custom response.
- If no question UI is available, disclose that once and use a numbered question with the same choices and `Custom answer:` in chat. Do not invent a working UI or install an app to provide one.
- Ask one decision at a time, or at most three tightly related questions. Each question must be self-contained and include the recommendation and why it fits the current brief.
- Keep a compact decision log: confirmed facts, decisions, assumptions, unresolved questions. Read each reply, update understanding, and choose the next most consequential unknown. Do useful independent research while an async question is pending; do not answer it for the user.
- Continue until consequential ambiguities are resolved and the user explicitly confirms the summarized brief. No fixed number of rounds. Do not re-ask settled questions. If the user wants to stop or proceed with assumptions, honor that and mark remaining assumptions.
- A preselected option, no response, or elapsed time is not agreement. Required decisions stay pending; optional questions can use clearly stated assumptions under the host's rules.

## Finish

Present a concise brief with goal, target users, in/out of scope, constraints, observable success criteria, confirmed decisions, and any agreed assumptions. Use the Q/A UI for the final understanding check (e.g. Confirm brief / Revise scope, with a custom answer). This confirms understanding only: it does not authorize publishing tickets, coding, or external changes. Once confirmed, offer the recommended next step appropriate to the request, such as drafting a ticket.
