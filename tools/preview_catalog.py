"""Assemble a fresh multi-PR preview site from previously staged inert bundles.

Use only from a trusted, credential-free publisher checkout. This command does
not deploy, establish trusted CI provenance, or provide live review status. All
GitHub reads are through gh; a failed read aborts without creating an output.
"""
import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from tools.preview_artifact import MAX_FILE_BYTES, MAX_FILES, MAX_TOTAL_BYTES, InvalidPreviewArtifact, archive_path
from tools.preview_bundle import safe_json
from tools.preview_review import REPO_PATTERN, gh_api, snapshot, current_base_matches
from tools.stage_preview import trusted_check

SHA = re.compile(r'^[0-9a-f]{40}$')
DIGEST = re.compile(r'^[0-9a-f]{64}$')
PR_NUMBER = re.compile(r'^[1-9][0-9]{0,7}$')
TRUSTED_SHELL = ('index.html', 'shell.css', 'shell.js', 'frame.js')


def metadata(repo, number, manifest):
    """A closed or stale PR is omitted; API errors abort the entire rebuild."""
    pr = gh_api(f'repos/{repo}/pulls/{number}')
    if pr['number'] != number or pr['state'] not in ('open', 'closed'):
        raise InvalidPreviewArtifact('Invalid GitHub PR response')
    if pr['state'] == 'closed':
        return False
    if not current_base_matches(repo, pr, gh_api):
        return False
    if pr['head']['sha'] != manifest['head'] or pr['base']['sha'] != manifest['base']:
        return False
    run = gh_api(f"repos/{repo}/actions/runs/{manifest['run']}")
    matches = [item for item in run['pull_requests'] if item['number'] == number
               and item['head']['sha'] == manifest['head'] and item['base']['sha'] == manifest['base']]
    valid_build = (run['id'] == manifest['run'] and run['run_attempt'] == manifest['run_attempt'] and run['event'] == 'pull_request'
            and run['status'] == 'completed' and run['conclusion'] == 'success'
            and run['path'] == '.github/workflows/wiki-quality.yml'
            and run['head_sha'] == manifest['head'] and len(matches) == 1)
    if not valid_build:
        return False
    workflow = gh_api(f'repos/{repo}/actions/workflows/wiki-trusted-data.yml')
    trusted_run = gh_api(f"repos/{repo}/actions/runs/{manifest['trusted_run']}")
    try:
        return trusted_check(number, pr, workflow, trusted_run, manifest['trusted_run']) == (
            manifest['trusted_run'], manifest['trusted_attempt'])
    except InvalidPreviewArtifact:
        return False


def regular(path):
    return path.is_file() and not path.is_symlink()


def read_json(path, maximum):
    if not regular(path) or path.stat().st_size > maximum:
        raise InvalidPreviewArtifact('Invalid or oversized JSON file')
    return json.loads(path.read_text(encoding='ascii'))


def validated_manifest(bundle, repo, number):
    manifest = read_json(bundle / 'manifest.json', 16 * 1024 * 1024)
    try:
        files = manifest['files']
        if (type(manifest['version']) is not int or manifest['version'] != 1 or manifest['repo'] != repo
                or type(manifest['pr']) is not int or manifest['pr'] != number
                or not SHA.fullmatch(manifest['head']) or not SHA.fullmatch(manifest['base'])
                or type(manifest['run']) is not int or manifest['run'] < 1
                or type(manifest['run_attempt']) is not int or manifest['run_attempt'] < 1
                or type(manifest['trusted_run']) is not int or manifest['trusted_run'] < 1
                or type(manifest['trusted_attempt']) is not int or manifest['trusted_attempt'] < 1
                or not isinstance(files, dict) or not 0 < len(files) <= MAX_FILES or 'index.html' not in files):
            raise ValueError
        for path, digest in files.items():
            archive_path(path)
            if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
                raise ValueError
        return manifest
    except (KeyError, TypeError, ValueError):
        raise InvalidPreviewArtifact('Invalid preview manifest') from None


def copy_bundle(source, target, manifest):
    """Copy only normalized, verified JSON, never source-provided HTML or paths."""
    objects = source / 'objects'
    if objects.is_symlink() or not objects.is_dir():
        raise InvalidPreviewArtifact('Invalid object directory')
    target.mkdir(parents=True)
    target_objects = target / 'objects'
    target_objects.mkdir()
    total = 0
    for digest in sorted(set(manifest['files'].values())):
        obj = read_json(objects / (digest + '.json'), (MAX_FILE_BYTES * 4 // 3) + 1024)
        try:
            if not isinstance(obj, dict) or set(obj) != {'data'} or not isinstance(obj['data'], str):
                raise ValueError
            content = base64.b64decode(obj['data'], validate=True)
            if len(content) > MAX_FILE_BYTES or hashlib.sha256(content).hexdigest() != digest:
                raise ValueError
            total += len(content)
            if total > MAX_TOTAL_BYTES:
                raise ValueError
        except (ValueError, binascii.Error):
            raise InvalidPreviewArtifact('Invalid preview object') from None
        (target_objects / (digest + '.json')).write_text(safe_json(obj), encoding='ascii')
    (target / 'manifest.json').write_text(safe_json(manifest), encoding='ascii')


def assemble(repo, bundles, shell, destination):
    if not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo):
        raise InvalidPreviewArtifact('Invalid repository')
    bundles, shell, destination = Path(bundles), Path(shell), Path(destination)
    if (bundles.is_symlink() or not bundles.is_dir() or shell.is_symlink() or not shell.is_dir()
            or destination.exists() or destination.is_symlink() or not destination.parent.is_dir()):
        raise InvalidPreviewArtifact('Invalid input or destination')
    candidates = sorted(bundles.iterdir(), key=lambda path: path.name)
    if len(candidates) > 1000:
        raise InvalidPreviewArtifact('Too many previews')
    with tempfile.TemporaryDirectory(prefix='.preview-site-', dir=destination.parent) as tmp:
        staged = Path(tmp) / 'site'
        staged.mkdir()
        for name in TRUSTED_SHELL:
            source = shell / name
            if not regular(source) or source.stat().st_size > 1024 * 1024:
                raise InvalidPreviewArtifact('Invalid trusted shell')
            shutil.copyfile(source, staged / name)
        (staged / 'previews').mkdir()
        included = []
        for bundle in candidates:
            if not PR_NUMBER.fullmatch(bundle.name) or bundle.is_symlink() or not bundle.is_dir():
                raise InvalidPreviewArtifact('Unexpected entry in preview input')
            number = int(bundle.name)
            manifest = validated_manifest(bundle, repo, number)
            if metadata(repo, number, manifest):
                copy_bundle(bundle, staged / 'previews' / bundle.name, manifest)
                included.append((number, manifest))
        # Refuse to publish if a PR or run changed during the potentially long copy.
        if not all(metadata(repo, number, manifest) for number, manifest in included):
            raise InvalidPreviewArtifact('A preview became stale during assembly')
        for number, manifest in included:
            try:
                review = snapshot(repo, number)
                if review['pr'] != number or review['head'] != manifest['head']:
                    raise ValueError('Review snapshot does not match preview')
                review['repo'] = repo
                (staged / 'previews' / str(number) / 'review.json').write_text(safe_json(review), encoding='ascii')
            except (subprocess.SubprocessError, OSError, ValueError, KeyError, TypeError):
                # Failure to verify approval must never become an approval.
                pass
        if destination.exists() or destination.is_symlink():
            raise InvalidPreviewArtifact('Destination already exists')
        os.rename(staged, destination)
        return [number for number, _ in included]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo')
    parser.add_argument('bundles')
    parser.add_argument('shell')
    parser.add_argument('destination')
    args = parser.parse_args()
    try:
        included = assemble(args.repo, args.bundles, args.shell, args.destination)
    except (InvalidPreviewArtifact, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Cannot assemble preview site: {error}\n')
    print('Included PRs:', ', '.join(map(str, included)) or '(none)')


if __name__ == '__main__':
    main()
