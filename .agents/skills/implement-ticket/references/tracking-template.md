# Persistent implementation record

Store this in `<git-common-dir>/workshop-state/tickets/<safe-key>.md` so it survives agent restarts and worktree changes without changing source ownership. Avoid private issue text/secrets when a brief summary suffices.

```markdown
# <Issue key>: <Title>
Issue: <canonical URL>
Remote tracking: <active / unavailable / local-only>
Repository / remote / PR base: <values>
Base SHA: <sha>
Branch / worktree: <values>
Approver: <user or main agent>
Plan approval: <message/decision, scope, timestamp; pending initially>

| Milestone | Deliverable / acceptance criteria | Verification | Status | Gate approval |
|---|---|---|---|---|
| M1 | <outcome> | <check> | pending | pending |

## Evidence and decisions
<Per-milestone commands/results, commits, explicit approvals, scope changes, blockers>

## Reviews
Security: <revision, findings, disposition or explicit waiver>
Architecture: <revision, findings, disposition or explicit waiver>

## Handoff
PR: <URL or pending>
Final head: <sha>
Remaining limitations: <details>
```

Update remote progress with brief milestone status/evidence when permitted. Do not overwrite the issue description or mark it complete before its completion policy is satisfied. On resume, read this record and the current issue/branch rather than restarting from scratch.
