#!/usr/bin/env python3
"""Poll a GitHub PR; optionally dispatch changed snapshots to an agent runner.

The helper never edits code, posts comments, pushes, or merges by itself.
Python standard library + authenticated gh; Unix/WSL for the advisory lock.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time


class MonitorError(RuntimeError):
    pass


def command_json(arguments: list[str]):
    try:
        result = subprocess.run(arguments, capture_output=True, text=True, timeout=120, check=True)
        return json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        # Don't echo command output, which may include private tracker data.
        raise MonitorError(f'GitHub request failed ({type(error).__name__}). Check gh authentication, network, and repository access.') from error


def pages(endpoint: str) -> list:
    result = command_json(['gh', 'api', '--paginate', '--slurp', endpoint])
    if not isinstance(result, list) or any(not isinstance(page, list) for page in result):
        raise MonitorError('Unexpected paginated GitHub response.')
    return [item for page in result for item in page]


def fetch_snapshot(repo: str, pr: int) -> dict:
    before = command_json(['gh', 'api', f'repos/{repo}/pulls/{pr}'])
    if before.get('state') != 'open':
        return {'repository': repo, 'number': pr, 'state': before.get('state'), 'merged': bool(before.get('merged')), 'head_sha': before['head']['sha']}
    comments = pages(f'repos/{repo}/issues/{pr}/comments?per_page=100')
    inline = pages(f'repos/{repo}/pulls/{pr}/comments?per_page=100')
    reviews = pages(f'repos/{repo}/pulls/{pr}/reviews?per_page=100')
    sha = before['head']['sha']
    statuses = command_json(['gh', 'api', f'repos/{repo}/commits/{sha}/status'])
    check_pages = command_json(['gh', 'api', '--paginate', '--slurp', f'repos/{repo}/commits/{sha}/check-runs?per_page=100'])
    checks = [check for page in check_pages for check in page['check_runs']]
    after = command_json(['gh', 'api', f'repos/{repo}/pulls/{pr}'])
    if before['head']['sha'] != after['head']['sha']:
        raise MonitorError('PR head changed during collection; retry next cycle.')
    # REST comments don't include GraphQL thread resolution. Agent must fetch it before resolving/acting.
    return {
        'repository': repo, 'number': pr, 'state': after['state'], 'merged': bool(after.get('merged')),
        'url': after['html_url'], 'head_sha': sha, 'head_ref': after['head']['ref'],
        'head_repository': after['head']['repo']['full_name'] if after['head'].get('repo') else None,
        'base_sha': after['base']['sha'], 'base_ref': after['base']['ref'],
        'comments': comments, 'inline_comments': inline, 'reviews': reviews,
        'ci': {'combined_state': statuses['state'], 'statuses': pages(f'repos/{repo}/commits/{sha}/statuses?per_page=100'), 'checks': checks},
        'thread_resolution': 'not supplied by REST; fetch current unresolved threads before acting',
    }


def fingerprint(snapshot: dict) -> str:
    # Only actionable versions/states; omit volatile timestamps/counts in metadata.
    items = []
    for kind in ('comments', 'inline_comments', 'reviews'):
        for item in snapshot.get(kind, []):
            items.append((kind, item['id'], item.get('updated_at'), item.get('body'), item.get('state'), item.get('position'), item.get('commit_id')))
    ci = snapshot.get('ci', {})
    checks = [(item['id'], item.get('status'), item.get('conclusion'), item.get('completed_at')) for item in ci.get('checks', [])]
    statuses = [(item['id'], item.get('state')) for item in ci.get('statuses', [])]
    relevant = [snapshot.get('state'), snapshot.get('head_sha'), snapshot.get('base_sha'), sorted(items), sorted(checks), sorted(statuses), ci.get('combined_state')]
    return hashlib.sha256(json.dumps(relevant, sort_keys=True).encode()).hexdigest()


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as handle:
            json.dump(data, handle, indent=2)
            handle.write('\n')
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


@contextmanager
def exclusive_lock(path: Path):
    try:
        import fcntl
    except ImportError as error:
        raise MonitorError('Use Unix/WSL or a host scheduler; this helper needs fcntl locking.') from error
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise MonitorError('A monitor is already using this state file.') from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def monitor(repo: str, pr: int, state_file: Path, interval: float = 15, max_polls: int = 96,
            runner: list[str] | None = None, runner_timeout: float = 600,
            fetcher=fetch_snapshot, dispatcher=subprocess.run, sleeper=time.sleep) -> int:
    if not math.isfinite(interval) or interval <= 0 or max_polls <= 0 or not math.isfinite(runner_timeout) or runner_timeout <= 0:
        raise MonitorError('Interval, poll bound, and runner timeout must be positive and finite.')
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    if state and (state.get('repository'), state.get('number')) != (repo, pr):
        raise MonitorError('State file belongs to another PR.')
    state.update({'repository': repo, 'number': pr})
    event_file = state_file.with_suffix('.event.json')
    failures = 0
    for index in range(max_polls):
        started = time.monotonic()
        try:
            snapshot = fetcher(repo, pr)
            write_json(event_file, snapshot)
            if snapshot['state'] != 'open':
                state['stopped'] = 'merged' if snapshot.get('merged') else 'closed'
                write_json(state_file, state)
                print(f"Monitor stopped: PR {state['stopped']}.", flush=True)
                return 0
            version = fingerprint(snapshot)
            # Runner executes every cycle for unresolved items/human decisions, even without new feedback.
            changed = version != state.get('last_successful_snapshot')
            if runner:
                state['pending_snapshot'] = version
                write_json(state_file, state)
                values = {'event_file': str(event_file.resolve()), 'repo': repo, 'pr': str(pr)}
                arguments = []
                for argument in runner:
                    for key, value in values.items():
                        argument = argument.replace('{' + key + '}', value)
                    arguments.append(argument)
                dispatcher(arguments, check=True, timeout=runner_timeout)
                state['last_successful_snapshot'] = version
                state.pop('pending_snapshot', None)
            elif changed:
                print(f'New PR snapshot: {event_file.resolve()} (read-only; no agent runner configured).', flush=True)
                state['last_successful_snapshot'] = version
            state['last_poll_at'] = time.time()
            state['stopped'] = None
            write_json(state_file, state)
            failures = 0
        except (MonitorError, OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as error:
            failures += 1
            print(f'Poll failed ({failures}/3): {type(error).__name__}.', file=sys.stderr, flush=True)
            if failures >= 3:
                state['stopped'] = 'three consecutive failures'
                write_json(state_file, state)
                return 1
        if index + 1 < max_polls:
            sleeper(max(0, interval * 60 - (time.monotonic() - started)))
    state['stopped'] = 'poll bound reached with errors' if failures else 'poll bound reached'
    write_json(state_file, state)
    print(f"Monitor stopped: {state['stopped']}.", flush=True)
    return 1 if failures else 0


def default_state(repo: str, pr: int) -> Path:
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-common-dir'], capture_output=True, text=True, check=True)
    except (OSError, subprocess.SubprocessError) as error:
        raise MonitorError('Run inside the repository or pass --state explicitly.') from error
    return Path(result.stdout.strip()).resolve() / 'workshop-state' / 'prs' / f"{repo.replace('/', '-')}-{pr}.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='GitHub owner/repository')
    parser.add_argument('--pr', type=int, required=True)
    parser.add_argument('--interval-minutes', type=float, default=15)
    parser.add_argument('--max-polls', type=int, default=96)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--state', type=Path)
    parser.add_argument('--runner-json', help='JSON array of agent-runner arguments, no shell execution')
    parser.add_argument('--runner-timeout-seconds', type=float, default=600)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo) or args.pr <= 0:
        parser.error('Provide a valid owner/repository and positive PR number.')
    try:
        runner = json.loads(args.runner_json) if args.runner_json else None
        if runner is not None and (not isinstance(runner, list) or not runner or any(not isinstance(part, str) or not part for part in runner)):
            raise MonitorError('--runner-json must be a nonempty array of nonempty strings.')
        state = args.state or default_state(args.repo, args.pr)
        with exclusive_lock(state.with_suffix('.lock')):
            return monitor(args.repo, args.pr, state, args.interval_minutes, 1 if args.once else args.max_polls,
                           runner, args.runner_timeout_seconds)
    except (MonitorError, OSError, ValueError) as error:
        parser.exit(1, f'Monitor setup failed: {error}\n')
    except KeyboardInterrupt:
        print('Monitor stopped by user.', flush=True)
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
