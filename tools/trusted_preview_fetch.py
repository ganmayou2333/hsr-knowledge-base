"""Download a receipt-bound trusted preview for local inspection only.

The caller must independently review and pin *all* producer workflow, actions,
builder and dependencies at reviewed_base. A matching SHA or receipt cannot do
that review. This function does not authorize publication; it never extracts the
archive and callers must revalidate at staging and immediately before release.
"""
import os
from pathlib import Path
import tempfile

from tools.preview_artifact import InvalidPreviewArtifact
from tools.preview_review import REPO_PATTERN, current_base_matches, gh_api, snapshot
from tools.reconcile_previews import pages_items
from tools.stage_preview import SHA, download_artifact
from tools.trusted_preview_artifact import select_trusted_preview


def download_trusted_preview(repo, number, run_id, reviewed_base, destination):
    """Fetch by artifact ID, fail closed on stale metadata; never publish."""
    if (not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo)
            or type(number) is not int or number < 1 or type(run_id) is not int or run_id < 1
            or not isinstance(reviewed_base, str) or not SHA.fullmatch(reviewed_base)):
        raise InvalidPreviewArtifact('Invalid trusted preview arguments')
    destination = Path(destination)
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
        raise InvalidPreviewArtifact('Invalid preview destination')
    prefix = f'repos/{repo}'
    def metadata(receipt_zip=None):
        pr = gh_api(f'{prefix}/pulls/{number}')
        if not current_base_matches(repo, pr, gh_api) or pr['base']['sha'] != reviewed_base:
            raise InvalidPreviewArtifact('PR base is not independently reviewed current main')
        workflow = gh_api(f'{prefix}/actions/workflows/wiki-trusted-data.yml')
        run = gh_api(f'{prefix}/actions/runs/{run_id}')
        artifacts = pages_items(gh_api(f'{prefix}/actions/runs/{run_id}/artifacts?per_page=100', paginate=True), 'artifacts')
        runs = pages_items(gh_api(f"{prefix}/actions/workflows/wiki-trusted-data.yml/runs?event=pull_request_target&head_sha={pr['head']['sha']}&per_page=100", paginate=True), 'workflow_runs')
        if pr['head']['repo']['id'] != pr['base']['repo']['id']:
            review = snapshot(repo, number)
            if review.get('head') != pr['head']['sha'] or review.get('approved') is not True:
                raise InvalidPreviewArtifact('External PR approval missing or stale')
        if type(run.get('run_attempt')) is not int or run['run_attempt'] < 1:
            raise InvalidPreviewArtifact('Invalid trusted run attempt')
        receipt_name = f"trusted-check-receipt-{number}-{run_id}-{run['run_attempt']}"
        receipts = [item for item in artifacts if item.get('name') == receipt_name]
        if len(receipts) != 1 or type(receipts[0].get('id')) is not int or receipts[0]['id'] < 1:
            raise InvalidPreviewArtifact('Trusted receipt missing or ambiguous')
        if receipt_zip is None:
            return receipts[0]['id']
        selected = select_trusted_preview(number, pr, workflow, run, receipts[0], receipt_zip, artifacts, runs)
        return receipts[0]['id'], selected

    with tempfile.TemporaryDirectory(prefix='.trusted-download-', dir=destination.parent) as temp:
        temp = Path(temp)
        receipt_id = metadata()
        download_artifact(repo, receipt_id, temp / 'receipt.zip')
        observed_receipt, selected = metadata(temp / 'receipt.zip')
        if observed_receipt != receipt_id:
            raise InvalidPreviewArtifact('Trusted receipt changed during download')
        download_artifact(repo, selected[0], temp / 'preview.zip')
        if metadata(temp / 'receipt.zip') != (receipt_id, selected):
            raise InvalidPreviewArtifact('Trusted preview changed during download')
        if destination.exists() or destination.is_symlink():
            raise InvalidPreviewArtifact('Preview destination changed')
        # A prior exists() check cannot prevent a concurrent writer from
        # creating the destination.  rename() can replace it on POSIX.  A
        # hard link in the same directory publishes the completed file only
        # if the destination is still absent, on both Windows and POSIX.
        try:
            os.link(temp / 'preview.zip', destination)
        except FileExistsError:
            raise InvalidPreviewArtifact('Preview destination changed') from None
        return selected
