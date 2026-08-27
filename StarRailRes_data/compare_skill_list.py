# -*- coding: utf-8 -*-
"""对 13 个角色重新读取实际库值 vs SRR 值，与技能材料差异清单对照"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"

items = json.load(open(SRR + "/items.json", encoding="utf-8"))
trees = json.load(open(SRR + "/character_skill_trees.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))

SKILL_ANCHORS = {"Point01", "Point02", "Point03", "Point04"}

def srr_skill_materials(cid):
    agg = {}
    seen_anchor = set()
    for tid in chars[cid]["skill_trees"]:
        t = trees.get(tid, {})
        if t.get("anchor") not in SKILL_ANCHORS:
            continue
        if t.get("anchor") in seen_anchor:
            continue
        seen_anchor.add(t.get("anchor"))
        for lv in t.get("levels", []):
            for m in lv.get("materials", []):
                name = items.get(m["id"], {}).get("name", m["id"])
                agg[name] = agg.get(name, 0) + m["num"]
    return agg

def parse_user_table(text):
    m = re.search(r"##\s*技能材料[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    if not m:
        return None
    rows = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        line_esc = line.replace(r"\|", "\x00")
        cells = [c.strip() for c in line_esc.strip("|").split("|")]
        if len(cells) < 2:
            continue
        k = cells[0].replace("\x00", "|")
        v = cells[1].replace("\x00", "|")
        if k in ("材料", "") or set(k) <= set("-:") or k.startswith("属性"):
            continue
        m2 = re.search(r"\[\[([^\]]*?)\|([^\]]+)\]\]", k)
        if m2:
            k = m2.group(2).strip()
        elif k.startswith("[["):
            k = re.sub(r"\[\[|\]\]", "", k).split("/")[-1].strip()
        rows[k] = v
    return rows

def to_num(s):
    return int(re.sub(r"[^\d]", "", s or "0"))

targets = ['1402', '1407', '1409', '1413', '1415', '1512',
           '1501', '1502', '1505', '1506', '1513', '8007', '8009']

id2file = {}
for fp in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
    t = open(fp, encoding="utf-8").read()
    mm = re.search(r">\s*实体ID[：:]\s*(\d+)", t)
    if mm:
        id2file[mm.group(1)] = (fp, t)

for cid in targets:
    fp, text = id2file.get(cid, (None, None))
    if not fp:
        print(f"[{cid}] 未找到文件")
        continue
    srr = srr_skill_materials(cid)
    user = parse_user_table(text)
    print(f"\n[{cid}] {os.path.basename(fp)}")
    all_keys = set(list(srr.keys()) + list(user.keys()))
    for k in sorted(all_keys):
        u = user.get(k, '缺')
        s = srr.get(k, '缺')
        flag = "OK " if (u != '缺' and s != '缺' and to_num(u) == s) else "DIFF"
        print(f"  {k}: 库={u} vs SRR={s}  [{flag}]")
