# -*- coding: utf-8 -*-
"""检查模拟宇宙各分类重名情况"""
import json, re
from collections import defaultdict

CN = 'G:/HSR/StarRailRes_repo/index_new/cn'

def clean(name):
    if not name:
        return '未命名'
    s = name.replace('<', '《').replace('>', '》')
    for ch in ':"/\\|?*':
        s = s.replace(ch, ' ')
    return re.sub(r'\s+', ' ', s).strip()

for fn in ['simulated_blessings.json', 'simulated_curios.json',
           'simulated_events.json', 'simulated_blocks.json']:
    d = json.load(open(CN + '/' + fn, encoding='utf-8'))
    groups = defaultdict(list)
    for i, v in d.items():
        groups[clean(v.get('name', ''))].append((i, v.get('name', '')))
    dups = {k: v for k, v in groups.items() if len(v) > 1}
    print('=== %s ===' % fn)
    print('总数: %d, 清洗后唯一名: %d, 重名组: %d, 重名条数: %d' % (
        len(d), len(groups), len(dups), sum(len(v) for v in dups.values())))
    for k, v in sorted(dups.items(), key=lambda x: -len(x[1]))[:10]:
        print('  重名: "%s" -> %s' % (k, v))
    print()
