"""The reconciler discovers current checks but never deploys PR code."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.preview_artifact import InvalidPreviewArtifact
from tools.preview_bundle import build_bundle
from tools.reconcile_previews import latest_run, pages_items, reconcile

HEAD, BASE = 'a' * 40, 'b' * 40
PR = {'number': 7, 'state': 'open', 'head': {'sha': HEAD, 'repo': {'id': 1}},
      'base': {'sha': BASE, 'repo': {'id': 1}}}
WORKFLOW = {'id': 42, 'state': 'active', 'path': '.github/workflows/wiki-trusted-data.yml'}
ASSOCIATION = {'number': 7, 'head': {'sha': HEAD, 'repo': {'id': 1}},
               'base': {'sha': BASE, 'repo': {'id': 1}}}
BUILD = {'id': 10, 'event': 'pull_request', 'status': 'completed', 'conclusion': 'success',
         'path': '.github/workflows/wiki-quality.yml', 'head_sha': HEAD,
         'run_started_at': '2026-11-21T00:00:00Z', 'pull_requests': [ASSOCIATION]}
TRUSTED = {'id': 11, 'workflow_id': 42, 'repository': {'id': 1}, 'event': 'pull_request_target',
           'status': 'completed', 'conclusion': 'success', 'path': WORKFLOW['path'], 'head_sha': HEAD,
           'run_attempt': 1, 'run_started_at': '2026-11-21T00:00:01Z', 'pull_requests': [ASSOCIATION]}


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.builds, self.trusted = [copy.deepcopy(BUILD)], [copy.deepcopy(TRUSTED)]
        self.staged = []

    def api(self, path, paginate=False):
        if '/pulls?state=' in path:
            return [[copy.deepcopy(PR)]]
        if '/wiki-trusted-data.yml/runs?' in path:
            return [{'workflow_runs': self.trusted}]
        if '/wiki-quality.yml/runs?' in path:
            return [{'workflow_runs': self.builds}]
        if path.endswith('/actions/workflows/wiki-trusted-data.yml'):
            return WORKFLOW
        raise AssertionError(path)

    def stage(self, repo, number, build, destination, *, trusted_run_id):
        self.staged.append((number, build, trusted_run_id))
        Path(destination).mkdir()

    def assemble(self, repo, bundles, shell, destination):
        numbers = sorted(int(path.name) for path in Path(bundles).iterdir())
        Path(destination).mkdir()
        return numbers

    def run_reconcile(self, destination='out'):
        with patch('tools.reconcile_previews.gh_api', side_effect=self.api), \
                patch('tools.reconcile_previews.stage', side_effect=self.stage), \
                patch('tools.reconcile_previews.assemble', side_effect=self.assemble):
            return reconcile('owner/repo', self.root, self.root / destination)

    def test_discovers_and_stages_current_runs(self):
        self.assertEqual(self.run_reconcile(), [7])
        self.assertEqual(self.staged, [(7, 10, 11)])

    def test_newer_failed_or_running_check_does_not_reuse_old_success(self):
        for status, conclusion in [('completed', 'failure'), ('in_progress', None)]:
            self.builds = [copy.deepcopy(BUILD), dict(BUILD, id=12, status=status, conclusion=conclusion,
                                                      run_started_at='2026-11-21T00:01:00Z')]
            self.assertEqual(self.run_reconcile(f'out-{status}'), [])
        self.assertEqual(self.staged, [])

    def test_missing_association_is_omitted_but_api_failure_aborts(self):
        self.builds[0]['pull_requests'] = []
        self.assertEqual(self.run_reconcile(), [])
        self.assertEqual(self.staged, [])
        with patch('tools.reconcile_previews.gh_api', side_effect=subprocess.CalledProcessError(1, 'gh')):
            with self.assertRaises(subprocess.CalledProcessError):
                reconcile('owner/repo', self.root, self.root / 'api-failure')
        self.assertFalse((self.root / 'api-failure').exists())

    def test_same_repository_run_without_association_is_also_skipped(self):
        # Observed on internal PR #53: matching head and repository IDs do not
        # bind either the build or trusted run to one particular PR.
        self.builds[0]['pull_requests'] = []
        self.trusted[0]['pull_requests'] = []
        self.assertEqual(self.run_reconcile(), [])
        self.assertEqual(self.staged, [])

    def test_fork_run_without_github_pr_association_fails_closed(self):
        # GitHub can return an empty pull_requests list for fork runs. Without
        # trustworthy evidence binding the run to a PR, never infer the link.
        external = copy.deepcopy(PR)
        external['head']['repo']['id'] = 2
        self.builds[0]['pull_requests'] = []
        def api(path, paginate=False):
            if '/pulls?state=' in path:
                return [[external]]
            return self.api(path, paginate)
        with patch('tools.reconcile_previews.gh_api', side_effect=api), \
                patch('tools.reconcile_previews.stage', side_effect=self.stage), \
                patch('tools.reconcile_previews.assemble', side_effect=self.assemble):
            self.assertEqual(reconcile('owner/repo', self.root, self.root / 'out'), [])
        self.assertEqual(self.staged, [])

    def test_unassociated_fork_does_not_block_other_preview(self):
        external = copy.deepcopy(PR)
        external['head']['repo']['id'] = 2
        other = copy.deepcopy(PR)
        other['number'] = 8
        other['head']['sha'] = 'c' * 40
        association = copy.deepcopy(other)
        for key in ('state',):
            association.pop(key)
        def api(path, paginate=False):
            if '/pulls?state=' in path:
                return [[external, other]]
            if '/runs?' in path:
                if 'head_sha=' + HEAD in path:
                    return [{'workflow_runs': [dict(BUILD, pull_requests=[])]}]
                run = copy.deepcopy(TRUSTED if 'wiki-trusted-data.yml' in path else BUILD)
                run.update(id=21 if run['event'] == 'pull_request_target' else 20,
                           head_sha='c' * 40, pull_requests=[association])
                return [{'workflow_runs': [run]}]
            return self.api(path, paginate)
        with patch('tools.reconcile_previews.gh_api', side_effect=api), \
                patch('tools.reconcile_previews.stage', side_effect=self.stage), \
                patch('tools.reconcile_previews.assemble', side_effect=self.assemble):
            self.assertEqual(reconcile('owner/repo', self.root, self.root / 'out'), [8])
        self.assertEqual(self.staged, [(8, 20, 21)])

    def test_old_base_trusted_check_is_not_selected(self):
        self.trusted[0]['pull_requests'][0]['base']['sha'] = 'c' * 40
        self.assertEqual(self.run_reconcile(), [])
        self.assertEqual(self.staged, [])

    def test_discovery_builds_an_inert_catalog(self):
        for name in ('index.html', 'shell.css', 'shell.js', 'frame.js'):
            (self.root / name).write_text('trusted', encoding='ascii')
        site = self.root / 'fixture'
        site.mkdir()
        (site / 'index.html').write_text('<script>untrusted()</script>', encoding='ascii')
        def stage(repo, number, build, destination, *, trusted_run_id):
            build_bundle(site, destination, repo=repo, pr=number, head=HEAD, base=BASE, run=build,
                         run_attempt=1, trusted_run=trusted_run_id, trusted_attempt=1)
        review = {'pr': 7, 'head': HEAD, 'approved': False, 'reviews': [], 'captured_at': 1}
        with patch('tools.reconcile_previews.gh_api', side_effect=self.api), \
                patch('tools.reconcile_previews.stage', side_effect=stage), \
                patch('tools.preview_catalog.metadata', return_value=True), \
                patch('tools.preview_catalog.snapshot', return_value=review):
            self.assertEqual(reconcile('owner/repo', self.root, self.root / 'out'), [7])
        preview = self.root / 'out' / 'previews' / '7'
        manifest = json.loads((preview / 'manifest.json').read_text(encoding='ascii'))
        self.assertEqual((manifest['run'], manifest['trusted_run']), (10, 11))
        self.assertFalse((preview / 'index.html').exists())
        self.assertTrue((preview / 'objects' / (manifest['files']['index.html'] + '.json')).is_file())

    def test_rejects_invalid_run_dates(self):
        run = dict(BUILD, run_started_at='2026-99-99T00:00:00Z')
        with self.assertRaises(InvalidPreviewArtifact):
            latest_run([run], 7, PR, 'pull_request', BUILD['path'])

    def test_pagination_limit_cannot_be_treated_as_complete(self):
        self.assertEqual(len(pages_items([{'workflow_runs': [None] * 999}], 'workflow_runs')), 999)
        self.assertEqual(len(pages_items([[None] * 999])), 999)
        with self.assertRaises(InvalidPreviewArtifact):
            pages_items([{'workflow_runs': [None] * 1000}], 'workflow_runs')
        with self.assertRaises(InvalidPreviewArtifact):
            pages_items([[None] * 1000])

    def test_duplicate_run_across_pages_cannot_hide_a_failure_or_rerun(self):
        for second in (dict(BUILD, conclusion='failure'), dict(BUILD, run_attempt=2), copy.deepcopy(BUILD)):
            with self.subTest(second=second), self.assertRaises(InvalidPreviewArtifact):
                latest_run([BUILD, second], 7, PR, 'pull_request', BUILD['path'])
        self.builds = [BUILD, dict(BUILD, conclusion='failure')]
        with self.assertRaises(InvalidPreviewArtifact):
            self.run_reconcile()
        self.assertEqual(self.staged, [])
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
