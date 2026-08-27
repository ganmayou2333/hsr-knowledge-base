# -*- coding: utf-8 -*-
"""校验角色技能材料：SRR skill_trees 技能节点(Point01-04)材料汇总 vs 用户库「技能材料」表格"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"

items = json.load(open(SRR + "/items.json", encoding="utf-8"))
trees = json.load(open(SRR + "/character_skill_trees.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))

SKILL_ANCHORS = {"Point01", "Point02", "Point03", "Point04"}

def srr_skill_materials(cid):
    """汇总 4 个技能节点的全部升级材料 {中文名: 数量}（按锚点去重，双形态只算一套）"""
    if cid not in chars:
        return None
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
            mats = lv.get("materials", [])
            if not mats:
                continue
            for m in mats:
                name = items.get(m["id"], {}).get("name", m["id"])
                agg[name] = agg.get(name, 0) + m["num"]
    return agg

def parse_user_table(text):
    """解析「技能材料」表格，返回 {显示名: 数量}"""
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

id2file = {}
for fp in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
    t = open(fp, encoding="utf-8").read()
    mm = re.search(r">\s*实体ID[：:]\s*(\d+)", t)
    if mm:
        id2file[mm.group(1)] = (fp, t)

report = []
issues = 0
checked = 0
for cid, (fp, text) in sorted(id2file.items(), key=lambda x: int(x[0])):
    srr = srr_skill_materials(cid)
    if srr is None:
        continue
    user = parse_user_table(text)
    if user is None:
        report.append(f"[{cid}] 无「技能材料」表格")
        issues += 1
        continue
    checked += 1
    diffs = []
    for name, num in srr.items():
        if name not in user:
            diffs.append(f"  缺 {name}={num}")
        elif to_num(user[name]) != num:
            diffs.append(f"  {name}: 库={user[name]} vs SRR={num}")
    for name, v in user.items():
        if name not in srr:
            diffs.append(f"  多余 {name}={v}")
    if diffs:
        issues += 1
        report.append(f"[{cid}] {os.path.basename(fp)}")
        report.extend(diffs)

print(f"已校验 {checked} 角色，发现差异 {issues}")
print("\n".join(report))
with open(r"G:/HSR/StarRailRes_data/validate_skill_material.md", "w", encoding="utf-8") as f:
    f.write("# 技能材料校验报告\n\n")
    f.write(f"已校验 {checked} 角色，发现差异 {issues}\n\n")
    f.write("\n".join(report) if report else "（无差异）")
