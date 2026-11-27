"""Correlate a trusted-build artifact with a verified same-run check receipt.

This is a provenance building block, NOT publication authorization. The caller
must verify that the run actually used the reviewed producer workflow at the
expected base, select the latest applicable run (including failures/reruns),
validate all checks and approval, and refresh state around every staging step.
Fetch metadata and each ZIP by its unique artifact ID directly from GitHub.
"""
from tools.preview_artifact import MAX_ARCHIVE_BYTES, InvalidPreviewArtifact
from tools.trusted_receipt import validate_receipt


def select_trusted_preview(number, pr, workflow, run, receipt_artifact, receipt_zip, artifacts):
    """Return preview ID, head and base after local receipt and metadata checks.

    `artifacts` must be a complete, freshly fetched list from this run, not a
    caller-selected subset. This function never opens or trusts the preview ZIP.
    """
    run_id, attempt = validate_receipt(number, pr, workflow, run, receipt_artifact, receipt_zip)
    try:
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
        if matching_receipts != [receipt_artifact]:
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
