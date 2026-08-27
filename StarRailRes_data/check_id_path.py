# -*- coding: utf-8 -*-
"""分析祝福 ID 段与命途的对应规律"""
import json
from collections import defaultdict

b = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_blessings.json', encoding='utf-8'))

# 命途回响的 ID 段 → 命途（锚点）
anchors = {}
for i, v in b.items():
    n = v.get('name', '')
    if n.startswith('命途回响'):
        # 从名称提取命途
        import re
        m = re.search(r'「([^」]+)」', n)
        if m:
            anchors[i[:4]] = m.group(1)
print('命途锚点(ID前4位→命途):')
for k in sorted(anchors):
    print('  %s → %s' % (k, anchors[k]))

# 全部祝福按 ID 前4位分组
groups = defaultdict(list)
for i, v in b.items():
    groups[i[:4]].append((i, v.get('name', '')))

print('\n全部祝福 ID 段分布:')
for seg in sorted(groups):
    path = anchors.get(seg, '?')
    names = [n for _, n in groups[seg]]
    print('  %s (%s): %d 条 | 示例: %s' % (seg, path, len(groups[seg]), '、'.join(names[:3])))

# 统计可推命途的祝福数
covered = sum(len(v) for k, v in groups.items() if k in anchors)
print('\n可通过ID段推断命途: %d/%d' % (covered, len(b)))
