# -*- coding: utf-8 -*-
"""分析 wiki767 效果与 SRR desc/enhanced 的差异"""
import json, re

wiki = json.load(open('G:/HSR/StarRailRes_data/wiki767_blessings.json', encoding='utf-8'))
srr = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_blessings.json', encoding='utf-8'))

def split_eff(eff):
    """拆分 '强化前：... 强化后：...' 或 只有一段"""
    if '强化前：' in eff and '强化后：' in eff:
        i1 = eff.find('强化前：') + 4
        i2 = eff.find('强化后：', i1)
        return eff[i1:i2].strip(), eff[i2+4:].strip()
    return eff.strip(), None

n = 0
same = 0
diff = []
for w in wiki:
    pre, post = split_eff(w['eff'])
    for sid in w.get('srr_ids', []):
        v = srr[sid]
        n += 1
        srr_desc = (v.get('desc') or '').strip()
        srr_enh = (v.get('enhanced_desc') or '').strip()
        # 对比强化前 vs SRR desc
        if pre and pre == srr_desc:
            same += 1
        elif pre:
            diff.append((w['name'], sid, 'desc', pre[:60], srr_desc[:60]))

print('对比条数: %d' % n)
print('强化前==SRR desc: %d' % same)
print('强化前!=SRR desc: %d' % len(diff))
for d in diff[:15]:
    print('  [%s|%s] wiki:%s ||| SRR:%s' % (d[0], d[1], d[2], d[3]))
