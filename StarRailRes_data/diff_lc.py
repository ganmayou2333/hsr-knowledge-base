# -*- coding: utf-8 -*-
import json, os, re, glob

HSR = r'G:\HSR'
SRR = r'G:/HSR/StarRailRes_repo/index_new/cn'

lcs = json.load(open(SRR + '/light_cones.json', encoding='utf-8'))
srr_lc = set(lcs.keys())

user_files = glob.glob(os.path.join(HSR, 'lightcone', '**', '*.md'), recursive=True)
user_id2name = {}
user_noid = []
for fp in user_files:
    if os.path.basename(fp) == '光锥.md':
        continue
    t = open(fp, encoding='utf-8').read()
    m = re.search(r'>\s*实体ID[：:]\s*(\d+)', t)
    if m:
        user_id2name[m.group(1)] = os.path.basename(fp)
    else:
        user_noid.append(os.path.basename(fp))

only_srr = sorted(srr_lc - set(user_id2name.keys()), key=lambda x: int(x))
only_user = sorted(set(user_id2name.keys()) - srr_lc, key=lambda x: int(x))

print(f"SRR 光锥: {len(srr_lc)}  用户光锥(有ID): {len(user_id2name)}  无ID文件: {len(user_noid)}")
print(f"\n[SRR有/用户无] {len(only_srr)} 个:")
for i in only_srr:
    print(f"  {i} {lcs[i].get('name')}")
print(f"\n[用户有/SRR无] {len(only_user)} 个:")
for i in only_user:
    print(f"  {i} {user_id2name[i]}")
print(f"\n[用户无ID光锥文件] {len(user_noid)} 个:")
for f in user_noid:
    print(f"  {f}")
