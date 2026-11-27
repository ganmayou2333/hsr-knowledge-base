import copy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.preview_artifact import InvalidPreviewArtifact
from tools.preview_bundle import build_bundle
from tools.test_reconcile_previews import BASE, BUILD, HEAD, PR, TRUSTED
from tools.verify_preview_publication import verify


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site = Path(self.tmp.name) / 'catalog'
        (self.site / 'previews').mkdir(parents=True)
        source = Path(self.tmp.name) / 'source'
        source.mkdir()
        (source / 'index.html').write_text('preview', encoding='utf-8')
        build_bundle(source, self.site / 'previews' / '7', repo='owner/repo', pr=7,
                     head=HEAD, base=BASE, run=10, run_attempt=1, trusted_run=11, trusted_attempt=1)
        self.pr = copy.deepcopy(PR)
        self.build = dict(copy.deepcopy(BUILD), run_attempt=1)
        self.trusted = copy.deepcopy(TRUSTED)
        self.review = {'head': HEAD, 'approved': True}

    def api(self, path, paginate=False):
        if path.endswith('/pulls/7'):
            return copy.deepcopy(self.pr)
        if '/wiki-quality.yml/runs?' in path:
            return [{'total_count': 1, 'workflow_runs': [self.build]}]
        if '/wiki-trusted-data.yml/runs?' in path:
            return [{'total_count': 1, 'workflow_runs': [self.trusted]}]
        raise AssertionError(path)

    def run_verify(self, metadata=True):
        with patch('tools.verify_preview_publication.gh_api', side_effect=self.api), \
                patch('tools.verify_preview_publication.metadata', return_value=metadata), \
                patch('tools.verify_preview_publication.snapshot', return_value=self.review):
            return verify('owner/repo', self.site)

    def test_current_catalog_passes(self):
        self.assertEqual(self.run_verify(), 1)

    def test_new_or_failed_check_rejects_old_preview(self):
        for change in ({'id': 12}, {'run_attempt': 2}, {'conclusion': 'failure'}, {'status': 'in_progress'}):
            original = self.build.copy()
            self.build.update(change)
            with self.subTest(change=change), self.assertRaises(InvalidPreviewArtifact):
                self.run_verify()
            self.build = original

    def test_revoked_external_approval_and_stale_metadata_fail_closed(self):
        self.pr['head']['repo']['id'] = 2
        self.review['approved'] = False
        with self.assertRaises(InvalidPreviewArtifact):
            self.run_verify()
        self.review['approved'] = True
        with self.assertRaises(InvalidPreviewArtifact):
            self.run_verify(metadata=False)

    def test_metadata_changes_during_verification_and_api_failure_abort(self):
        with patch('tools.verify_preview_publication.gh_api', side_effect=self.api), \
                patch('tools.verify_preview_publication.metadata', side_effect=[True, False]), \
                self.assertRaises(InvalidPreviewArtifact):
            verify('owner/repo', self.site)
        with patch('tools.verify_preview_publication.gh_api', side_effect=subprocess.CalledProcessError(1, 'gh')), \
                self.assertRaises(subprocess.CalledProcessError):
            verify('owner/repo', self.site)


if __name__ == '__main__':
    unittest.main()
