# -*- coding: utf-8 -*-
"""逐个核对差异角色：用户星魂 vs SRR 星魂"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
ranks = json.load(open(SRR + "/character_ranks.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))

# SRR 1224 三月七巡猎星魂
print("=== SRR 1224（巡猎三月七?） ===")
print("name:", chars.get('1224', {}).get('name'), "path:", chars.get('1224', {}).get('path'))
for i, rid in enumerate(chars.get('1224', {}).get('ranks', [])):
    r = ranks.get(rid, {})
    print(f"  E{i+1} [{rid}] {r.get('name')}: {r.get('desc')[:55]}")

# 核对差异角色
targets = ['1004', '1005', '1102', '1205', '1306', '1307', '1212', '1001']
for cid in targets:
    fp = None
    for f in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
        t = open(f, encoding="utf-8").read()
        if re.search(r">\s*实体ID[：:]\s*" + cid, t):
            fp, text = f, t
            break
    if not fp:
        continue
    print("\n" + "=" * 70)
    print(f"[{cid}] {os.path.basename(fp)}")
    sm = re.search(r"##\s*星魂(.*?)(?=\n## |\Z)", text, re.S)
    if not sm:
        continue
    user_ranks = {}
    for line in sm.group(1).splitlines():
        line = line.strip()
        if line.startswith("|") and not line.startswith("|---"):
            le = line.replace(r"\|", "\x00")
            cells = [c.strip() for c in le.strip("|").split("|")]
            if len(cells) >= 3 and cells[0].startswith("E"):
                user_ranks[cells[0]] = (cells[1], cells[2].replace("\x00", "|"))
    for i, rid in enumerate(chars.get(cid, {}).get('ranks', [])):
        r = ranks.get(rid, {})
        ekey = f"E{i+1}"
        if ekey not in user_ranks:
            continue
        uname, utext = user_ranks[ekey]
        sname, sdesc = r.get('name', ''), r.get('desc', '')
        match = (uname == sname)
        print(f"\n  {ekey} 用户[{uname}] SRR[{sname}] 名称{'一致' if match else '不同'}")
        print(f"    用户: {utext[:90]}")
        print(f"    SRR : {sdesc[:90]}")
