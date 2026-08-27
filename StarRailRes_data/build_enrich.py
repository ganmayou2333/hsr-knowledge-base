# -*- coding: utf-8 -*-
"""匹配 wiki767 到 SRR，输出回填数据 enrich_612.json + 差异分析"""
import json, re

wiki = json.load(open('G:/HSR/StarRailRes_data/wiki767_blessings.json', encoding='utf-8'))
srr = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_blessings.json', encoding='utf-8'))

def norm(s):
    s = s.replace('·', '•').replace('·', '•')
    s = s.replace(':', '：').replace(':', '：')
    return re.sub(r'[\s\u3000]', '', s)

# SRR 索引
srr_idx = {}
for i, v in srr.items():
    srr_idx.setdefault(norm(v.get('name', '')), []).append(i)

def split_eff(eff):
    if '强化前：' in eff and '强化后：' in eff:
        i1 = eff.find('强化前：') + 4
        i2 = eff.find('强化后：', i1)
        return eff[i1:i2].strip(), eff[i2+4:].strip()
    return eff.strip(), None

enrich = {}   # sid -> {path, pre, post}
diff_desc = []
diff_enh = []
path_fix = []  # ID推断 vs wiki 不同

matched_ids = set()
for w in wiki:
    n = norm(w['name'])
    if n not in srr_idx:
        continue
    pre, post = split_eff(w['eff'])
    for sid in srr_idx[n]:
        matched_ids.add(sid)
        v = srr[sid]
        enrich[sid] = {'path': w['path'], 'pre': pre, 'post': post}
        # 对比 desc
        srr_desc = (v.get('desc') or '').strip()
        srr_enh = (v.get('enhanced_desc') or '').strip()
        if pre and srr_desc and pre != srr_desc:
            diff_desc.append((sid, w['name'], pre[:50], srr_desc[:50]))
        if post and srr_enh and post != srr_enh:
            diff_enh.append((sid, w['name'], post[:50], srr_enh[:50]))

json.dump(enrich, open('G:/HSR/StarRailRes_data/enrich_612.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('匹配 SRR 实体: %d' % len(matched_ids))
print('enrich 条目: %d' % len(enrich))
print('强化前 != SRR desc: %d' % len(diff_desc))
for d in diff_desc[:12]:
    print('  [%s] wiki:%s ||| srr:%s' % (d[0], d[2], d[3]))
print('强化后 != SRR enhanced: %d' % len(diff_enh))
for d in diff_enh[:8]:
    print('  [%s] wiki:%s ||| srr:%s' % (d[0], d[2], d[3]))

# 命途：wiki 与 ID 推断对比
ID_PATH = {('612%d' % i): ['存护','记忆','虚无','丰饶','巡猎','毁灭','欢愉','繁育','智识'][i] for i in range(9)}
for sid, e in list(enrich.items()):
    idp = ID_PATH.get(sid[:4])
    if idp and e['path'] != idp:
        path_fix.append((sid, idp, e['path']))
print('\nID推断与wiki命途不同(多为主命途+双命途): %d' % len(path_fix))
for p in path_fix[:10]:
    print('  %s: 推断=%s wiki=%s' % p)
