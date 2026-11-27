"""Stage a PR artifact as inert data; never execute or publish PR content.

Run only from an independently trusted checkout. GitHub's successful PR workflow
is not proof that a PR-modified workflow or tests are trustworthy. This utility
also does not implement hosting, cleanup, or continuously current review status.
"""
import argparse
import os
import re
import stat
import subprocess
import tempfile
import threading
import zipfile
from pathlib import Path

from tools.preview_artifact import MAX_ARCHIVE_BYTES, InvalidPreviewArtifact, check_zip_directory, extract_preview_zip
from tools.preview_bundle import build_bundle
from tools.preview_review import REPO_PATTERN, gh_api, snapshot, current_base_matches

WORKFLOW = '.github/workflows/wiki-quality.yml'
TRUSTED_WORKFLOW = '.github/workflows/wiki-trusted-data.yml'
SHA = re.compile(r'^[0-9a-f]{40}$')


def select_artifact(repo, number, run_id, pr, run, pages, external_approved=False):
    """Validate GitHub API metadata and return the one matching artifact ID."""
    try:
        if (not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo)
                or type(number) is not int or number < 1 or type(run_id) is not int or run_id < 1):
            raise ValueError
        head, base = pr['head']['sha'], pr['base']['sha']
        base_repo, head_repo = pr['base']['repo'], pr['head']['repo']
        repo_id = base_repo['id']
        if (pr['number'] != number or pr['state'] != 'open'
                or base_repo['full_name'].casefold() != repo.casefold()
                or type(repo_id) is not int or repo_id < 1
                or not SHA.fullmatch(head) or not SHA.fullmatch(base)
                or run['id'] != run_id or run['repository']['id'] != repo_id
                or run['event'] != 'pull_request' or run['status'] != 'completed'
                or run['conclusion'] != 'success' or run['path'] != WORKFLOW
                or run['head_sha'] != head or type(run['run_attempt']) is not int or run['run_attempt'] < 1):
            raise ValueError
        if not isinstance(head_repo, dict) or type(head_repo.get('id')) is not int:
            raise ValueError
        if head_repo['id'] != repo_id and external_approved is not True:
            raise ValueError
        matches = [item for item in run['pull_requests'] if item['number'] == number
                   and item['head']['sha'] == head and item['base']['sha'] == base
                   and item['base']['repo']['id'] == repo_id
                   and item['head']['repo']['id'] == head_repo['id']]
        if len(matches) != 1:
            raise ValueError
        expected = f"wiki-preview-{number}-{head}-{run['run_attempt']}"
        if not isinstance(pages, list) or not pages:
            raise ValueError
        inventory = []
        for page in pages:
            if not isinstance(page, dict) or not isinstance(page.get('artifacts'), list):
                raise ValueError
            inventory.extend(page['artifacts'])
            # A capped listing cannot prove there isn't a duplicate name later.
            if len(inventory) >= 1000:
                raise ValueError
        ids = [item['id'] for item in inventory]
        if any(type(identifier) is not int or identifier < 1 for identifier in ids) or len(set(ids)) != len(ids):
            raise ValueError
        artifacts = [item for item in inventory if item['name'] == expected]
        if len(artifacts) != 1:
            raise ValueError
        artifact = artifacts[0]
        origin = artifact['workflow_run']
        if (artifact['expired'] is not False or type(artifact['id']) is not int or artifact['id'] < 1
                or type(artifact['size_in_bytes']) is not int or not 0 < artifact['size_in_bytes'] <= MAX_ARCHIVE_BYTES
                or origin['id'] != run_id or origin['repository_id'] != repo_id
                or origin['head_repository_id'] != head_repo['id'] or origin['head_sha'] != head):
            raise ValueError
        return artifact['id'], head, base
    except (KeyError, TypeError, AttributeError, ValueError):
        raise InvalidPreviewArtifact('PR, run, or artifact metadata is invalid, stale, or unauthorized') from None


def download_artifact(repo, artifact_id, destination):
    """Stream bounded binary output from gh, without extracting its ZIP wrapper."""
    process = subprocess.Popen(['gh', 'api', f'repos/{repo}/actions/artifacts/{artifact_id}/zip'],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    def stop_download():
        try:
            process.kill()
        except OSError:
            pass  # The process may have just exited.
    timeout = threading.Timer(180, stop_download)
    timeout.daemon = True
    timeout.start()
    try:
        total = 0
        with Path(destination).open('xb') as output:
            while chunk := process.stdout.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    raise InvalidPreviewArtifact('Downloaded artifact exceeds size limit')
                output.write(chunk)
        if process.wait() != 0:
            raise InvalidPreviewArtifact('Artifact download failed')
    finally:
        timeout.cancel()
        process.stdout.close()
        if process.poll() is None:
            process.kill()
            process.wait()


def unwrap_artifact(wrapper, destination):
    """Extract exactly one regular, bounded ZIP member from GitHub's wrapper."""
    with Path(wrapper).open('rb') as handle:
        size = os.fstat(handle.fileno()).st_size
        if size > MAX_ARCHIVE_BYTES:
            raise InvalidPreviewArtifact('Artifact wrapper exceeds size limit')
        check_zip_directory(handle, size)
        with zipfile.ZipFile(handle) as archive:
            entries = archive.infolist()
            if len(entries) != 1:
                raise InvalidPreviewArtifact('Artifact must contain exactly one file')
            info = entries[0]
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (info.orig_filename != 'wiki-preview.zip' or info.filename != 'wiki-preview.zip'
                    or info.is_dir() or file_type not in (0, stat.S_IFREG)
                    or info.flag_bits & 1 or info.file_size > MAX_ARCHIVE_BYTES
                    or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                raise InvalidPreviewArtifact('Invalid artifact wrapper member')
            with archive.open(info) as source, Path(destination).open('xb') as output:
                total = 0
                while chunk := source.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_ARCHIVE_BYTES:
                        raise InvalidPreviewArtifact('Preview ZIP exceeds size limit')
                    output.write(chunk)
                if total != info.file_size:
                    raise InvalidPreviewArtifact('Preview ZIP size mismatch')


def trusted_check(number, pr, workflow, run, run_id):
    """Bind the base-branch data gate to the exact open PR revision."""
    try:
        base_id, head_id = pr['base']['repo']['id'], pr['head']['repo']['id']
        if (type(base_id) is not int or type(head_id) is not int or base_id < 1 or head_id < 1
                or pr['number'] != number or pr['state'] != 'open'
                or workflow['state'] != 'active' or workflow['path'] != TRUSTED_WORKFLOW
                or type(workflow['id']) is not int or workflow['id'] < 1
                or run['id'] != run_id or run['workflow_id'] != workflow['id']
                or run['repository']['id'] != base_id or run['event'] != 'pull_request_target'
                or run['status'] != 'completed' or run['conclusion'] != 'success'
                or run['path'] != TRUSTED_WORKFLOW or run['head_sha'] != pr['head']['sha']
                or type(run['run_attempt']) is not int or run['run_attempt'] < 1):
            raise ValueError
        matches = [item for item in run['pull_requests'] if item['number'] == number
                   and item['head']['sha'] == pr['head']['sha'] and item['base']['sha'] == pr['base']['sha']
                   and item['head']['repo']['id'] == head_id and item['base']['repo']['id'] == base_id]
        if len(matches) != 1:
            raise ValueError
        return (run_id, run['run_attempt'])
    except (KeyError, TypeError, ValueError):
        raise InvalidPreviewArtifact('Trusted data check is missing, stale, or unsuccessful') from None


def stage(repo, number, run_id, destination, *, trusted_run_id):
    if (not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo) or type(number) is not int or number < 1
            or type(run_id) is not int or run_id < 1 or type(trusted_run_id) is not int or trusted_run_id < 1):
        raise InvalidPreviewArtifact('Invalid staging arguments')
    prefix = f'repos/{repo}'
    pr_path, run_path = f'{prefix}/pulls/{number}', f'{prefix}/actions/runs/{run_id}'

    def metadata():
        # Import here: the reconciler itself imports stage().  Discovery alone
        # is insufficient because a newer run can appear during conversion.
        from tools.reconcile_previews import latest_run, pages_items
        pr = gh_api(pr_path)
        if not current_base_matches(repo, pr, gh_api):
            raise InvalidPreviewArtifact('PR base is not the current main branch')
        run = gh_api(run_path)
        pages = gh_api(run_path + '/artifacts?per_page=100', paginate=True)
        workflow = gh_api(f'{prefix}/actions/workflows/wiki-trusted-data.yml')
        trusted_run = gh_api(f'{prefix}/actions/runs/{trusted_run_id}')
        external = (pr.get('head', {}).get('repo') or {}).get('id') != (pr.get('base', {}).get('repo') or {}).get('id')
        review = snapshot(repo, number) if external else None
        approved = bool(review and review.get('head') == pr.get('head', {}).get('sha') and review.get('approved') is True)
        artifact = select_artifact(repo, number, run_id, pr, run, pages, approved)
        checked = trusted_check(number, pr, workflow, trusted_run, trusted_run_id)
        for name, event, expected_id, expected_attempt in (
            ('wiki-quality.yml', 'pull_request', run_id, run['run_attempt']),
            ('wiki-trusted-data.yml', 'pull_request_target', trusted_run_id, checked[1]),
        ):
            runs = pages_items(gh_api(f"{prefix}/actions/workflows/{name}/runs?event={event}&head_sha={artifact[1]}&per_page=100", paginate=True), 'workflow_runs')
            latest = latest_run(runs, number, pr, event, f'.github/workflows/{name}')
            if (not latest or latest.get('id') != expected_id or latest.get('run_attempt') != expected_attempt
                    or latest.get('status') != 'completed' or latest.get('conclusion') != 'success'):
                raise InvalidPreviewArtifact('A newer or unsuccessful check exists during staging')
        return (*artifact, *checked, run['run_attempt'])

    selected = metadata()
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise InvalidPreviewArtifact('Destination already exists')
    with tempfile.TemporaryDirectory(prefix='preview-input-', dir=destination.parent) as temporary:
        root = Path(temporary)
        download_artifact(repo, selected[0], root / 'artifact.zip')
        unwrap_artifact(root / 'artifact.zip', root / 'wiki-preview.zip')
        extract_preview_zip(root / 'wiki-preview.zip', root / 'site')
        if metadata() != selected:
            raise InvalidPreviewArtifact('PR or artifact changed during staging')
        build_bundle(root / 'site', root / 'bundle', repo=repo, pr=number, head=selected[1], base=selected[2],
                     run=run_id, run_attempt=selected[5], trusted_run=selected[3], trusted_attempt=selected[4])
        # Check again after the expensive conversion; never publish this output blindly.
        if metadata() != selected:
            raise InvalidPreviewArtifact('PR or artifact changed during conversion')
        if destination.exists() or destination.is_symlink():
            raise InvalidPreviewArtifact('Destination already exists')
        os.rename(root / 'bundle', destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo')
    parser.add_argument('pr', type=int)
    parser.add_argument('run', type=int)
    parser.add_argument('destination')
    parser.add_argument('--trusted-run', type=int, required=True, help='successful trusted data-check run ID')
    args = parser.parse_args()
    try:
        stage(args.repo, args.pr, args.run, args.destination, trusted_run_id=args.trusted_run)
    except (InvalidPreviewArtifact, subprocess.SubprocessError, OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Cannot stage preview: {error}\n')


if __name__ == '__main__':
    main()
