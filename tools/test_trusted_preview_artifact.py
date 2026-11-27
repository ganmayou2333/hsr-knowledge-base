import copy
import base64
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.preview_artifact import InvalidPreviewArtifact, MAX_ARCHIVE_BYTES, extract_preview_zip
from tools.preview_bundle import build_bundle
from tools.stage_preview import unwrap_artifact
from tools.trusted_preview_build import build
from tools.test_trusted_receipt import PR, WORKFLOW_INFO, RUN, ARTIFACT, RECEIPT
from tools.trusted_preview_artifact import select_trusted_preview


class TrustedPreviewArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.receipt_zip = Path(self.temp.name) / 'receipt.zip'
        with zipfile.ZipFile(self.receipt_zip, 'w') as archive:
            archive.writestr('trusted-check-receipt.json', json.dumps(dict(RECEIPT, version=2, workflow_sha='b' * 40)))
        self.pr, self.workflow, self.run, self.receipt = map(copy.deepcopy, (PR, WORKFLOW_INFO, RUN, ARTIFACT))
        self.run['run_started_at'] = '2026-11-21T00:00:00Z'
        self.run['created_at'] = '2026-11-21T00:00:00Z'
        self.runs = [copy.deepcopy(self.run)]
        self.preview = {'id': 34, 'name': 'trusted-wiki-preview-7-11-1', 'expired': False,
                        'size_in_bytes': 500, 'workflow_run': copy.deepcopy(ARTIFACT['workflow_run'])}
        self.items = [self.receipt, self.preview]

    def select(self):
        return select_trusted_preview(7, self.pr, self.workflow, self.run, self.receipt, self.receipt_zip, self.items, self.runs)

    def test_matches_receipt_and_preview_to_same_run_without_pr_association(self):
        self.assertEqual(self.select(), (34, 'a' * 40, 'b' * 40, 11, 1))

    def test_legacy_receipt_cannot_bind_trusted_preview(self):
        with zipfile.ZipFile(self.receipt_zip, 'w') as archive:
            archive.writestr('trusted-check-receipt.json', json.dumps(RECEIPT))
        with self.assertRaises(InvalidPreviewArtifact): self.select()

    def test_local_trusted_build_receipt_wrapper_and_inert_bundle(self):
        # Local fixtures only: this does not establish real GitHub provenance,
        # ordinary check status, external approval, or publication eligibility.
        root = Path(self.temp.name)
        source = root / 'input'
        (source / 'zh_cn').mkdir(parents=True)
        (source / 'zh_cn' / 'example.md').write_text('# Trusted build fixture\n', encoding='utf-8')
        (source / 'poison.py').write_text('raise RuntimeError("PR code executed")', encoding='utf-8')
        build(source, Path(__file__).resolve().parent.parent, root / 'wiki-preview.zip')
        with zipfile.ZipFile(root / 'artifact.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(root / 'wiki-preview.zip', 'wiki-preview.zip')
        self.preview['size_in_bytes'] = (root / 'artifact.zip').stat().st_size
        artifact_id, head, base, run_id, attempt = self.select()
        self.assertEqual(artifact_id, 34)
        unwrap_artifact(root / 'artifact.zip', root / 'inner.zip')
        extract_preview_zip(root / 'inner.zip', root / 'site')
        build_bundle(root / 'site', root / 'bundle', repo='owner/repo', pr=7, head=head, base=base,
                     run=10, run_attempt=1, trusted_run=run_id, trusted_attempt=attempt)
        manifest = json.loads((root / 'bundle' / 'manifest.json').read_text(encoding='ascii'))
        self.assertEqual((manifest['trusted_run'], manifest['trusted_attempt']), (11, 1))
        digest = manifest['files']['pages/example.html']
        obj = json.loads((root / 'bundle' / 'objects' / (digest + '.json')).read_text(encoding='ascii'))
        self.assertIn(b'Trusted build fixture', base64.b64decode(obj['data'], validate=True))
        self.assertNotIn('poison.py', manifest['files'])

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
        duplicate_receipt = copy.deepcopy(self.receipt)
        duplicate_receipt['id'] = 36
        for items in ([self.preview], [self.receipt], [self.receipt, self.preview, other],
                      [self.receipt, self.preview, self.preview],
                      [self.receipt, self.preview, duplicate_receipt]):
            with self.subTest(count=len(items)):
                self.items = items
                with self.assertRaises(InvalidPreviewArtifact): self.select()

    def test_rejects_stale_receipt_even_when_preview_looks_valid(self):
        self.pr['state'] = 'closed'
        with self.assertRaises(InvalidPreviewArtifact): self.select()
        self.pr['state'] = 'open'
        self.run['run_attempt'] = 2
        with self.assertRaises(InvalidPreviewArtifact): self.select()

    def test_newer_same_head_run_blocks_even_without_pr_association(self):
        for status, conclusion in [('completed', 'failure'), ('in_progress', None), ('completed', 'success')]:
            newer = dict(self.run, id=12, created_at='2026-11-21T00:01:00Z', run_started_at='2026-11-21T00:01:00Z',
                         status=status, conclusion=conclusion, pull_requests=[])
            self.runs = [copy.deepcopy(self.run), newer]
            with self.subTest(status=status, conclusion=conclusion), self.assertRaises(InvalidPreviewArtifact):
                self.select()

    def test_rerun_duplicate_and_incomplete_run_lists_fail_closed(self):
        for runs in ([], [self.run, copy.deepcopy(self.run)],
                     [dict(self.run, run_attempt=2)], [dict(self.run, status='in_progress', conclusion=None)],
                     [dict(self.run, run_started_at=None)]):
            self.runs = runs
            with self.subTest(runs=runs), self.assertRaises(InvalidPreviewArtifact): self.select()

    def test_old_successful_rerun_does_not_hide_newer_failed_run(self):
        old = dict(self.run, run_started_at='2026-11-21T00:02:00Z')
        newer = dict(self.run, id=12, created_at='2026-11-21T00:01:00Z',
                     run_started_at='2026-11-21T00:01:00Z', conclusion='failure')
        self.runs = [old, newer]
        with self.assertRaises(InvalidPreviewArtifact): self.select()
        old['conclusion'], newer['conclusion'] = 'failure', 'success'
        self.run = newer
        self.run['id'] = 11
        newer['id'], old['id'] = 11, 12
        with self.assertRaises(InvalidPreviewArtifact): self.select()


if __name__ == '__main__': unittest.main()
