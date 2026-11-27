"""Correlate a trusted-build artifact with a verified same-run check receipt.

This is a provenance building block, NOT publication authorization. The caller
must verify that the run actually used the reviewed producer workflow at the
expected base, validate all checks and approval, and refresh state around every
staging step. This conservative head-wide freshness gate can omit valid PRs.
Fetch metadata and each ZIP by its unique artifact ID directly from GitHub.
"""
from tools.preview_artifact import MAX_ARCHIVE_BYTES, InvalidPreviewArtifact
from tools.reconcile_previews import MAX_RUNS
from tools.trusted_receipt import validate_receipt
from datetime import datetime


def select_trusted_preview(number, pr, workflow, run, receipt_artifact, receipt_zip, artifacts, runs):
    """Return preview ID, head and base after local receipt and metadata checks.

    `artifacts` must be a complete, freshly fetched list from this run, not a
    caller-selected subset. `runs` must likewise contain every freshly fetched
    run of this workflow for the head, including failures and in-progress runs.
    All same-head runs block older ones even if they belong to a different PR:
    an empty GitHub association cannot safely establish their PR identity.
    This function never opens or trusts the preview ZIP.
    """
    run_id, attempt = validate_receipt(number, pr, workflow, run, receipt_artifact, receipt_zip)
    try:
        if not isinstance(runs, list) or not runs or len(runs) >= MAX_RUNS:
            raise ValueError
        candidates, seen = [], set()
        for item in runs:
            if item['event'] != 'pull_request_target' or item['path'] != workflow['path'] or item['head_sha'] != pr['head']['sha']:
                raise ValueError
            identifier, created, started = item['id'], item['created_at'], item['run_started_at']
            if (type(identifier) is not int or identifier < 1 or identifier in seen
                    or any(not isinstance(value, str) or len(value) != 20 or not value.endswith('Z')
                           for value in (created, started))):
                raise ValueError
            datetime.strptime(created, '%Y-%m-%dT%H:%M:%SZ')
            datetime.strptime(started, '%Y-%m-%dT%H:%M:%SZ')
            if started < created or item['status'] != 'completed':
                raise ValueError
            seen.add(identifier)
            candidates.append((created, identifier, item))
        if len({item[0] for item in candidates}) != len(candidates):
            raise ValueError
        latest = max(candidates, key=lambda item: (item[0], item[1]))[2]
        started = max(item[2]['run_started_at'] for item in candidates)
        if latest['run_started_at'] != started or sum(item[2]['run_started_at'] == started for item in candidates) != 1:
            raise ValueError
        if (latest['id'] != run_id or type(latest['run_attempt']) is not int or latest['run_attempt'] != attempt
                or latest['status'] != 'completed' or latest['conclusion'] != 'success'):
            raise ValueError
        if not isinstance(artifacts, list) or len(artifacts) > 1000:
            raise ValueError
        ids = []
        for item in artifacts:
            identifier = item['id']
            if type(identifier) is not int or identifier < 1:
                raise ValueError
            ids.append(identifier)
        if len(set(ids)) != len(ids) or ids.count(receipt_artifact['id']) != 1:
            raise ValueError
        matching_receipts = [item for item in artifacts if item['id'] == receipt_artifact['id']]
        if (matching_receipts != [receipt_artifact]
                or sum(item['name'] == receipt_artifact['name'] for item in artifacts) != 1):
            raise ValueError
        expected = f'trusted-wiki-preview-{number}-{run_id}-{attempt}'
        matches = [item for item in artifacts if item['name'] == expected]
        if len(matches) != 1:
            raise ValueError
        artifact = matches[0]
        origin = artifact['workflow_run']
        if (artifact['id'] == receipt_artifact['id'] or artifact['expired'] is not False
                or type(artifact['size_in_bytes']) is not int
                or not 0 < artifact['size_in_bytes'] <= MAX_ARCHIVE_BYTES
                or type(origin['id']) is not int or origin['id'] != run_id
                or type(origin['repository_id']) is not int or origin['repository_id'] != pr['base']['repo']['id']
                or type(origin['head_repository_id']) is not int or origin['head_repository_id'] != pr['head']['repo']['id']
                or origin['head_sha'] != pr['head']['sha']):
            raise ValueError
        return artifact['id'], pr['head']['sha'], pr['base']['sha'], run_id, attempt
    except (KeyError, TypeError, ValueError):
        raise InvalidPreviewArtifact('Trusted preview artifact metadata is invalid or stale') from None
