"""Build and atomically activate a local preview release; never publish remotely.

Use a dedicated, trusted release root and only read-only GitHub credentials.
Run behind an HTTPS proxy with preview_review_server --site-root. The caller
must arrange scheduling, hosting, and protection of the release root.
"""
import argparse
import json
import os
import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from tools.preview_artifact import InvalidPreviewArtifact
from tools.preview_release_state import RELEASE, active_site
from tools.preview_review import REPO_PATTERN
from tools.reconcile_previews import reconcile
from tools.verify_preview_publication import verify

GRACE_SECONDS = 600


def prune(root, repo, keep):
    """Remove only older, tool-owned releases inside the dedicated sites directory."""
    sites = root / 'sites'
    for site in sites.iterdir():
        if site.name in keep or not RELEASE.fullmatch(site.name) or site.is_symlink() or not site.is_dir():
            continue
        marker = site / '.preview-release.json'
        try:
            if marker.is_symlink() or not marker.is_file() or marker.stat().st_size > 1024:
                continue
            value = json.loads(marker.read_text(encoding='ascii'))
            if (value != {'version': 1, 'repo': repo, 'name': site.name}
                    or time.time() - site.stat().st_mtime < GRACE_SECONDS):
                continue
            if site.resolve(strict=True).parent != sites.resolve(strict=True):
                continue
            shutil.rmtree(site)
        except (OSError, ValueError, TypeError):
            continue


def publish(repo, shell, root):
    if not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo):
        raise InvalidPreviewArtifact('Invalid repository')
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise InvalidPreviewArtifact('Invalid release root')
    root = root.resolve(strict=True)
    sites = root / 'sites'
    if sites.is_symlink():
        raise InvalidPreviewArtifact('Invalid release directory')
    sites.mkdir(exist_ok=True)
    if not sites.is_dir():
        raise InvalidPreviewArtifact('Invalid release directory')
    lock = root / '.publish-lock'
    try:
        lock.mkdir()
    except FileExistsError:
        raise InvalidPreviewArtifact('Another release is running or a stale lock needs attention') from None
    site = None
    built = False
    switched = False
    try:
        previous = active_site(root, optional=True)
        name = 'site-' + secrets.token_hex(16)
        site = sites / name
        included = reconcile(repo, shell, site)
        built = True
        actual = {entry.name for entry in (site / 'previews').iterdir()}
        if (not isinstance(included, list) or any(type(number) is not int or number < 1 for number in included)
                or len(set(included)) != len(included) or actual != {str(number) for number in included}
                or verify(repo, site) != len(included)):
            raise InvalidPreviewArtifact('Preview inventory or final verification changed before activation')
        marker = {'version': 1, 'repo': repo, 'name': name}
        (site / '.preview-release.json').write_text(json.dumps(marker), encoding='ascii')
        pointer = root / 'current'
        if pointer.is_symlink():
            raise InvalidPreviewArtifact('Invalid active release pointer')
        with tempfile.NamedTemporaryFile(mode='w', encoding='ascii', dir=root, prefix='.current-', delete=False) as file:
            temp_pointer = Path(file.name)
            try:
                file.write(name + '\n')
                file.flush()
                os.fsync(file.fileno())
            except BaseException:
                temp_pointer.unlink(missing_ok=True)
                raise
        try:
            os.replace(temp_pointer, pointer)
            switched = True
        finally:
            temp_pointer.unlink(missing_ok=True)
        prune(root, repo, {name, previous.name if previous else ''})
        return included
    finally:
        if not switched and built and site is not None and site.is_dir() and not site.is_symlink():
            shutil.rmtree(site)
        lock.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo')
    parser.add_argument('shell')
    parser.add_argument('root')
    args = parser.parse_args()
    try:
        included = publish(args.repo, args.shell, args.root)
    except (InvalidPreviewArtifact, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Cannot activate preview release: {error}\n')
    print('Activated PRs:', ', '.join(map(str, included)) or '(none)')


if __name__ == '__main__':
    main()
