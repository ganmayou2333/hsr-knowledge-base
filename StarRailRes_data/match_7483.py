# -*- coding: utf-8 -*-
"""匹配 wiki7483 祝福到 SRR，输出星级回填数据"""
import json, re

wiki = json.load(open('G:/HSR/StarRailRes_data/wiki7483_blessings.json', encoding='utf-8'))
# 去掉表头行
wiki = [d for d in wiki if d['name'] != '祝福']
srr = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_blessings.json', encoding='utf-8'))

def norm(s):
    s = s.replace('·', '•').replace('·', '•')
    s = s.replace(':', '：').replace(':', '：')
    return re.sub(r'[\s\u3000]', '', s)

srr_idx = {}
for i, v in srr.items():
    srr_idx.setdefault(norm(v.get('name', '')), []).append(i)

matched = 0
unmatched = []
star_map = {}
path_map = {}
for w in wiki:
    n = norm(w['name'])
    if n in srr_idx:
        matched += 1
        for sid in srr_idx[n]:
            star_map[sid] = w['star']
            path_map[sid] = w['path']
    else:
        unmatched.append(w['name'])

print('匹配: %d/%d' % (matched, len(wiki)))
print('未匹配 %d:' % len(unmatched))
for u in unmatched:
    print('  ', u)

# 覆盖 SRR 实体ID 及命途
from collections import Counter
print('\n覆盖 SRR 实体ID: %d' % len(star_map))
seg = Counter(sid[:4] for sid in star_map)
print('按 ID 段:', dict(seg))
print('7483 命途分布:', dict(Counter(path_map.values())))

# 保存星级+命途回填
json.dump(star_map, open('G:/HSR/StarRailRes_data/star_7483.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(path_map, open('G:/HSR/StarRailRes_data/path_7483.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已保存 star_7483.json + path_7483.json')
