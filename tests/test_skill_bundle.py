"""Verify the redistributable upstream snapshot and worktree-safe links."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillBundleTests(unittest.TestCase):
    def test_upstream_files_match_pinned_blob_hashes_except_documented_adaptation(self):
        skill = ROOT / '.agents/skills/ui-ux-pro-max'
        manifest = json.loads((skill / 'UPSTREAM.json').read_text())
        self.assertEqual({'SKILL.md'}, set(manifest['local_changes']))
        for entry in manifest['files']:
            with self.subTest(path=entry['path']):
                path = skill / entry['path']
                self.assertTrue(path.is_file())
                if entry['path'] in manifest['local_changes']:
                    continue
                payload = path.read_bytes()
                blob = b'blob ' + str(len(payload)).encode() + b'\0' + payload
                self.assertEqual(entry['size'], len(payload))
                self.assertEqual(entry['sha'], hashlib.sha1(blob).hexdigest())

    def test_links_resolve_after_copying_checkout_to_another_directory(self):
        import shutil
        with tempfile.TemporaryDirectory() as raw:
            checkout = Path(raw) / 'new-checkout'
            checkout.mkdir()
            shutil.copytree(ROOT / '.agents', checkout / '.agents', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            shutil.copytree(ROOT / '.claude', checkout / '.claude', symlinks=True)
            shutil.copy(ROOT / 'AGENTS.md', checkout / 'AGENTS.md')
            (checkout / 'CLAUDE.md').symlink_to('AGENTS.md')
            self.assertTrue((checkout / '.claude/skills').is_symlink())
            for name in ('grill-me', 'create-ticket', 'implement-ticket', 'pr-babysitter', 'ui-ux-pro-max'):
                self.assertTrue((checkout / '.claude/skills' / name / 'SKILL.md').is_file())
            self.assertEqual((checkout / 'CLAUDE.md').read_text(), (checkout / 'AGENTS.md').read_text())


if __name__ == '__main__':
    unittest.main()
