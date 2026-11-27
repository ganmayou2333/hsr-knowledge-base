"""Build a fresh multi-PR site and omit closed or stale previews."""
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.preview_artifact import InvalidPreviewArtifact
from tools.preview_bundle import build_bundle
from tools.preview_catalog import assemble

HEAD, BASE = 'a' * 40, 'b' * 40


class PreviewCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bundles = self.root / 'bundles'; self.bundles.mkdir()
        self.shell = self.root / 'shell'; self.shell.mkdir()
        for name in ('index.html', 'shell.css', 'shell.js', 'frame.js'):
            (self.shell / name).write_text('trusted', encoding='ascii')
        self.site = self.root / 'site'; self.site.mkdir()
        (self.site / 'index.html').write_text('<script>untrusted()</script>', encoding='utf-8')
        self.states = {1: 'open', 2: 'open', 3: 'closed', 4: 'stale'}
        review_patch = patch('tools.preview_catalog.snapshot', side_effect=lambda repo, number: {
            'pr': number, 'head': HEAD, 'approved': False, 'reviews': [], 'captured_at': int(time.time())})
        review_patch.start()
        self.addCleanup(review_patch.stop)
        for number in self.states:
            build_bundle(self.site, self.bundles / str(number), repo='owner/repo', pr=number, head=HEAD, base=BASE,
                         run=number + 10, run_attempt=1, trusted_run=number + 20, trusted_attempt=1)

    def api(self, path):
        if '/actions/workflows/' in path:
            return {'id': 42, 'state': 'active', 'path': '.github/workflows/wiki-trusted-data.yml'}
        if path.endswith('/branches/main'):
            return {'name': 'main', 'commit': {'sha': BASE}}
        number = int(path.rsplit('/', 1)[-1])
        if '/pulls/' in path:
            state = self.states[number]
            return {'number': number, 'state': 'closed' if state == 'closed' else 'open',
                    'head': {'sha': 'c' * 40 if state == 'stale' else HEAD, 'repo': {'id': 1}},
                    'base': {'sha': BASE, 'ref': 'main', 'repo': {'id': 1, 'full_name': 'owner/repo'}}}
        if number > 20:
            return {'id': number, 'workflow_id': 42, 'repository': {'id': 1}, 'run_attempt': 1,
                    'event': 'pull_request_target', 'status': 'completed', 'conclusion': 'success',
                    'path': '.github/workflows/wiki-trusted-data.yml', 'head_sha': HEAD,
                    'pull_requests': [{'number': number - 20, 'head': {'sha': HEAD, 'repo': {'id': 1}},
                                       'base': {'sha': BASE, 'repo': {'id': 1}}}]}
        number -= 10
        return {'id': number + 10, 'repository': {'id': 1}, 'run_attempt': 1, 'event': 'pull_request', 'status': 'completed', 'conclusion': 'success',
                'path': '.github/workflows/wiki-quality.yml', 'head_sha': HEAD,
                'pull_requests': [{'number': number, 'head': {'sha': HEAD, 'repo': {'id': 1}},
                                   'base': {'sha': BASE, 'repo': {'id': 1}}}]}

    def test_build_repository_identity_is_revalidated(self):
        for change in ('repository', 'head_repo', 'base_repo'):
            def api(path):
                result = self.api(path)
                if path.endswith('/actions/runs/11'):
                    if change == 'repository': result['repository']['id'] = 999
                    elif change == 'head_repo': result['pull_requests'][0]['head']['repo']['id'] = 999
                    else: result['pull_requests'][0]['base']['repo']['id'] = 999
                return result
            with self.subTest(change=change), patch('tools.preview_catalog.gh_api', side_effect=api):
                self.assertEqual(assemble('owner/repo', self.bundles, self.shell, self.root / change), [2])

    def test_multiple_prs_remain_and_closed_or_stale_previews_disappear(self):
        (self.bundles / '1' / 'unused.html').write_text('<script>bad</script>', encoding='ascii')
        with patch('tools.preview_catalog.gh_api', side_effect=self.api):
            included = assemble('owner/repo', self.bundles, self.shell, self.root / 'out')
        self.assertEqual(included, [1, 2])
        output = self.root / 'out'
        self.assertEqual(sorted(p.name for p in (output / 'previews').iterdir()), ['1', '2'])
        self.assertFalse((output / 'previews' / '1' / 'unused.html').exists())
        self.assertEqual((output / 'index.html').read_text(), 'trusted')
        review = json.loads((output / 'previews' / '1' / 'review.json').read_text())
        self.assertFalse(review['approved'])
        self.assertEqual(review['repo'], 'owner/repo')
        self.assertTrue(all(p.suffix == '.json' for p in (output / 'previews').rglob('*') if p.is_file()))

    def test_corrupted_object_or_missing_api_does_not_create_output(self):
        manifest = json.loads((self.bundles / '1' / 'manifest.json').read_text())
        obj = self.bundles / '1' / 'objects' / (manifest['files']['index.html'] + '.json')
        obj.write_text('{"data":"YQ=="}', encoding='ascii')
        with patch('tools.preview_catalog.gh_api', side_effect=self.api), self.assertRaises(InvalidPreviewArtifact):
            assemble('owner/repo', self.bundles, self.shell, self.root / 'out')
        self.assertFalse((self.root / 'out').exists())
        with patch('tools.preview_catalog.gh_api', side_effect=subprocess.CalledProcessError(1, 'gh')), self.assertRaises(subprocess.CalledProcessError):
            assemble('owner/repo', self.bundles, self.shell, self.root / 'out')
        self.assertFalse((self.root / 'out').exists())

    def test_pr_changing_during_assembly_aborts_without_output(self):
        calls = 0
        def api(path):
            nonlocal calls
            result = self.api(path)
            if path.endswith('/pulls/1'):
                calls += 1
                if calls == 2: result['head']['sha'] = 'd' * 40
            return result
        with patch('tools.preview_catalog.gh_api', side_effect=api), self.assertRaises(InvalidPreviewArtifact):
            assemble('owner/repo', self.bundles, self.shell, self.root / 'out')
        self.assertFalse((self.root / 'out').exists())

    def test_stale_pull_base_is_not_a_current_main(self):
        def api(path):
            if path.endswith('/branches/main'):
                return {'name': 'main', 'commit': {'sha': 'c' * 40}}
            return self.api(path)
        with patch('tools.preview_catalog.gh_api', side_effect=api):
            self.assertEqual(assemble('owner/repo', self.bundles, self.shell, self.root / 'out'), [])

    def test_never_overwrites_existing_output(self):
        output = self.root / 'out'; output.mkdir(); (output / 'keep').write_text('keep')
        with self.assertRaises(InvalidPreviewArtifact): assemble('owner/repo', self.bundles, self.shell, output)
        self.assertEqual((output / 'keep').read_text(), 'keep')

    def test_review_service_failure_leaves_preview_without_approval(self):
        with patch('tools.preview_catalog.gh_api', side_effect=self.api), patch('tools.preview_catalog.snapshot', side_effect=subprocess.CalledProcessError(1, 'gh')):
            assemble('owner/repo', self.bundles, self.shell, self.root / 'out')
        self.assertFalse((self.root / 'out' / 'previews' / '1' / 'review.json').exists())

    def test_stale_or_repeated_trusted_check_is_never_published(self):
        def api(path):
            result = self.api(path)
            if path.endswith('/actions/runs/21'):
                result['run_attempt'] = 2
            return result
        with patch('tools.preview_catalog.gh_api', side_effect=api):
            self.assertEqual(assemble('owner/repo', self.bundles, self.shell, self.root / 'out'), [2])
        self.assertFalse((self.root / 'out' / 'previews' / '1').exists())

    def test_repeated_build_invalidates_previous_preview(self):
        def api(path):
            result = self.api(path)
            if path.endswith('/actions/runs/11'):
                result['run_attempt'] = 2
            return result
        with patch('tools.preview_catalog.gh_api', side_effect=api):
            self.assertEqual(assemble('owner/repo', self.bundles, self.shell, self.root / 'out'), [2])

    def test_trusted_check_changing_during_assembly_aborts_output(self):
        calls = 0
        def api(path):
            nonlocal calls
            result = self.api(path)
            if path.endswith('/actions/runs/21'):
                calls += 1
                if calls == 2:
                    result['run_attempt'] = 2
            return result
        with patch('tools.preview_catalog.gh_api', side_effect=api), self.assertRaises(InvalidPreviewArtifact):
            assemble('owner/repo', self.bundles, self.shell, self.root / 'out')
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__': unittest.main()
