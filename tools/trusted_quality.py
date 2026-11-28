"""Run trusted data checks against an untrusted checkout without executing it.

Invoke this file with Python isolated mode from an independently trusted checkout:
    python -I /trusted/tools/trusted_quality.py /path/to/untrusted/checkout
This is a data gate, not a publisher or proof that PR-provided tests ran.
Run it with no publishing credentials and appropriate resource isolation.
"""
import argparse
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TRUSTED_ROOT = Path(__file__).resolve().parent.parent
MAX_FILES = 50000
MAX_MARKDOWN_FILE = 16 * 1024 * 1024
MAX_MARKDOWN_TOTAL = 512 * 1024 * 1024
SKIP = {'.git', '.obsidian', 'StarRailRes_repo', '.tmp_build', 'node_modules',
        'StarRailRes_data', 'temp', 'StarRailRes-master'}


def inspect_tree(root):
    """Reject links, special files and excessive input before trusted scanners read it.

    The checkout must remain immutable during inspection and scanning. Do not
    give untrusted processes write access to it while this check is running.
    """
    root = Path(root)
    if root.is_symlink() or not root.is_dir() or (root / 'data' / 'zh_cn').is_symlink() or not (root / 'data' / 'zh_cn').is_dir():
        raise ValueError('Source checkout or zh_cn directory is invalid')
    count = total = zh_markdown = 0
    def onerror(error):
        raise error
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        for name in dirs[:]:
            path = Path(directory) / name
            if path.is_symlink() or not stat.S_ISDIR(path.lstat().st_mode):
                raise ValueError('Checkout contains a linked or special directory')
            if name in SKIP:
                # The link/field scanners skip these names at any depth, but
                # the Wiki builder renders all Markdown below data/zh_cn. Reject
                # them there rather than publishing unchecked data.
                if path.relative_to(root).parts[:2] == ('data', 'zh_cn'):
                    raise ValueError('Data directory would be skipped by trusted scanners')
                dirs.remove(name)
        for name in files:
            path = Path(directory) / name
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise ValueError('Checkout contains a linked or special file')
            count += 1
            if count > MAX_FILES:
                raise ValueError('Checkout exceeds file count limit')
            if name.endswith('.md'):
                if path.relative_to(root).parts[:2] == ('data', 'zh_cn'):
                    zh_markdown += 1
                total += info.st_size
                if info.st_size > MAX_MARKDOWN_FILE or total > MAX_MARKDOWN_TOTAL:
                    raise ValueError('Checkout exceeds Markdown size limit')
    if not zh_markdown:
        raise ValueError('Checkout contains no Chinese Markdown data')
    return count, total


def check(root, trusted_root=TRUSTED_ROOT):
    root = Path(root)
    if root.is_symlink():
        raise ValueError('Source checkout is a symbolic link')
    root = root.resolve(strict=True)
    trusted_root = Path(trusted_root).resolve(strict=True)
    inspect_tree(root)
    spec = importlib.util.spec_from_file_location('trusted_verify_links', trusted_root / 'scripts' / 'verify_links.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    baseline = json.loads((trusted_root / 'tools' / 'quality_baseline.json').read_text(encoding='utf-8'))
    allowed = Counter(tuple(item) for item in baseline['dead_links'])
    actual = Counter(tuple(item) for item in module.scan(str(root))['dead_data_details'])
    new = actual - allowed
    print(f'数据区链接：现存 {sum(actual.values())}，新增 {sum(new.values())}')
    for (source, target), count in sorted(new.items()):
        print(f'  新增 {count} 处: {source} -> {target}')
    result = subprocess.run([sys.executable, '-I', '-X', 'utf8', str(trusted_root / 'scripts' / 'verify_fields.py'), '--quality-count'],
                            cwd=root / 'data' / 'zh_cn', capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=120, env={'PYTHONIOENCODING': 'utf-8'})
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    match = re.fullmatch(r'([0-9]+)\n', result.stdout)
    return not new and result.returncode == 0 and match is not None and int(match.group(1)) == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', help='read-only PR checkout to inspect')
    args = parser.parse_args()
    try:
        if not check(args.checkout):
            parser.exit(1, '可信数据检查失败\n')
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'无法完成可信数据检查: {error}\n')
    print('可信数据检查通过')


if __name__ == '__main__':
    main()
