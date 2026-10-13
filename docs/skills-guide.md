# Reusable coding skills

The repository includes five skills in `.agents/skills/`. The four workflow skills are written for this workshop; UI UX Pro Max is a pinned upstream bundle. `.claude/skills` is a symlink to the same directory, so there is one canonical copy.

| Skill | Use |
|---|---|
| `grill-me` | Question an idea until shared understanding, with recommended choices and a custom answer |
| `create-ticket` | Produce a scoped ticket with observable acceptance criteria and verification |
| `implement-ticket` | Implement an issue through approved milestones in a worktree; independent security/architecture gates precede the PR |
| `pr-babysitter` | Monitor PR feedback, defer with reasons, fix bounded issues, and escalate consequential decisions |
| `ui-ux-pro-max` | Search local design guidance and generate a design system for the detected stack |

## Use after cloning

Install the application's dependencies using README.md. The skills themselves need no npm or Python package installation. Launch a skill-capable coding agent in this repository; Codex discovers `.agents/skills`, and Claude Code uses `.claude/skills`. Codex's official [skill documentation](https://learn.chatgpt.com/docs/build-skills) describes local discovery and symlink support. If the new skills do not appear, start a fresh session/restart the agent.

Example Codex prompts:

```text
$grill-me Help me clarify a small task creation feature for this application.
$create-ticket Draft two tickets from the agreed task creation contract, one frontend and one backend.
$implement-ticket Implement https://github.com/OWNER/REPO/issues/NUMBER using the approved scope.
$pr-babysitter Monitor https://github.com/OWNER/REPO/pull/NUMBER every 15 minutes.
$ui-ux-pro-max Review the task list and recommend accessible form styling for the existing React stack.
```

In Claude Code use the corresponding `/grill-me`, `/create-ticket`, `/implement-ticket`, `/pr-babysitter`, and `/ui-ux-pro-max` skills. If your client does not support this invocation syntax, ask it to read the named skill's SKILL.md explicitly. Capabilities vary by host; the skill does not create a missing UI, tracker connection, scheduler, or subagent tool.

`grill-me` uses the host's Q/A UI when available, with the recommendation first and custom/free-text answers allowed. Without such a UI it uses the same question/choices in chat and explains the fallback. It stops when the user confirms the brief or explicitly asks to proceed/stop.

## Install outside this repository

The offline installer copies the entire bundle, including UI UX Pro Max's data, scripts, and license. It refuses to replace differing files and supports a dry run:

```bash
# Portable local bundle in your dev directory:
python3 scripts/install_skills.py --dest ../agentic-skills/.agents/skills --dry-run
python3 scripts/install_skills.py --dest ../agentic-skills/.agents/skills

# Codex user-wide discovery (run yourself if your agent cannot write here):
python3 scripts/install_skills.py --dest ~/.agents/skills

# Claude Code user-wide installation:
python3 scripts/install_skills.py --dest ~/.claude/skills

# Another project's repository-scoped install, or a single skill:
python3 scripts/install_skills.py --dest /path/to/project/.agents/skills
python3 scripts/install_skills.py --dest /path/to/project/.agents/skills --skill grill-me
```

Keep one installed version per discovery scope when possible; duplicate names can appear separately in selectors. For an older Codex setup configured to use `$CODEX_HOME/skills`, pass that actual directory as `--dest` instead. Installation never changes the agent's configuration or overwrites unrelated skills. Re-running with identical copies is safe. For updates with differing copies, review the changes and reconcile manually or choose a fresh destination.

The setup session installed the dev bundle at `/home/avenka29/dev/agentic-skills/.agents/skills`. User-wide directories are outside that session's permitted writable roots, and the parent dev directory's `.agents`/`.codex` directories are read-only. Consequently the dev bundle is a portable local copy, not a claimed user-wide installation. The checked-in repository skills are usable when an agent opens this repository. Run the user-wide command above to make them discoverable across projects.

## Ticket implementation gates

`create-ticket` produces a reviewable draft before publication. Explicitly requesting creation in a known tracker authorizes that publication; drafting alone does not. GitHub/Linear/Jira need an authenticated connector or CLI. Missing integrations produce an honest local draft/tracking fallback, not a fabricated issue URL.

`implement-ticket` requires approval of the concrete plan before coding, and approval of each milestone's evidence before starting the next unless the user/main agent has explicitly preapproved that scope. A delegated implementer reports gates to its main agent. All coding takes place in a separate worktree. Tracking lives in `<git-common-dir>/workshop-state/tickets/` and records the issue URL, approvals, results, commits, review revisions, and PR URL; relevant remote progress updates are made when permitted.

The security and architecture reviewers inspect the proposed PR diff before publication. Their independent gates must pass, or the approver must explicitly accept a documented waiver/limitation. A host without subagents needs human review or an explicit waiver; the skill cannot silently replace independence with self-review. Publication uses the approved target and normal pushes, never automatic merging. This repository retains its no-push-without-approval instruction.

For the 20-minute workshop, use the existing two small tickets and worktree guide. The exercise uses grill-me, create-ticket, and implement-ticket explicitly; interviewing, remote ticket setup, and extended review may need time outside the timed exercise. UI UX Pro Max and PR babysitting are optional follow-up practice. Do not implement task creation just by installing skills.

## PR monitor

The skill prefers a host scheduler that can run an agent. Without a scheduler, its local helper needs Python 3, Unix/macOS/WSL, and [GitHub CLI](https://cli.github.com/) authenticated for the repository. Run inside the intended repository so the default state lives in its Git common directory.

```bash
# One read-only poll; substitute your real repository and PR number:
python3 .agents/skills/pr-babysitter/scripts/monitor_pr.py --repo OWNER/REPO --pr 123 --once

# Foreground read-only monitor, default 15-minute interval, at most 96 polls:
python3 .agents/skills/pr-babysitter/scripts/monitor_pr.py --repo OWNER/REPO --pr 123

# Custom interval:
python3 .agents/skills/pr-babysitter/scripts/monitor_pr.py --repo OWNER/REPO --pr 123 --interval-minutes 5 --max-polls 12
```

Without a runner this only collects snapshots; it does not fix or reply to anything. Stop with Ctrl-C. It also stops on closed/merged PRs, three consecutive failures, or the poll bound. The cadence is measured from cycle start, so long agent runs can delay it. State/lock files prevent overlapping runs on the same state file; use the same state for a given PR. Don't launch multiple agents that write to the same worktree.

To execute autonomous triage/fixes, configure an already installed agent runner. Pass its invocation as a JSON argument array, for example:

```bash
python3 .agents/skills/pr-babysitter/scripts/monitor_pr.py --repo OWNER/REPO --pr 123 \
  --runner-json '["/absolute/path/to/your-agent-runner", "{event_file}", "{repo}", "{pr}"]'
```

`your-agent-runner` is an adapter you supply for your chosen agent, not a bundled executable. Its contract is: receive snapshot path, repository, and PR number; load `$pr-babysitter`; run one cycle without scheduling another monitor; persist triage dispositions; return 0 when that cycle has been handled (including recorded escalations/deferred items) or nonzero on execution failure. Use your agent's normal permissions; do not enable bypass modes. The runner is invoked every cycle to revisit pending human decisions, so its ledger must suppress duplicate fixes/replies. A runner timeout defaults to 600 seconds and can be configured. Keep a live session able to receive decisions, or provide an explicit persisted decision channel the runner reads; no reply means no approval.

The helper uses paginated [GitHub CLI API](https://cli.github.com/manual/gh_api) reads for comments/reviews/statuses/checks. REST review comments lack thread resolution, so the agent must fetch current unresolved threads before acting/resolving; the snapshot marks this limitation. CI data are tied to the observed head and are rechecked by the agent before pushing. The helper does not install an OS service, survive terminal shutdown, invent credentials, or authorize deployments/merges.

## UI UX Pro Max provenance and use

Source: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), pinned to commit `7246805992a42b7bba37d4cac83b01416f0c6c44`, MIT license. The bundle includes the original LICENSE and a file/hash manifest in `.agents/skills/ui-ux-pro-max/UPSTREAM.json`. Only SKILL.md's plugin-specific script paths were adapted to work with local/copied skill directories; executable scripts/data are unchanged. Fonts/icons are catalog metadata, not installed fonts or downloaded assets; preserve the upstream provenance/license records.

```bash
python3 .agents/skills/ui-ux-pro-max/scripts/search.py 'error summary validation' --domain ux
python3 .agents/skills/ui-ux-pro-max/scripts/search.py 'form state' --stack react
python3 .agents/skills/ui-ux-pro-max/scripts/search.py 'productivity dashboard minimal' --design-system -p 'Workshop Tasks'
```

Search runs offline with the Python standard library. Respect the project's no-external-services requirement: recommendations about web fonts or third-party assets do not authorize adding external network dependencies.

## Verify this bundle

```bash
python3 -m unittest discover -s tests -v
python3 .agents/skills/ui-ux-pro-max/scripts/validate_data.py
python3 .agents/skills/ui-ux-pro-max/scripts/tests/test_core.py
python3 .agents/skills/ui-ux-pro-max/scripts/tests/test_design_system_mode.py
python3 .agents/skills/ui-ux-pro-max/scripts/tests/test_design_system_stack.py
```

Other upstream tests retained in the snapshot include maintenance tests that require files from the full upstream repository. Don't use broad unittest discovery over that vendored directory; run the standalone checks listed above.
