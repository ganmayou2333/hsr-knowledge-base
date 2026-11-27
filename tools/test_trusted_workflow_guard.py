"""Exercise the actual workflow's pre-checkout base guard with a local repo."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


class TrustedWorkflowGuardTests(unittest.TestCase):
    def test_base_guard_rejects_wrong_event_ref_sha_and_checkout(self):
        bash = shutil.which('bash')
        if not bash and os.name == 'nt':
            git = shutil.which('git')
            candidate = Path(git).resolve().parent.parent / 'usr' / 'bin' / 'bash.exe' if git else None
            if candidate and candidate.is_file():
                bash = str(candidate)
        if not bash:
            self.skipTest('bash is unavailable')
        workflow = (Path(__file__).resolve().parent.parent / '.github/workflows/wiki-trusted-data.yml').read_text(encoding='utf-8')
        marker = '      - name: Confirm trusted workflow and checkout base\n'
        self.assertEqual(workflow.count(marker), 1)
        block = workflow.split(marker, 1)[1].split('      - name:', 1)[0]
        self.assertIn('EXPECTED_BASE: ${{ github.event.pull_request.base.sha }}', block)
        self.assertIn('        run: |\n', block)
        script = textwrap.dedent(block.split('        run: |\n', 1)[1])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root / 'trusted')], check=True)
            subprocess.run(['git', '-C', str(root / 'trusted'), '-c', 'user.name=Test', '-c',
                            'user.email=test@example.invalid', 'commit', '--allow-empty', '-qm', 'fixture'], check=True)
            sha = subprocess.check_output(['git', '-C', str(root / 'trusted'), 'rev-parse', 'HEAD'], text=True).strip()
            env = dict(os.environ, GITHUB_EVENT_NAME='pull_request_target', GITHUB_REF='refs/heads/main',
                       GITHUB_SHA=sha, GITHUB_WORKFLOW_SHA=sha, EXPECTED_BASE=sha)
            def execute(changes):
                return subprocess.run([bash, '-e', '-c', script], cwd=root, env=env | changes,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode
            self.assertEqual(execute({}), 0)
            for change in ({'GITHUB_EVENT_NAME': 'pull_request'}, {'GITHUB_REF': 'refs/heads/other'},
                           {'GITHUB_SHA': '0' * 40}, {'EXPECTED_BASE': '0' * 40},
                           {'GITHUB_WORKFLOW_SHA': '0' * 40},
                           {'GITHUB_SHA': '0' * 40, 'EXPECTED_BASE': '0' * 40}):
                with self.subTest(change=change):
                    self.assertNotEqual(execute(change), 0)


if __name__ == '__main__':
    unittest.main()
