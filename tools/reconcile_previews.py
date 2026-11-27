"""Discover current PRs and assemble an inert, unpublished preview catalog.

Run from an independently trusted checkout with read-only gh credentials.
This does not switch a live site, host it, or execute PR-provided content.
An API, download, or validation failure leaves no destination directory.
"""
import argparse
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from tools.preview_artifact import InvalidPreviewArtifact
from tools.preview_catalog import assemble
from tools.preview_review import REPO_PATTERN, gh_api, snapshot
from tools.stage_preview import SHA, stage, trusted_check

MAX_PRS = 1000
MAX_RUNS = 1000


class MissingRunAssociation(InvalidPreviewArtifact):
    """GitHub did not supply evidence binding a run to a PR."""


def pages_items(pages, key=None):
    if not isinstance(pages, list):
        raise InvalidPreviewArtifact('Invalid paginated response')
    result = []
    for page in pages:
        items = page.get(key) if key and isinstance(page, dict) else page if key is None else None
        if not isinstance(items, list):
            raise InvalidPreviewArtifact('Invalid paginated response')
        result.extend(items)
        if len(result) > (MAX_RUNS if key else MAX_PRS):
            raise InvalidPreviewArtifact('Too many GitHub results')
    return result


def latest_run(runs, number, pr, event, path):
    """Find the newest run for this exact PR revision, including failed runs."""
    candidates = []
    seen = set()
    for run in runs:
        try:
            if run['event'] != event or run['path'] != path or run['head_sha'] != pr['head']['sha']:
                continue
            identifier = run['id']
            if type(identifier) is not int or identifier < 1 or identifier in seen:
                raise ValueError
            seen.add(identifier)
            associations = run['pull_requests']
            if not isinstance(associations, list):
                raise ValueError
            if not associations:
                raise MissingRunAssociation('Workflow run has no PR association')
            matches = [item for item in associations if item['number'] == number]
            if not matches:
                continue
            if len(matches) != 1:
                raise ValueError
            started = run['run_started_at']
            if not isinstance(started, str) or len(started) != 20 or not started.endswith('Z'):
                raise ValueError
            if datetime.strptime(started, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).isoformat()[:19] != started[:19]:
                raise ValueError
            candidates.append((started, run['id'], run))
        except MissingRunAssociation:
            raise
        except (KeyError, TypeError, ValueError):
            raise InvalidPreviewArtifact('Invalid workflow run metadata') from None
    return max(candidates, default=(None, None, None), key=lambda item: (item[0] or '', item[1] or 0))[2]


def reconcile(repo, shell, destination):
    if not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo):
        raise InvalidPreviewArtifact('Invalid repository')
    destination = Path(destination)
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
        raise InvalidPreviewArtifact('Invalid destination')
    prefix = f'repos/{repo}'
    prs = pages_items(gh_api(f'{prefix}/pulls?state=open&per_page=100', paginate=True))
    workflow = gh_api(f'{prefix}/actions/workflows/wiki-trusted-data.yml')
    seen = set()
    with tempfile.TemporaryDirectory(prefix='.preview-reconcile-', dir=destination.parent) as temp:
        bundles = Path(temp) / 'bundles'
        bundles.mkdir()
        for pr in prs:
            try:
                number, head = pr['number'], pr['head']['sha']
                if (type(number) is not int or not 0 < number < 100000000 or number in seen
                        or pr['state'] != 'open' or not SHA.fullmatch(head)
                        or not SHA.fullmatch(pr['base']['sha'])):
                    raise ValueError
                seen.add(number)
                base_id, head_id = pr['base']['repo']['id'], pr['head']['repo']['id']
                if type(base_id) is not int or type(head_id) is not int or min(base_id, head_id) < 1:
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                raise InvalidPreviewArtifact('Invalid PR metadata') from None
            build_path = '.github/workflows/wiki-quality.yml'
            trusted_path = '.github/workflows/wiki-trusted-data.yml'
            build_runs = pages_items(gh_api(f'{prefix}/actions/workflows/wiki-quality.yml/runs?event=pull_request&head_sha={head}&per_page=100', paginate=True), 'workflow_runs')
            trusted_runs = pages_items(gh_api(f'{prefix}/actions/workflows/wiki-trusted-data.yml/runs?event=pull_request_target&head_sha={head}&per_page=100', paginate=True), 'workflow_runs')
            try:
                build = latest_run(build_runs, number, pr, 'pull_request', build_path)
                trusted = latest_run(trusted_runs, number, pr, 'pull_request_target', trusted_path)
            except MissingRunAssociation:
                # Do not infer PR identity from a commit SHA; other PRs may proceed.
                continue
            if (not build or not trusted or build.get('status') != 'completed' or build.get('conclusion') != 'success'
                    or trusted.get('status') != 'completed' or trusted.get('conclusion') != 'success'):
                continue
            try:
                trusted_check(number, pr, workflow, trusted, trusted['id'])
            except InvalidPreviewArtifact:
                continue
            if head_id != base_id:
                review = snapshot(repo, number)
                if review.get('head') != head or review.get('approved') is not True:
                    continue
            stage(repo, number, build['id'], bundles / str(number), trusted_run_id=trusted['id'])
        return assemble(repo, bundles, shell, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo')
    parser.add_argument('shell')
    parser.add_argument('destination')
    args = parser.parse_args()
    try:
        included = reconcile(args.repo, args.shell, args.destination)
    except (InvalidPreviewArtifact, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Cannot reconcile previews: {error}\n')
    print('Included PRs:', ', '.join(map(str, included)) or '(none)')


if __name__ == '__main__':
    main()
