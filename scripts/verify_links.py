# -*- coding: utf-8 -*-
"""全库双链校验：扫描所有 .md，检查 [[...]] 链接目标是否存在。

用法（**仓库根目录**）：python scripts/verify_links.py
退出码：0 = 数据区死链 0；1 = 数据区（五语目录）存在死链。

口径（D-072 与 `docs/仓库结构.md` §四）：
  * **数据区** = `zh_cn/` `en_us/` `zh_tw/` `ja_jp/` `ko_kr/` 五个语言目录。
    这些是站点正文的来源，**死链必须为 0**，因此只有它们影响退出码。
  * **文档区** = `docs/`、`update.md`、`格式规范与要求.md` 等声明与流程文档。
    其中大量 `[[xxx]]` / `[[页面|示例]]` 是**语法示例**，按既有口径不计入判据，
    但其数量仍照常打印，避免「静默放过」。

本模块可被 `scripts/gen_metrics.py` 以 `import verify_links; verify_links.scan(ROOT)` 复用
（`main()` 之外不做任何 I/O）。
"""
import os
import re
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

skip_dirs = {'.obsidian', '.git', 'StarRailRes_repo', '.tmp_build', 'node_modules', 'StarRailRes_data', 'temp', 'StarRailRes-master'}

# 数据区语言目录（死链即判失败）
DATA_DIRS = ('zh_cn/', 'en_us/', 'zh_tw/', 'ja_jp/', 'ko_kr/', 'zh_cn\\', 'en_us\\', 'zh_tw\\', 'ja_jp\\', 'ko_kr\\')


def is_data_area(path):
    """path 是否落在五语数据目录内（兼容 / 与 \\ 两种分隔符）。"""
    p = path.replace('\\', '/')
    return any(p.startswith(d.strip('/') + '/') for d in DATA_DIRS)


def iter_wikilinks(text):
    """Yield the same non-overlapping targets as the old regex, in linear time.

    A long run of unmatched ``[[`` previously made repeated regex retries scan
    the remaining file quadratically. PR data is untrusted and can contain it.
    """
    pos = 0
    while True:
        start = text.find('[[', pos)
        if start < 0:
            return
        end = text.find(']', start + 2)
        if end < 0:
            return
        if end + 1 < len(text) and text[end + 1] == ']' and end > start + 2:
            yield text[start + 2:end]
            pos = end + 2
        else:
            # No opener before this closing bracket can form a valid match.
            pos = end + 1


def scan(root='.'):
    """扫描 root 下全部 .md 的 [[...]] 双链。

    返回 dict：files / total / dead / dead_data / dead_docs / by_src（Counter）/ details（[(file, raw)]）
    """
    files = []
    for dirpath, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in fs:
            if f.endswith('.md'):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, root).replace(os.sep, '/')
                files.append(rel)
    existing = set(files)

    dead = []
    total_links = 0
    for f in files:
        with open(os.path.join(root, f), encoding='utf-8') as source:
            txt = source.read()
        for raw in iter_wikilinks(txt):
            total_links += 1
            # 表格内转义管道符 \| 即显示名分隔符：先还原为 | 再取路径段
            link = raw.replace('\\|', '|').split('|')[0].strip()
            if link.startswith('!'):
                link = link[1:]
            if not link:
                continue
            # 文件名可能本身含 #（Obsidian 锚点语法歧义）：同时尝试含 # 原样与去 # 两种
            candidates = [link, link + '.md']
            if '#' in link:
                base = link.split('#')[0]
                candidates += [base, base + '.md']
            if not any(c in existing for c in candidates):
                dead.append((f, raw))

    dead_data = [d for d in dead if is_data_area(d[0])]
    return {
        'files': len(files),
        'total': total_links,
        'dead': len(dead),
        'dead_data': len(dead_data),
        'dead_docs': len(dead) - len(dead_data),
        'by_src': Counter(f for f, _ in dead),
        'details': dead,
        'dead_data_details': dead_data,
    }


def main():
    res = scan('.')
    print('扫描文件数:', res['files'])
    print('链接总数:', res['total'])
    print('死链数:', res['dead'])
    print('  ├ 数据区（五语目录，判据 = 0）:', res['dead_data'])
    print('  └ 文档区（含语法示例，不计入判据）:', res['dead_docs'])
    print('--- 按源文件聚拢 (top 25) ---')
    for f, c in res['by_src'].most_common(25):
        print('  [%d] %s' % (c, f))
    print('--- 死链明细 (前 40) ---')
    for f, raw in res['details'][:40]:
        print('  %s -> [[%s]]' % (f, raw))
    if res['dead_data']:
        print()
        print('RESULT: FAIL 数据区死链 %d 条（要求 0）：' % res['dead_data'])
        for f, raw in res['dead_data_details'][:40]:
            print('  %s -> [[%s]]' % (f, raw))
        return 1
    print()
    print('RESULT: PASS 数据区死链 0（文档区 %d 条语法示例不计）' % res['dead_docs'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
