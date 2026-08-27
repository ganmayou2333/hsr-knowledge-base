# -*- coding: utf-8 -*-
"""匹配米游社 WIKI 767 祝福与 SRR 祝福"""
import json, re

wiki = json.load(open('G:/HSR/StarRailRes_data/wiki767_blessings.json', encoding='utf-8'))
srr = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_blessings.json', encoding='utf-8'))

def norm(s):
    # 归一化名称：统一标点、去空格
    s = s.replace('·', '•').replace('·', '•').replace('•', '•')
    s = s.replace(':', '：').replace(':', '：')
    s = re.sub(r'[\s\u3000]', '', s)
    return s

# SRR 索引（按归一化名称 → 实体ID列表）
srr_idx = {}
for i, v in srr.items():
    n = norm(v.get('name', ''))
    srr_idx.setdefault(n, []).append(i)

matched = 0
unmatched = []
for w in wiki:
    n = norm(w['name'])
    if n in srr_idx:
        matched += 1
        w['srr_ids'] = srr_idx[n]
    else:
        unmatched.append(w['name'])

print('匹配: %d/%d' % (matched, len(wiki)))
print('未匹配 %d 条:' % len(unmatched))
for u in unmatched:
    print('  ', u)

# SRR 中被 wiki 覆盖的经典祝福数（6120-6128）
cover_ids = set()
for w in wiki:
    for i in w.get('srr_ids', []):
        cover_ids.add(i)
print('\n覆盖 SRR 实体ID: %d' % len(cover_ids))
# 未覆盖的 6120-6128 段祝福
import collections
seg_612 = {i for i in srr if i[:4] in ['612%d' % d for d in range(9)]}
print('SRR 612x 段祝福: %d, 被wiki覆盖: %d, 未覆盖: %d' % (len(seg_612), len(cover_ids & seg_612), len(seg_612 - cover_ids)))
for i in sorted(seg_612 - cover_ids)[:20]:
    print('   未覆盖:', i, srr[i].get('name'))
