# -*- coding: utf-8 -*-
"""补充：遗器套装级对比 + 物品缺失示例 + 角色文件ID检查"""
import os, json, glob, re

srr = 'G:/HSR/StarRailRes_repo/index_new/cn'
relic_sets = json.load(open(srr + '/relic_sets.json', encoding='utf-8'))
relics = json.load(open(srr + '/relics.json', encoding='utf-8'))
items = json.load(open(srr + '/items.json', encoding='utf-8'))
characters = json.load(open(srr + '/characters.json', encoding='utf-8'))

def md_ids(root):
    ids = {}
    for fp in glob.glob(os.path.join(root, '**', '*.md'), recursive=True):
        t = open(fp, encoding='utf-8', errors='ignore').read()
        m = re.search(r'>\s*实体ID[：:]\s*(\S+)', t)
        if m:
            ids[m.group(1).strip()] = fp
    return ids

# ===== 遗器套装级对比 =====
hsr_rel = md_ids('G:/HSR/relic')
srr_set_ids = set(relic_sets.keys())  # 套装 id（如 101,102...）
hsr_rel_ids = set(hsr_rel.keys())
miss_sets = sorted(srr_set_ids - hsr_rel_ids, key=int)
print('=== 遗器套装 === SRR套装=%d HSR文件=%d' % (len(srr_set_ids), len(hsr_rel_ids)))
print('SRR有HSR无的套装: %d 个' % len(miss_sets))
for sid in miss_sets:
    rs = relic_sets[sid]
    name = rs.get('name', '?')
    # 找套装类型
    typ = '?'
    for rid, r in relics.items():
        if str(r.get('set_id')) == str(sid):
            typ = r.get('type', {}).get('name', '?') if isinstance(r.get('type'), dict) else str(r.get('type', '?'))
            break
    print('  %s %s (类型:%s)' % (sid, name, typ))
print()

# ===== 物品缺失示例 =====
hsr_item = md_ids('G:/HSR/items')
srr_item_ids = set(items.keys())
hsr_item_ids = set(hsr_item.keys())
miss_item = sorted(srr_item_ids - hsr_item_ids, key=int)
def itype(iid):
    it = items[iid].get('type', {})
    if isinstance(it, dict):
        return it.get('name', '?')
    return str(it)
from collections import Counter
c = Counter(itype(i) for i in miss_item)
for typ, n in c.most_common():
    ex = [items[i].get('name', '?') for i in miss_item if itype(i) == typ][:8]
    print('【%s】缺失 %d 个，示例: %s' % (typ, n, '、'.join(ex)))
print()

# ===== HSR 角色文件 vs SRR 角色 id 检查 =====
all_char_files = glob.glob(os.path.join('G:/HSR/character', '**', '*.md'), recursive=True)
print('HSR 角色文件总数: %d' % len(all_char_files))
no_id = []
for fp in all_char_files:
    t = open(fp, encoding='utf-8', errors='ignore').read()
    if not re.search(r'>\s*实体ID[：:]', t):
        no_id.append(os.path.basename(fp))
print('无实体ID字段的角色文件: %d 个' % len(no_id))
for f in no_id:
    print('  ', f)
