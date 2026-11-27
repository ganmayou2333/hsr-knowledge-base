"""Validate a trusted-check receipt; this module does not authorize publication.

The caller must fetch the artifact metadata from GitHub and download the ZIP by
that artifact's ID. PR build artifacts remain untrusted and need their own
independent binding to the PR. Do not use a receipt as proof of build origin.
"""
import json
import re
import stat
import zipfile
import zlib
from pathlib import Path

from tools.preview_artifact import InvalidPreviewArtifact, check_zip_directory

SHA = re.compile(r'^[0-9a-f]{40}$')
WORKFLOW = '.github/workflows/wiki-trusted-data.yml'
MAX_WRAPPER = 65536
MAX_RECEIPT = 8192


def _positive(value):
    return type(value) is int and value > 0


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate field')
        result[key] = value
    return result


def validate_receipt(number, pr, workflow, run, artifact, wrapper):
    """Validate the current PR, trusted run, artifact metadata and downloaded ZIP.

    GitHub's artifact association is the provenance boundary. The caller must
    obtain the wrapper by the validated artifact ID from GitHub, over its API.
    All arguments must be refreshed when enforcing freshness or review status.
    """
    try:
        head, base = pr['head']['sha'], pr['base']['sha']
        head_id, base_id = pr['head']['repo']['id'], pr['base']['repo']['id']
        run_id, attempt = run['id'], run['run_attempt']
        if (not _positive(number) or not _positive(pr['number']) or pr['number'] != number or pr['state'] != 'open'
                or not isinstance(head, str) or not SHA.fullmatch(head)
                or not isinstance(base, str) or not SHA.fullmatch(base)
                or not all(map(_positive, (head_id, base_id, run_id, attempt, workflow['id'])))
                or workflow['state'] != 'active' or workflow['path'] != WORKFLOW
                or not _positive(run['workflow_id']) or not _positive(run['repository']['id'])
                or run['workflow_id'] != workflow['id'] or run['repository']['id'] != base_id
                or run['event'] != 'pull_request_target' or run['path'] != WORKFLOW
                or run['status'] != 'completed' or run['conclusion'] != 'success'
                or run['head_sha'] != head):
            raise ValueError('invalid trusted run')
        origin = artifact['workflow_run']
        if (artifact['name'] != f'trusted-check-receipt-{number}-{run_id}-{attempt}'
                or not _positive(artifact['id']) or artifact['expired'] is not False
                or not _positive(artifact['size_in_bytes']) or artifact['size_in_bytes'] > MAX_WRAPPER
                or not _positive(origin['id']) or not _positive(origin['repository_id'])
                or origin['id'] != run_id or origin['repository_id'] != base_id
                or origin['head_sha'] != head):
            raise ValueError('invalid artifact')
        with Path(wrapper).open('rb') as handle:
            size = handle.seek(0, 2)
            if size > MAX_WRAPPER:
                raise ValueError('oversized wrapper')
            check_zip_directory(handle, size)
            with zipfile.ZipFile(handle) as archive:
                entries = archive.infolist()
                if len(entries) != 1:
                    raise ValueError('invalid member count')
                info = entries[0]
                kind = stat.S_IFMT(info.external_attr >> 16)
                if (info.orig_filename != 'trusted-check-receipt.json' or info.is_dir()
                        or kind not in (0, stat.S_IFREG) or info.flag_bits & 1
                        or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                        or info.file_size > MAX_RECEIPT):
                    raise ValueError('invalid member')
                with archive.open(info) as data:
                    raw = data.read(MAX_RECEIPT + 1)
                if len(raw) != info.file_size or len(raw) > MAX_RECEIPT:
                    raise ValueError('invalid receipt size')
        receipt = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object)
        expected = {'version': 1, 'pr': number, 'head': head, 'base': base,
                    'head_repo': head_id, 'base_repo': base_id, 'run': run_id, 'attempt': attempt}
        if not isinstance(receipt, dict) or receipt != expected:
            raise ValueError('receipt does not match')
        if any(type(receipt[key]) is not int for key in ('version', 'pr', 'head_repo', 'base_repo', 'run', 'attempt')):
            raise ValueError('invalid numeric fields')
        return run_id, attempt
    except (KeyError, TypeError, ValueError, AttributeError, OSError, EOFError, zlib.error, zipfile.BadZipFile):
        raise InvalidPreviewArtifact('Trusted check receipt is invalid or stale') from None
