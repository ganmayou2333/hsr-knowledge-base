import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.preview_artifact import InvalidPreviewArtifact, MAX_ARCHIVE_BYTES
from tools.test_trusted_receipt import PR, WORKFLOW_INFO, RUN, ARTIFACT, RECEIPT
from tools.trusted_preview_artifact import select_trusted_preview


class TrustedPreviewArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.receipt_zip = Path(self.temp.name) / 'receipt.zip'
        with zipfile.ZipFile(self.receipt_zip, 'w') as archive:
            archive.writestr('trusted-check-receipt.json', json.dumps(RECEIPT))
        self.pr, self.workflow, self.run, self.receipt = map(copy.deepcopy, (PR, WORKFLOW_INFO, RUN, ARTIFACT))
        self.preview = {'id': 34, 'name': 'trusted-wiki-preview-7-11-1', 'expired': False,
                        'size_in_bytes': 500, 'workflow_run': copy.deepcopy(ARTIFACT['workflow_run'])}
        self.items = [self.receipt, self.preview]

    def select(self):
        return select_trusted_preview(7, self.pr, self.workflow, self.run, self.receipt, self.receipt_zip, self.items)

    def test_matches_receipt_and_preview_to_same_run_without_pr_association(self):
        self.assertEqual(self.select(), (34, 'a' * 40, 'b' * 40, 11, 1))

    def test_rejects_invalid_preview_metadata(self):
        for key, value in [('id', True), ('id', 33), ('expired', True), ('size_in_bytes', True),
                           ('size_in_bytes', 0), ('size_in_bytes', MAX_ARCHIVE_BYTES + 1),
                           ('name', 'trusted-wiki-preview-7-11-2')]:
            with self.subTest(key=key, value=value):
                old = self.preview[key]
                self.preview[key] = value
                with self.assertRaises(InvalidPreviewArtifact): self.select()
                self.preview[key] = old

    def test_rejects_wrong_run_repo_or_head(self):
        for key, value in [('id', 12), ('repository_id', True), ('repository_id', 2),
                           ('head_repository_id', 1), ('head_repository_id', True), ('head_sha', 'c' * 40)]:
            with self.subTest(key=key, value=value):
                old = self.preview['workflow_run'][key]
                self.preview['workflow_run'][key] = value
                with self.assertRaises(InvalidPreviewArtifact): self.select()
                self.preview['workflow_run'][key] = old

    def test_rejects_incomplete_or_ambiguous_artifact_lists(self):
        other = copy.deepcopy(self.preview)
        other['id'] = 35
        for items in ([self.preview], [self.receipt], [self.receipt, self.preview, other],
                      [self.receipt, self.preview, self.preview]):
            with self.subTest(count=len(items)):
                self.items = items
                with self.assertRaises(InvalidPreviewArtifact): self.select()

    def test_rejects_stale_receipt_even_when_preview_looks_valid(self):
        self.pr['state'] = 'closed'
        with self.assertRaises(InvalidPreviewArtifact): self.select()
        self.pr['state'] = 'open'
        self.run['run_attempt'] = 2
        with self.assertRaises(InvalidPreviewArtifact): self.select()


if __name__ == '__main__': unittest.main()
