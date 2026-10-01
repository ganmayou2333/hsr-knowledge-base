# -*- coding: utf-8 -*-
"""全库双链校验：扫描所有 .md，检查 [[...]] 链接目标是否存在"""
import os, re
from collections import Counter

skip_dirs = {'.obsidian', '.git', 'StarRailRes_repo', '.tmp_build', 'node_modules', 'StarRailRes_data', 'temp', 'StarRailRes-master'}
files = []
for root, dirs, fs in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for f in fs:
        if f.endswith('.md'):
            files.append(os.path.join(root, f).replace(os.sep, '/')[2:])
existing = set(files)

dead = []
total_links = 0
for f in files:
    txt = open(f, encoding='utf-8').read()
    for m in re.finditer(r'\[\[([^\]]+)\]\]', txt):
        raw = m.group(1)
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

print('扫描文件数:', len(files))
print('链接总数:', total_links)
print('死链数:', len(dead))
src = Counter(f for f, _ in dead)
print('--- 按源文件聚拢 (top 25) ---')
for f, c in src.most_common(25):
    print('  [%d] %s' % (c, f))
print('--- 死链明细 (前 40) ---')
for f, raw in dead[:40]:
    print('  %s -> [[%s]]' % (f, raw))
