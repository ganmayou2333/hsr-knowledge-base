# -*- coding: utf-8 -*-
"""对比 SRR 与 HSR 知识库的实体覆盖，找出 SRR 有而 HSR 无的部分"""
import os, json, glob, re

srr = 'G:/HSR/StarRailRes_repo/index_new/cn'
characters = json.load(open(srr + '/characters.json', encoding='utf-8'))
light_cones = json.load(open(srr + '/light_cones.json', encoding='utf-8'))
relics = json.load(open(srr + '/relics.json', encoding='utf-8'))
items = json.load(open(srr + '/items.json', encoding='utf-8'))
relic_sets = json.load(open(srr + '/relic_sets.json', encoding='utf-8'))

def md_ids(root):
    ids = {}
    for fp in glob.glob(os.path.join(root, '**', '*.md'), recursive=True):
        t = open(fp, encoding='utf-8', errors='ignore').read()
        m = re.search(r'>\s*实体ID[：:]\s*(\S+)', t)
        if m:
            ids[m.group(1).strip()] = fp
    return ids

# ============ 角色 ============
hsr_char = md_ids('G:/HSR/character')
srr_char_ids = set(characters.keys())
hsr_char_ids = set(hsr_char.keys())
miss_char = sorted(srr_char_ids - hsr_char_ids, key=int)
print('=== 角色 === SRR=%d HSR=%d' % (len(srr_char_ids), len(hsr_char_ids)))
print('SRR有HSR无: %d 个' % len(miss_char))
for cid in miss_char:
    print('  %s %s' % (cid, characters[cid].get('name', '')))
print()

# ============ 光锥 ============
hsr_lc = md_ids('G:/HSR/lightcone')
srr_lc_ids = set(light_cones.keys())
hsr_lc_ids = set(hsr_lc.keys())
miss_lc = sorted(srr_lc_ids - hsr_lc_ids, key=int)
print('=== 光锥 === SRR=%d HSR=%d' % (len(srr_lc_ids), len(hsr_lc_ids)))
print('SRR有HSR无: %d 个' % len(miss_lc))
for lid in miss_lc:
    print('  %s %s' % (lid, light_cones[lid].get('name', '')))
print()

# ============ 遗器 ============
hsr_rel = md_ids('G:/HSR/relic')
# SRR 遗器 id 是套装+部位（如 setid+piece），HSR 按套装收录（实体ID可能=套装id）
# 先看双方 id 形式
srr_rel_ids = set(relics.keys())
print('=== 遗器 === SRR=%d HSR=%d' % (len(srr_rel_ids), len(hsr_rel)))
# 采样 SRR 遗器 id
samp = sorted(srr_rel_ids)[:10]
print('SRR 遗器 id 样例:', samp)
for sid in samp:
    r = relics[sid]
    print('   ', sid, r.get('name', ''), '套装id=', r.get('set_id'))
print('HSR 遗器 id 样例:', sorted(hsr_rel.keys())[:10])
print()

# ============ 物品 ============
hsr_item = md_ids('G:/HSR/items')
srr_item_ids = set(items.keys())
hsr_item_ids = set(hsr_item.keys())
miss_item = sorted(srr_item_ids - hsr_item_ids, key=int)
print('=== 物品 === SRR=%d HSR=%d' % (len(srr_item_ids), len(hsr_item_ids)))
print('SRR有HSR无: %d 个' % len(miss_item))
# 按物品种类统计缺失
def item_type(iid):
    it = items[iid].get('type', {}).get('name', '?') if isinstance(items[iid].get('type'), dict) else str(items[iid].get('type', '?'))
    return it
from collections import Counter
c = Counter()
for iid in miss_item:
    c[item_type(iid)] += 1
print('缺失物品按类型分布:')
for k, v in c.most_common():
    print('  %s: %d' % (k, v))
