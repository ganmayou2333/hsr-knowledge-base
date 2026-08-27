# -*- coding: utf-8 -*-
"""匹配 wiki7483 事件到 SRR 事件，输出事件文本回填数据"""
import json, re

wiki = json.load(open('G:/HSR/StarRailRes_data/wiki7483_events.json', encoding='utf-8'))
srr = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_events.json', encoding='utf-8'))

def norm(s):
    s = s.replace('·', '•').replace('·', '•')
    s = s.replace(':', '：').replace(':', '：')
    s = re.sub(r'[\s\u3000]', '', s)
    # 去掉括号后缀（其一/其二/（灯鱼篇）等）
    s = re.sub(r'[（(].{1,12}[）)]$', '', s)
    s = re.sub(r'其[一二三四五六七八九]$', '', s)
    return s

srr_idx = {}
for i, v in srr.items():
    srr_idx.setdefault(norm(v.get('name', '')), []).append(i)

matched = 0
unmatched = []
event_map = {}
for w in wiki:
    n = norm(w['name'])
    if n in srr_idx:
        matched += 1
        for sid in srr_idx[n]:
            event_map[sid] = w
    else:
        unmatched.append(w['name'])

print('匹配: %d/%d' % (matched, len(wiki)))
print('未匹配 %d:' % len(unmatched))
for u in unmatched:
    print('  ', u)

print('\n覆盖 SRR 事件实体ID: %d' % len(event_map))
from collections import Counter
seg = Counter(sid[:4] for sid in event_map)
print('按 ID 段:', dict(seg))

json.dump(event_map, open('G:/HSR/StarRailRes_data/event_text_7483.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已保存 event_text_7483.json')
