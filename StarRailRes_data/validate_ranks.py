# -*- coding: utf-8 -*-
"""校验星魂效果：用户星魂表格 vs SRR character_ranks 描述数值"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
ranks = json.load(open(SRR + "/character_ranks.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))

def extract_nums(s):
    """提取文本中所有百分数和整数数值（含小数）"""
    return set(round(float(x), 2) for x in re.findall(r"([\d.]+)%", s or ""))

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
    if cid not in chars:
        continue
    # 解析用户星魂表格
    sm = re.search(r"##\s*星魂(.*?)(?=\n## |\Z)", text, re.S)
    if not sm:
        continue
    user_ranks = {}
    for line in sm.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        le = line.replace(r"\|", "\x00")
        cells = [c.strip() for c in le.strip("|").split("|")]
        if len(cells) < 3:
            continue
        key = cells[0].replace("\x00", "|")
        if key.startswith("E"):
            user_ranks[key] = cells[2].replace("\x00", "|")
    if not user_ranks:
        continue
    checked += 1
    diffs = []
    rids = chars[cid].get("ranks", [])
    for i, rid in enumerate(rids):
        srr = ranks.get(rid, {})
        ekey = f"E{i+1}"
        if ekey not in user_ranks:
            continue
        srr_desc = srr.get("desc", "")
        srr_nums = extract_nums(srr_desc)
        user_text = user_ranks[ekey]
        user_nums = extract_nums(user_text)
        # SRR 中的数值（排除 100/200 等通用百分比后）应能在用户文本中找到
        missing = sorted(srr_nums - user_nums)
        if missing and not (set(missing) <= {0, 100, 200}):
            diffs.append(f"  {ekey} {srr.get('name','')}: SRR含数值{missing} 用户文本未见 | SRR: {srr_desc[:80]}...")
    if diffs:
        issues += 1
        report.append(f"[{cid}] {os.path.basename(fp)}")
        report.extend(diffs)

print(f"已校验 {checked} 角色星魂，发现差异 {issues}")
print("\n".join(report) if report else "（无差异）")
with open(r"G:/HSR/StarRailRes_data/validate_ranks.md", "w", encoding="utf-8") as f:
    f.write("# 星魂效果校验报告\n\n")
    f.write(f"已校验 {checked} 角色星魂，发现差异 {issues}\n\n")
    f.write("\n".join(report) if report else "（无差异）")
