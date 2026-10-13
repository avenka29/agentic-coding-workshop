"""Test macOS wrapper routing with fake host tools; no packages are installed."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MacSetupRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='setup fixtures ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scripts = self.root / 'scripts'
        self.scripts.mkdir()
        shutil.copy(ROOT / 'scripts/macos.sh', self.scripts / 'macos.sh')
        for mode in ('setup', 'dev'):
            (self.scripts / f'{mode}.sh').write_text(f'#!/bin/bash\nprintf "{mode} "\nnode\npython3.13\n')
        self.tools = self.root / 'fake tools'
        self.tools.mkdir()
        self.log = self.root / 'brew.jsonl'
        self.env = dict(os.environ, PATH=f'{self.tools}:/usr/bin:/bin')
        self.executable(self.tools / 'uname', '#!/bin/sh\necho Darwin\n')
        for formula, executable in [('node@22', 'node'), ('python@3.13', 'python3.13')]:
            folder = self.root / formula / 'bin'
            folder.mkdir(parents=True)
            self.executable(folder / executable, f'#!/bin/sh\necho "mock {formula}"\n')
        self.executable(self.tools / 'brew', f'''#!{sys.executable}
import json, sys
from pathlib import Path
root = Path({str(self.root)!r})
with (root / 'brew.jsonl').open('a') as log:
    log.write(json.dumps(sys.argv[1:]) + '\\n')
if sys.argv[1] == '--prefix':
    print(root / sys.argv[2])
''')

    def executable(self, path, content):
        path.write_text(content)
        path.chmod(0o755)

    def run_wrapper(self, mode):
        return subprocess.run(['/bin/bash', str(self.scripts / 'macos.sh'), mode], env=self.env,
                              cwd='/tmp', capture_output=True, text=True, timeout=10)

    def test_setup_and_dev_find_keg_only_tools_from_unrelated_directory(self):
        for mode in ('setup', 'dev'):
            with self.subTest(mode=mode):
                result = self.run_wrapper(mode)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn(f'{mode} mock node@22', result.stdout)
                self.assertIn('mock python@3.13', result.stdout)
        actions = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertFalse(any(action[0] == 'install' for action in actions))

    def test_host_install_happens_only_in_explicit_mode(self):
        result = self.run_wrapper('install-tools')
        self.assertEqual(0, result.returncode, result.stderr)
        actions = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertIn(['install', 'node@22', 'python@3.13'], actions)
        self.assertNotIn('mock node@22', result.stdout)

    def test_other_os_and_invalid_modes_do_not_install(self):
        self.executable(self.tools / 'uname', '#!/bin/sh\necho Linux\n')
        for mode in ('setup', 'install-tools', 'invalid'):
            result = self.run_wrapper(mode)
            self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.log.exists())


if __name__ == '__main__':
    unittest.main()
