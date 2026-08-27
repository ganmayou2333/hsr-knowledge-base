# -*- coding: utf-8 -*-
"""对比 SRR 与用户 HSR 知识库：角色/光锥/遗器覆盖 + 内容差异"""
import json, os, re, glob

HSR = r'G:\HSR'
SRR = r'G:/HSR/StarRailRes_repo/index_new/cn'

chars = json.load(open(SRR + '/characters.json', encoding='utf-8'))
lcs = json.load(open(SRR + '/light_cones.json', encoding='utf-8'))
relics = json.load(open(SRR + '/relics.json', encoding='utf-8'))
relic_sets = json.load(open(SRR + '/relic_sets.json', encoding='utf-8'))
items = json.load(open(SRR + '/items.json', encoding='utf-8'))

# ============ 角色对比 ============
srr_ids = set(chars.keys())
# 用户知识库角色
user_files = glob.glob(os.path.join(HSR, 'character', '**', '*.md'), recursive=True)
user_id2name = {}
user_no_id = []
for fp in user_files:
    if os.path.basename(fp) == '角色.md':
        continue
    t = open(fp, encoding='utf-8').read()
    m = re.search(r'>\s*实体ID[：:]\s*(\d+)', t)
    if m:
        user_id2name[m.group(1)] = os.path.basename(fp)
    else:
        user_no_id.append(os.path.basename(fp))

print("=== 角色覆盖 ===")
print(f"SRR 角色数: {len(srr_ids)}  用户角色文件数: {len(user_files)-1}  用户有实体ID: {len(user_id2name)}")
only_srr = sorted(srr_ids - set(user_id2name.keys()), key=lambda x: int(x))
only_user = sorted(set(user_id2name.keys()) - srr_ids, key=lambda x: int(x))
print(f"\n[SRR有 / 用户无] {len(only_srr)} 个:")
for cid in only_srr:
    print(f"  {cid} {chars[cid].get('name')}")
print(f"\n[用户有 / SRR无] {len(only_user)} 个:")
for cid in only_user:
    print(f"  {cid} {user_id2name[cid]}")
print(f"\n[用户无实体ID的文件] {len(user_no_id)} 个:")
for f in user_no_id:
    print(f"  {f}")

# ============ 光锥对比 ============
print("\n=== 光锥覆盖 ===")
srr_lc = set(lcs.keys())
user_lc_files = [os.path.basename(f) for f in glob.glob(os.path.join(HSR, 'lightcone', '**', '*.md'), recursive=True)]
print(f"SRR 光锥数: {len(srr_lc)}  用户光锥文件数: {len(user_lc_files)-1}")

# ============ 遗器对比 ============
print("\n=== 遗器覆盖 ===")
print(f"SRR 遗器套装数: {len(relic_sets)}  用户遗器文件数(含索引): {len(glob.glob(os.path.join(HSR,'relic','**','*.md'), recursive=True))}")
# 用户遗器套装
user_relic_files = glob.glob(os.path.join(HSR, 'relic', '**', '*.md'), recursive=True)
user_set_ids = set()
for fp in user_relic_files:
    t = open(fp, encoding='utf-8').read()
    m = re.search(r'>\s*套装ID[：:]\s*(\d+)', t)
    if m:
        user_set_ids.add(m.group(1))
srr_set_ids = set(relic_sets.keys())
print(f"SRR 套装ID: {len(srr_set_ids)}  用户套装ID: {len(user_set_ids)}")
only_srr_set = sorted(srr_set_ids - user_set_ids, key=lambda x: int(x))
only_user_set = sorted(user_set_ids - srr_set_ids, key=lambda x: int(x))
print(f"[SRR有/用户无] {len(only_srr_set)}: {[(s, relic_sets[s].get('name')) for s in only_srr_set]}")
print(f"[用户有/SRR无] {len(only_user_set)}: {only_user_set}")

# ============ 物品对比 ============
print("\n=== 物品覆盖 ===")
srr_item_ids = set(items.keys())
user_item_files = [f for f in glob.glob(os.path.join(HSR, 'items', '**', '*.md'), recursive=True) if os.path.basename(f) != '物品.md']
print(f"SRR 物品数: {len(srr_item_ids)}  用户物品文件数: {len(user_item_files)}")
