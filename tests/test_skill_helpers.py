"""Offline behavioral tests for installation and the PR monitor."""
import copy
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load('install_skills', ROOT / 'scripts/install_skills.py')
watcher = load('monitor_pr', ROOT / '.agents/skills/pr-babysitter/scripts/monitor_pr.py')


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'source'
        self.destination = Path(self.temp.name) / 'destination'
        for name in ('first', 'second'):
            skill = self.source / name
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: A fixture\n---\n')
            (skill / 'data.txt').write_text(name)

    def test_dry_run_then_install_and_idempotent_retry(self):
        installer.install(self.source, self.destination, ['first'], dry_run=True)
        self.assertFalse(self.destination.exists())
        installer.install(self.source, self.destination, ['first'])
        self.assertEqual('first', (self.destination / 'first/data.txt').read_text())
        self.assertIn('already installed', installer.install(self.source, self.destination, ['first'])[0])

    def test_conflicting_destination_preserved_before_any_copy(self):
        installer.install(self.source, self.destination, ['second'])
        existing = self.destination / 'second/data.txt'
        existing.write_text('user changes')
        with self.assertRaises(ValueError):
            installer.install(self.source, self.destination, ['first', 'second'])
        self.assertEqual('user changes', existing.read_text())
        self.assertFalse((self.destination / 'first').exists())

    def test_path_traversal_and_source_symlinks_rejected(self):
        with self.assertRaises(ValueError):
            installer.install(self.source, self.destination, ['../first'])
        (self.source / 'first/link').symlink_to(self.source / 'second/data.txt')
        with self.assertRaises(ValueError):
            installer.install(self.source, self.destination, ['first'])


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / 'state.json'
        self.snapshot = {'state': 'open', 'head_sha': 'abc', 'base_sha': 'base', 'comments': [{'id': 1, 'body': 'Fix this', 'updated_at': 'first'}], 'inline_comments': [], 'reviews': [], 'ci': {}}

    def run_monitor(self, **kwargs):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return watcher.monitor('owner/repo', 7, self.state, interval=0.001, sleeper=lambda _: None, **kwargs)

    def test_read_only_deduplicates_and_detects_edited_comment(self):
        with redirect_stdout(io.StringIO()) as output:
            watcher.monitor('owner/repo', 7, self.state, max_polls=2, interval=0.001,
                            fetcher=lambda *_: self.snapshot, sleeper=lambda _: None)
        self.assertEqual(1, output.getvalue().count('New PR snapshot:'))
        original = json.loads(self.state.read_text())['last_successful_snapshot']
        changed = copy.deepcopy(self.snapshot)
        changed['comments'][0]['body'] = 'Actually fix that'
        self.run_monitor(fetcher=lambda *_: changed, max_polls=1)
        self.assertNotEqual(original, json.loads(self.state.read_text())['last_successful_snapshot'])

    def test_runner_receives_literal_arguments_and_revisits_pending_decisions(self):
        calls = []
        self.run_monitor(fetcher=lambda *_: self.snapshot, max_polls=2,
                         runner=['agent', '{event_file}', '{repo}', '{pr}', '$(not-a-shell-command)'],
                         dispatcher=lambda args, **kwargs: calls.append(args))
        self.assertEqual(2, len(calls))
        self.assertEqual(['owner/repo', '7', '$(not-a-shell-command)'], calls[0][2:])
        self.assertEqual('Fix this', json.loads(Path(calls[0][1]).read_text())['comments'][0]['body'])
        self.assertNotIn('pending_snapshot', json.loads(self.state.read_text()))

    def test_runner_failures_stop_and_do_not_mark_processed(self):
        def fail(*args, **kwargs):
            raise subprocess.CalledProcessError(1, ['agent'])
        self.assertEqual(1, self.run_monitor(fetcher=lambda *_: self.snapshot, max_polls=10, runner=['agent'], dispatcher=fail))
        state = json.loads(self.state.read_text())
        self.assertEqual('three consecutive failures', state['stopped'])
        self.assertNotIn('last_successful_snapshot', state)
        self.assertIn('pending_snapshot', state)

    def test_one_failed_poll_returns_failure(self):
        def fail(*args):
            raise watcher.MonitorError('Network unavailable')
        self.assertEqual(1, self.run_monitor(fetcher=fail, max_polls=1))
        self.assertEqual('poll bound reached with errors', json.loads(self.state.read_text())['stopped'])

    def test_closed_or_merged_never_dispatches(self):
        for merged in (False, True):
            closed = {**self.snapshot, 'state': 'closed', 'merged': merged}
            self.assertEqual(0, self.run_monitor(fetcher=lambda *_: closed, max_polls=1, runner=['agent'],
                                              dispatcher=lambda *_args, **_kwargs: self.fail('dispatched closed PR')))
            self.assertEqual('merged' if merged else 'closed', json.loads(self.state.read_text())['stopped'])

    def test_mismatched_pr_and_invalid_limits_rejected(self):
        self.state.write_text(json.dumps({'repository': 'different/repo', 'number': 7}))
        with self.assertRaises(watcher.MonitorError):
            self.run_monitor(fetcher=lambda *_: self.snapshot, max_polls=1)
        for interval in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(watcher.MonitorError):
                watcher.monitor('owner/repo', 7, self.state, interval=interval)

    def test_lock_prevents_concurrent_monitors(self):
        path = self.state.with_suffix('.lock')
        with watcher.exclusive_lock(path):
            with self.assertRaises(watcher.MonitorError):
                with watcher.exclusive_lock(path):
                    self.fail('second lock acquired')
        with watcher.exclusive_lock(path):
            pass

    def test_pagination_keeps_all_pages(self):
        with patch.object(watcher, 'command_json', return_value=[[{'id': 1}], [{'id': 2}]]) as request:
            self.assertEqual([{'id': 1}, {'id': 2}], watcher.pages('endpoint'))
            self.assertIn('--paginate', request.call_args.args[0])
            self.assertIn('--slurp', request.call_args.args[0])

    def test_snapshot_rejects_head_change_during_fetch(self):
        first = {'state': 'open', 'head': {'sha': 'abc'}}
        second = {'state': 'open', 'head': {'sha': 'new'}}
        responses = [first, [], [], [], {'state': 'pending'}, [{'check_runs': []}], second]
        with patch.object(watcher, 'command_json', side_effect=responses):
            with self.assertRaises(watcher.MonitorError):
                watcher.fetch_snapshot('owner/repo', 7)


if __name__ == '__main__':
    unittest.main()
