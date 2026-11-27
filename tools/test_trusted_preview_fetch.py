import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.preview_artifact import InvalidPreviewArtifact
from tools.test_trusted_receipt import PR, WORKFLOW_INFO, RUN, ARTIFACT, RECEIPT, BASE
from tools.trusted_preview_fetch import download_trusted_preview


class TrustedFetchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pr = copy.deepcopy(PR)
        self.pr['base'].update(ref='main')
        self.pr['base']['repo']['full_name'] = 'owner/repo'
        self.run = copy.deepcopy(RUN)
        self.run.update(created_at='2026-11-21T00:00:00Z', run_started_at='2026-11-21T00:00:00Z')
        self.receipt = copy.deepcopy(ARTIFACT)
        self.preview = {'id': 34, 'name': 'trusted-wiki-preview-7-11-1', 'expired': False,
                        'size_in_bytes': 500, 'workflow_run': copy.deepcopy(ARTIFACT['workflow_run'])}
        self.review = {'head': 'a' * 40, 'approved': True}
        self.count = 0

    def api(self, path, paginate=False):
        if path.endswith('/pulls/7'): return copy.deepcopy(self.pr)
        if path.endswith('/branches/main'): return {'name': 'main', 'commit': {'sha': BASE}}
        if path.endswith('/actions/workflows/wiki-trusted-data.yml'): return copy.deepcopy(WORKFLOW_INFO)
        if path.endswith('/actions/runs/11'): return copy.deepcopy(self.run)
        if '/actions/runs/11/artifacts?' in path:
            return [{'total_count': 2, 'artifacts': copy.deepcopy([self.receipt, self.preview])}]
        if '/wiki-trusted-data.yml/runs?' in path:
            return [{'total_count': 1, 'workflow_runs': [copy.deepcopy(self.run)]}]
        raise AssertionError(path)

    def download(self, repo, identifier, path):
        if identifier == 33:
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('trusted-check-receipt.json', json.dumps(dict(RECEIPT, version=2, workflow_sha=BASE)))
        elif identifier == 34:
            Path(path).write_bytes(b'fixture wrapper, not yet extracted')
        else:
            raise AssertionError(identifier)

    def execute(self, name='out.zip', base=BASE):
        with patch('tools.trusted_preview_fetch.gh_api', side_effect=self.api), \
             patch('tools.trusted_preview_fetch.snapshot', side_effect=lambda *a: self.review), \
             patch('tools.trusted_preview_fetch.download_artifact', side_effect=self.download):
            return download_trusted_preview('owner/repo', 7, 11, base, self.root / name)

    def test_downloads_current_receipt_bound_artifact(self):
        self.assertEqual(self.execute(), (34, 'a' * 40, BASE, 11, 1))
        self.assertEqual((self.root / 'out.zip').read_bytes(), b'fixture wrapper, not yet extracted')

    def test_review_and_pin_are_required(self):
        self.review['approved'] = False
        with self.assertRaises(InvalidPreviewArtifact): self.execute()
        self.assertFalse((self.root / 'out.zip').exists())
        self.review['approved'] = True
        with self.assertRaises(InvalidPreviewArtifact): self.execute(base='c' * 40)

    def test_change_during_download_leaves_no_output(self):
        old = self.download
        def download(repo, identifier, path):
            old(repo, identifier, path)
            if identifier == 34:
                self.preview['expired'] = True
        with patch.object(self, 'download', side_effect=download):
            with self.assertRaises(InvalidPreviewArtifact): self.execute()
        self.assertFalse((self.root / 'out.zip').exists())
        self.assertFalse(list(self.root.glob('.trusted-download-*')))

    def test_receipt_identity_and_pr_state_are_rechecked(self):
        original_download = self.download
        for change in ('receipt', 'closed'):
            self.receipt = copy.deepcopy(ARTIFACT)
            self.pr['state'] = 'open'
            def download(repo, identifier, path):
                original_download(repo, identifier, path)
                if identifier == 34:
                    if change == 'receipt': self.receipt['id'] = 35
                    else: self.pr['state'] = 'closed'
            with self.subTest(change=change), patch.object(self, 'download', side_effect=download):
                with self.assertRaises(InvalidPreviewArtifact): self.execute(name=change + '.zip')
            self.assertFalse((self.root / (change + '.zip')).exists())

    def test_concurrent_destination_is_never_overwritten(self):
        destination = self.root / 'out.zip'
        real_link = os.link
        def competing_link(source, target):
            destination.write_bytes(b'other writer')
            return real_link(source, target)
        with patch('tools.trusted_preview_fetch.os.link', side_effect=competing_link):
            with self.assertRaises(InvalidPreviewArtifact):
                self.execute()
        self.assertEqual(destination.read_bytes(), b'other writer')
        self.assertFalse(list(self.root.glob('.trusted-download-*')))


if __name__ == '__main__':
    unittest.main()
