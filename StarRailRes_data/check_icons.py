# -*- coding: utf-8 -*-
"""校验 index_new/cn 所有 icon 路径是否在本地图包存在"""
import os, json, glob
from collections import defaultdict

REPO = 'G:/HSR/StarRailRes_repo'
CN = os.path.join(REPO, 'index_new', 'cn')

def walk_icons(obj):
    """递归提取所有 icon 值"""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'icon' and isinstance(v, str) and v:
                found.append(v)
            else:
                found.extend(walk_icons(v))
    elif isinstance(obj, list):
        for it in obj:
            found.extend(walk_icons(it))
    return found

total = 0
missing = []          # (file, icon_path, ref_count)
missing_detail = defaultdict(int)
per_file = defaultdict(int)

for fp in sorted(glob.glob(os.path.join(CN, '*.json'))):
    fname = os.path.basename(fp)
    try:
        data = json.load(open(fp, encoding='utf-8'))
    except Exception as e:
        print(f'{fname}: 解析失败 {e}')
        continue
    icons = walk_icons(data)
    per_file[fname] = len(icons)
    total += len(icons)
    for ic in icons:
        # 去重统计每个 icon 引用次数
        local = os.path.join(REPO, ic.replace('/', os.sep))
        if not os.path.isfile(local):
            missing_detail[ic] += 1
            missing.append((fname, ic))

print('=== 引用统计 ===')
for f, n in per_file.items():
    print(f'  {f}: 引用 {n} 个 icon')
print(f'\n总 icon 引用: {total}')
print(f'本地缺失 icon 路径数(去重): {len(missing_detail)}')
if missing_detail:
    print('\n=== 缺失明细 ===')
    for ic, cnt in sorted(missing_detail.items()):
        print(f'  {ic}  (引用{cnt}次)')
