"""Build an unpublished preview with trusted code and untrusted Markdown data.

Prototype only: this does NOT establish PR/run/artifact identity or authorize
publication. The PR checkout must be immutable for the whole call. Never run
this with publishing credentials or alongside a process that can modify input.
The generated site remains untrusted and requires preview-shell isolation.
"""
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

if __package__ in (None, ""):
    # Isolated mode omits the script directory; add only this trusted checkout.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.package_preview import package_site
from tools.preview_artifact import InvalidPreviewArtifact
from tools.trusted_quality import MAX_FILES, MAX_MARKDOWN_FILE, MAX_MARKDOWN_TOTAL, inspect_tree


def build(source, trusted, destination, timeout=180):
    source = Path(source)
    trusted = Path(trusted)
    destination = Path(destination)
    if source.is_symlink() or trusted.is_symlink():
        raise InvalidPreviewArtifact('Linked checkout root')
    source = source.resolve(strict=True)
    trusted = trusted.resolve(strict=True)
    if (source == trusted or source in trusted.parents or trusted in source.parents
            or destination.exists() or destination.is_symlink()
            or not destination.parent.is_dir()):
        raise InvalidPreviewArtifact('Invalid input or destination')
    output_parent = destination.parent.resolve(strict=True)
    if output_parent == source or source in output_parent.parents or output_parent == trusted or trusted in output_parent.parents:
        raise InvalidPreviewArtifact('Destination must be outside both checkouts')
    inspect_tree(source)
    if not (trusted / 'wiki' / 'build_wiki.py').is_file():
        raise InvalidPreviewArtifact('Trusted builder is missing')
    with tempfile.TemporaryDirectory(prefix='trusted-preview-') as tmp:
        workspace = Path(tmp)
        # Generated outputs and downloaded icons are not trusted source files.
        def ignore(directory, names):
            folder = Path(directory)
            if folder == trusted / 'wiki':
                return {'pages', 'data', '__pycache__'} & set(names)
            if folder == trusted / 'wiki' / 'assets':
                return {'icons'} & set(names)
            return {'__pycache__'} & set(names)
        shutil.copytree(trusted / 'wiki', workspace / 'wiki', ignore=ignore)
        root = source / 'zh_cn'
        count = total = 0
        def onerror(error):
            raise error
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
            for name in dirs:
                entry = Path(directory) / name
                if entry.is_symlink() or not stat.S_ISDIR(entry.lstat().st_mode):
                    raise InvalidPreviewArtifact('Unexpected data directory')
            for name in files:
                if not name.endswith('.md'):
                    continue
                path = Path(directory) / name
                info = path.lstat()
                if not stat.S_ISREG(info.st_mode):
                    raise InvalidPreviewArtifact('Unexpected data file')
                count += 1
                total += info.st_size
                if count > MAX_FILES or info.st_size > MAX_MARKDOWN_FILE or total > MAX_MARKDOWN_TOTAL:
                    raise InvalidPreviewArtifact('Data exceeds resource limits')
                target = workspace / 'zh_cn' / path.relative_to(root)
                target.parent.mkdir(parents=True, exist_ok=True)
                flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
                with os.fdopen(os.open(path, flags), 'rb') as original:
                    opened = os.fstat(original.fileno())
                    if (opened.st_dev, opened.st_ino, opened.st_size) != (info.st_dev, info.st_ino, info.st_size):
                        raise InvalidPreviewArtifact('Input changed during copy')
                    with target.open('xb') as output:
                        shutil.copyfileobj(original, output, length=65536)
        # No GitHub token, PR environment, imports from the checkout or user site.
        env = {key: os.environ[key] for key in ('PATH', 'SystemRoot', 'TEMP', 'TMP') if key in os.environ}
        subprocess.run([sys.executable, '-I', '-X', 'utf8', str(workspace / 'wiki' / 'build_wiki.py')],
                       cwd=workspace, env=env, check=True, timeout=timeout)
        package_site(workspace / 'wiki', destination)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='immutable PR checkout, treated only as data')
    parser.add_argument('destination', help='new ZIP path outside both checkouts')
    args = parser.parse_args()
    build(args.source, Path(__file__).resolve().parent.parent, args.destination)
