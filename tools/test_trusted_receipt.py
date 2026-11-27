import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.preview_artifact import InvalidPreviewArtifact
from tools.trusted_receipt import WORKFLOW, validate_receipt

HEAD, BASE = 'a' * 40, 'b' * 40
PR = {'number': 7, 'state': 'open', 'head': {'sha': HEAD, 'repo': {'id': 2}},
      'base': {'sha': BASE, 'repo': {'id': 1}}}
WORKFLOW_INFO = {'id': 42, 'state': 'active', 'path': WORKFLOW}
RUN = {'id': 11, 'run_attempt': 1, 'workflow_id': 42, 'repository': {'id': 1},
       'head_repository': {'id': 2}, 'event': 'pull_request_target', 'path': WORKFLOW, 'status': 'completed',
       'conclusion': 'success', 'head_sha': HEAD, 'pull_requests': []}
ARTIFACT = {'id': 33, 'name': 'trusted-check-receipt-7-11-1', 'expired': False,
            'size_in_bytes': 200, 'workflow_run': {'id': 11, 'repository_id': 1, 'head_repository_id': 2, 'head_sha': HEAD}}
RECEIPT = {'version': 1, 'pr': 7, 'head': HEAD, 'base': BASE, 'head_repo': 2,
           'base_repo': 1, 'run': 11, 'attempt': 1}


class TrustedReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.wrapper = Path(self.temp.name) / 'receipt.zip'
        self.pr, self.workflow = copy.deepcopy(PR), copy.deepcopy(WORKFLOW_INFO)
        self.run, self.artifact = copy.deepcopy(RUN), copy.deepcopy(ARTIFACT)
        self.write(json.dumps(RECEIPT))

    def write(self, data, name='trusted-check-receipt.json', extra=False):
        with zipfile.ZipFile(self.wrapper, 'w') as archive:
            archive.writestr(name, data)
            if extra:
                archive.writestr('extra', 'unexpected')

    def validate(self):
        return validate_receipt(7, self.pr, self.workflow, self.run, self.artifact, self.wrapper)

    def test_valid_fork_receipt_does_not_need_run_pr_associations(self):
        self.assertEqual(self.validate(), (11, 1))

    def test_v2_binds_workflow_revision_to_base_while_v1_remains_legacy_only(self):
        with self.assertRaises(InvalidPreviewArtifact):
            validate_receipt(7, self.pr, self.workflow, self.run, self.artifact, self.wrapper,
                             require_workflow_sha=True)
        self.write(json.dumps(dict(RECEIPT, version=2, workflow_sha=BASE)))
        self.assertEqual(validate_receipt(7, self.pr, self.workflow, self.run, self.artifact, self.wrapper,
                                          require_workflow_sha=True), (11, 1))
        for value in ('c' * 40, '', True, None):
            self.write(json.dumps(dict(RECEIPT, version=2, workflow_sha=value)))
            with self.subTest(workflow_sha=value), self.assertRaises(InvalidPreviewArtifact):
                self.validate()

    def test_same_repository_receipt_is_accepted_only_while_open(self):
        self.pr['head']['repo']['id'] = 1
        self.run['head_repository']['id'] = 1
        self.artifact['workflow_run']['head_repository_id'] = 1
        self.write(json.dumps(dict(RECEIPT, head_repo=1)))
        self.assertEqual(self.validate(), (11, 1))
        self.pr['state'] = 'closed'
        with self.assertRaises(InvalidPreviewArtifact):
            self.validate()

    def test_rejects_stale_pr_and_other_workflow_runs(self):
        for target, field, value in [(self.pr, 'state', 'closed'), (self.run, 'status', 'in_progress'),
                                     (self.run, 'conclusion', 'failure'), (self.run, 'event', 'pull_request'),
                                     (self.run, 'run_attempt', 2), (self.workflow, 'id', 43),
                                     (self.artifact, 'expired', True), (self.artifact, 'name', 'different')]:
            with self.subTest(field=field, value=value):
                old = target[field]
                target[field] = value
                with self.assertRaises(InvalidPreviewArtifact):
                    self.validate()
                target[field] = old
        self.pr['base']['sha'] = 'c' * 40
        with self.assertRaises(InvalidPreviewArtifact):
            self.validate()

    def test_rejects_forged_contents_and_archive(self):
        for raw, name, extra in [(json.dumps(dict(RECEIPT, pr=8)), 'trusted-check-receipt.json', False),
                                 (json.dumps(dict(RECEIPT, head_repo=True)), 'trusted-check-receipt.json', False),
                                 ('{"version":1,"version":1}', 'trusted-check-receipt.json', False),
                                 (json.dumps(RECEIPT), '../trusted-check-receipt.json', False),
                                 (json.dumps(RECEIPT), 'trusted-check-receipt.json', True),
                                 ('x' * 8193, 'trusted-check-receipt.json', False)]:
            with self.subTest(name=name, extra=extra, length=len(raw)):
                self.write(raw, name, extra)
                with self.assertRaises(InvalidPreviewArtifact):
                    self.validate()

    def test_rejects_unsupported_or_corrupt_compressed_receipts(self):
        with zipfile.ZipFile(self.wrapper, 'w', compression=zipfile.ZIP_BZIP2) as archive:
            archive.writestr('trusted-check-receipt.json', json.dumps(RECEIPT))
        with self.assertRaises(InvalidPreviewArtifact):
            self.validate()

        with zipfile.ZipFile(self.wrapper, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('trusted-check-receipt.json', json.dumps(RECEIPT))
        data = bytearray(self.wrapper.read_bytes())
        with zipfile.ZipFile(self.wrapper) as archive:
            info = archive.infolist()[0]
            start = info.header_offset + 30 + len(info.filename.encode('utf-8')) + len(info.extra)
        data[start] = 0xff  # Invalid DEFLATE block type.
        self.wrapper.write_bytes(data)
        with self.assertRaises(InvalidPreviewArtifact):
            self.validate()

    def test_rejects_artifact_from_other_run_or_repository(self):
        for field, value in [('id', 12), ('repository_id', 3), ('head_sha', 'c' * 40)]:
            with self.subTest(field=field):
                old = self.artifact['workflow_run'][field]
                self.artifact['workflow_run'][field] = value
                with self.assertRaises(InvalidPreviewArtifact):
                    self.validate()
                self.artifact['workflow_run'][field] = old

    def test_rejects_other_or_invalid_head_repository_provenance(self):
        for target, field in ((self.run['head_repository'], 'id'),
                              (self.artifact['workflow_run'], 'head_repository_id')):
            for value in (1, 3, True, None):
                with self.subTest(field=field, value=value):
                    old = target[field]
                    target[field] = value
                    with self.assertRaises(InvalidPreviewArtifact):
                        self.validate()
                    target[field] = old

    def test_rejects_boolean_metadata_even_when_equal_to_numeric_id(self):
        for target, field in [(self.run['repository'], 'id'),
                              (self.artifact['workflow_run'], 'repository_id')]:
            with self.subTest(field=field):
                old = target[field]
                target[field] = True
                with self.assertRaises(InvalidPreviewArtifact):
                    self.validate()
                target[field] = old


if __name__ == '__main__':
    unittest.main()
