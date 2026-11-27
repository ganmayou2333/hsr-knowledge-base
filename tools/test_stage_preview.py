"""The staging gate treats GitHub metadata and downloaded ZIPs as untrusted."""
import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.package_preview import package_site
from tools.preview_artifact import InvalidPreviewArtifact
from tools.stage_preview import select_artifact, stage, trusted_check, unwrap_artifact

HEAD, BASE = 'a' * 40, 'b' * 40
PR = {'number': 7, 'state': 'open', 'head': {'sha': HEAD, 'repo': {'id': 1}},
      'base': {'sha': BASE, 'ref': 'main', 'repo': {'id': 1, 'full_name': 'owner/repo'}}}
RUN = {'id': 10, 'repository': {'id': 1}, 'event': 'pull_request', 'status': 'completed',
       'conclusion': 'success', 'path': '.github/workflows/wiki-quality.yml', 'head_sha': HEAD, 'run_attempt': 1,
       'created_at': '2026-11-21T00:00:00Z', 'run_started_at': '2026-11-21T00:00:00Z',
       'pull_requests': [{'number': 7, 'head': {'sha': HEAD, 'repo': {'id': 1}},
                          'base': {'sha': BASE, 'repo': {'id': 1}}}]}
ARTIFACT = {'id': 20, 'name': f'wiki-preview-7-{HEAD}-1', 'expired': False, 'size_in_bytes': 123,
            'workflow_run': {'id': 10, 'repository_id': 1, 'head_repository_id': 1, 'head_sha': HEAD}}
WORKFLOW = {'id': 42, 'state': 'active', 'path': '.github/workflows/wiki-trusted-data.yml'}
TRUSTED_RUN = {'id': 11, 'workflow_id': 42, 'repository': {'id': 1}, 'event': 'pull_request_target',
               'status': 'completed', 'conclusion': 'success', 'path': WORKFLOW['path'], 'head_sha': HEAD,
               'run_attempt': 1, 'created_at': '2026-11-21T00:00:01Z', 'run_started_at': '2026-11-21T00:00:01Z', 'pull_requests': copy.deepcopy(RUN['pull_requests'])}


def responses(pr=PR, run=RUN, pages=None, trusted=TRUSTED_RUN):
    return [pr, {'name': 'main', 'commit': {'sha': BASE}}, run, [{'total_count': 1, 'artifacts': [ARTIFACT]}] if pages is None else pages, WORKFLOW, trusted,
            [{'total_count': 1, 'workflow_runs': [run]}], [{'total_count': 1, 'workflow_runs': [trusted]}]]


class StagingTests(unittest.TestCase):
    def select(self, pr=PR, run=RUN, pages=None, approved=False):
        return select_artifact('owner/repo', 7, 10, pr, run,
                               [{'total_count': 1, 'artifacts': [ARTIFACT]}] if pages is None else pages, approved)

    def test_matching_metadata(self):
        self.assertEqual(self.select(), (20, HEAD, BASE))
        old = dict(ARTIFACT, id=19, name=f'wiki-preview-7-{HEAD}-1')
        current = dict(ARTIFACT, id=21, name=f'wiki-preview-7-{HEAD}-2')
        self.assertEqual(self.select(run=dict(RUN, run_attempt=2), pages=[{'total_count': 2, 'artifacts': [old, current]}]),
                         (21, HEAD, BASE))

    def test_artifact_pagination_cap_and_duplicate_ids_fail_closed(self):
        others = [{'id': 1000 + i, 'name': f'unrelated-{i}'} for i in range(998)]
        self.assertEqual(self.select(pages=[{'total_count': 999, 'artifacts': [ARTIFACT, *others]}])[0], 20)
        with self.assertRaises(InvalidPreviewArtifact):
            self.select(pages=[{'total_count': 1000, 'artifacts': [ARTIFACT, *others, {'id': 9999, 'name': 'extra'}]}])
        with self.assertRaises(InvalidPreviewArtifact):
            self.select(pages=[{'total_count': 2, 'artifacts': [ARTIFACT, {'id': 20, 'name': 'other'}]}])
        for pages in ([{'artifacts': [ARTIFACT]}], [{'total_count': 2, 'artifacts': [ARTIFACT]}],
                      [{'total_count': True, 'artifacts': [ARTIFACT]}],
                      [{'total_count': 1, 'artifacts': [ARTIFACT]}, {'total_count': 2, 'artifacts': []}]):
            with self.subTest(pages=pages), self.assertRaises(InvalidPreviewArtifact):
                self.select(pages=pages)

    def test_stale_failed_or_unmatched_inputs_are_rejected(self):
        cases = []
        for field, value in [('state', 'closed'), ('number', 8)]:
            pr = copy.deepcopy(PR); pr[field] = value; cases.append((pr, RUN, None))
        pr = copy.deepcopy(PR); pr['base']['sha'] = 'c' * 40; cases.append((pr, RUN, None))
        for field, value in [('head_sha', 'c' * 40), ('conclusion', 'failure'), ('status', 'in_progress'),
                             ('event', 'push'), ('path', '.github/workflows/other.yml'), ('run_attempt', 2)]:
            run = copy.deepcopy(RUN); run[field] = value; cases.append((PR, run, None))
        for field, value in [('expired', True), ('name', 'wrong'), ('size_in_bytes', 0)]:
            item = copy.deepcopy(ARTIFACT); item[field] = value; cases.append((PR, RUN, [{'total_count': 1, 'artifacts': [item]}]))
        item = copy.deepcopy(ARTIFACT); item['workflow_run']['id'] = 11; cases.append((PR, RUN, [{'total_count': 1, 'artifacts': [item]}]))
        cases.append((PR, RUN, [{'total_count': 2, 'artifacts': [ARTIFACT, ARTIFACT]}]))
        for pr, run, pages in cases:
            with self.subTest(pr=pr, run=run, pages=pages), self.assertRaises(InvalidPreviewArtifact):
                self.select(pr, run, pages)

    def test_external_pr_requires_current_authorized_approval(self):
        pr, run, artifact = copy.deepcopy(PR), copy.deepcopy(RUN), copy.deepcopy(ARTIFACT)
        pr['head']['repo']['id'] = run['pull_requests'][0]['head']['repo']['id'] = 2
        artifact['workflow_run']['head_repository_id'] = 2
        pages = [{'total_count': 1, 'artifacts': [artifact]}]
        with self.assertRaises(InvalidPreviewArtifact): self.select(pr, run, pages)
        self.assertEqual(self.select(pr, run, pages, approved=True), (20, HEAD, BASE))
        self.assertRaises(InvalidPreviewArtifact, self.select, pr, run, pages, 'yes')

    def test_trusted_check_requires_current_successful_base_workflow(self):
        self.assertEqual(trusted_check(7, PR, WORKFLOW, TRUSTED_RUN, 11), (11, 1))
        for field, value in [('id', 12), ('workflow_id', 43), ('event', 'pull_request'),
                             ('status', 'in_progress'), ('conclusion', 'failure'),
                             ('head_sha', 'c' * 40), ('run_attempt', 0), ('pull_requests', [])]:
            run = copy.deepcopy(TRUSTED_RUN); run[field] = value
            with self.subTest(field=field), self.assertRaises(InvalidPreviewArtifact):
                trusted_check(7, PR, WORKFLOW, run, 11)
        run = copy.deepcopy(TRUSTED_RUN); run['pull_requests'][0]['base']['sha'] = 'c' * 40
        with self.assertRaises(InvalidPreviewArtifact): trusted_check(7, PR, WORKFLOW, run, 11)
        workflow = dict(WORKFLOW, state='disabled_manually')
        with self.assertRaises(InvalidPreviewArtifact): trusted_check(7, PR, workflow, TRUSTED_RUN, 11)

    def test_wrapper_rejects_other_members_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in ['../wiki-preview.zip', 'other.zip']:
                wrapper = root / 'input.zip'
                with zipfile.ZipFile(wrapper, 'w') as z: z.writestr(filename, b'data')
                with self.assertRaises(InvalidPreviewArtifact): unwrap_artifact(wrapper, root / 'out')
                wrapper.unlink()
            with zipfile.ZipFile(root / 'input.zip', 'w') as z:
                info = zipfile.ZipInfo('wiki-preview.zip'); info.create_system = 3; info.external_attr = 0o120777 << 16
                z.writestr(info, b'link')
            with self.assertRaises(InvalidPreviewArtifact): unwrap_artifact(root / 'input.zip', root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_wrapper_rejects_unsupported_compression(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for method in (zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA):
                with self.subTest(method=method):
                    with zipfile.ZipFile(root / 'input.zip', 'w', compression=method) as archive:
                        archive.writestr('wiki-preview.zip', b'not an inner zip')
                    with self.assertRaises(InvalidPreviewArtifact):
                        unwrap_artifact(root / 'input.zip', root / 'out')
                    self.assertFalse((root / 'out').exists())

    def test_staging_rechecks_metadata_and_leaves_no_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); wiki = root / 'wiki'; wiki.mkdir()
            (wiki / 'index.html').write_text('<h1>test</h1>', encoding='utf-8')
            for name in ('assets', 'data', 'pages'): (wiki / name).mkdir()
            package_site(wiki, root / 'inner.zip')
            with zipfile.ZipFile(root / 'wrapper.zip', 'w') as z: z.write(root / 'inner.zip', 'wiki-preview.zip')
            pages = [{'total_count': 1, 'artifacts': [ARTIFACT]}]
            def fake_download(repo, artifact_id, destination): Path(destination).write_bytes((root / 'wrapper.zip').read_bytes())
            good = responses(pages=pages)
            changed = copy.deepcopy(PR); changed['head']['sha'] = 'c' * 40
            with patch('tools.stage_preview.gh_api', side_effect=good * 3), patch('tools.stage_preview.download_artifact', side_effect=fake_download):
                stage('owner/repo', 7, 10, root / 'bundle', trusted_run_id=11)
            self.assertTrue((root / 'bundle' / 'manifest.json').is_file())
            manifest = json.loads((root / 'bundle' / 'manifest.json').read_text(encoding='ascii'))
            self.assertEqual((manifest['run_attempt'], manifest['trusted_run'], manifest['trusted_attempt']), (1, 11, 1))
            with patch('tools.stage_preview.gh_api', side_effect=good * 2 + responses(pr=changed, pages=pages)), patch('tools.stage_preview.download_artifact', side_effect=fake_download):
                with self.assertRaises(InvalidPreviewArtifact): stage('owner/repo', 7, 10, root / 'stale', trusted_run_id=11)
            self.assertFalse((root / 'stale').exists())
            rerun = dict(TRUSTED_RUN, run_attempt=2)
            with patch('tools.stage_preview.gh_api', side_effect=good * 2 + responses(pages=pages, trusted=rerun)), patch('tools.stage_preview.download_artifact', side_effect=fake_download):
                with self.assertRaises(InvalidPreviewArtifact): stage('owner/repo', 7, 10, root / 'rerun', trusted_run_id=11)
            self.assertFalse((root / 'rerun').exists())
            newer = dict(RUN, id=12, created_at='2026-11-21T00:01:00Z', run_started_at='2026-11-21T00:01:00Z', conclusion='failure')
            stale = responses(pages=pages)
            stale[6] = [{'total_count': 2, 'workflow_runs': [RUN, newer]}]
            with patch('tools.stage_preview.gh_api', side_effect=good * 2 + stale), patch('tools.stage_preview.download_artifact', side_effect=fake_download):
                with self.assertRaises(InvalidPreviewArtifact): stage('owner/repo', 7, 10, root / 'newer', trusted_run_id=11)
            self.assertFalse((root / 'newer').exists())
            pending = dict(TRUSTED_RUN, id=13, created_at='2026-11-21T00:01:00Z', run_started_at='2026-11-21T00:01:00Z', status='in_progress', conclusion=None)
            stale = responses(pages=pages)
            stale[7] = [{'total_count': 2, 'workflow_runs': [TRUSTED_RUN, pending]}]
            with patch('tools.stage_preview.gh_api', side_effect=good * 2 + stale), patch('tools.stage_preview.download_artifact', side_effect=fake_download):
                with self.assertRaises(InvalidPreviewArtifact): stage('owner/repo', 7, 10, root / 'pending', trusted_run_id=11)
            self.assertFalse((root / 'pending').exists())
            stale = responses(pages=pages)
            stale[1] = {'name': 'main', 'commit': {'sha': 'c' * 40}}
            with patch('tools.stage_preview.gh_api', side_effect=good * 2 + stale), patch('tools.stage_preview.download_artifact', side_effect=fake_download):
                with self.assertRaises(InvalidPreviewArtifact): stage('owner/repo', 7, 10, root / 'base-changed', trusted_run_id=11)
            self.assertFalse((root / 'base-changed').exists())

    def test_external_approval_revoked_during_conversion_leaves_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); wiki = root / 'wiki'; wiki.mkdir()
            (wiki / 'index.html').write_text('<h1>test</h1>', encoding='utf-8')
            for name in ('assets', 'data', 'pages'): (wiki / name).mkdir()
            package_site(wiki, root / 'inner.zip')
            with zipfile.ZipFile(root / 'wrapper.zip', 'w') as z: z.write(root / 'inner.zip', 'wiki-preview.zip')
            pr, run, artifact = copy.deepcopy(PR), copy.deepcopy(RUN), copy.deepcopy(ARTIFACT)
            pr['head']['repo']['id'] = run['pull_requests'][0]['head']['repo']['id'] = 2
            trusted_run = copy.deepcopy(TRUSTED_RUN)
            trusted_run['pull_requests'][0]['head']['repo']['id'] = 2
            artifact['workflow_run']['head_repository_id'] = 2
            api_responses = responses(pr, run, [{'total_count': 1, 'artifacts': [artifact]}], trusted_run) * 3
            approvals = [{'head': HEAD, 'approved': True}] * 2 + [{'head': HEAD, 'approved': False}]
            def fake_download(repo, artifact_id, destination): Path(destination).write_bytes((root / 'wrapper.zip').read_bytes())
            with patch('tools.stage_preview.gh_api', side_effect=api_responses), patch('tools.stage_preview.snapshot', side_effect=approvals), patch('tools.stage_preview.download_artifact', side_effect=fake_download):
                with self.assertRaises(InvalidPreviewArtifact): stage('owner/repo', 7, 10, root / 'revoked', trusted_run_id=11)
            self.assertFalse((root / 'revoked').exists())


if __name__ == '__main__': unittest.main()
