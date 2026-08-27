# -*- coding: utf-8 -*-
"""校验物品库：名称、评级、存在性 vs StarRailRes items.json"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
items = json.load(open(SRR + "/items.json", encoding="utf-8"))

files = glob.glob(os.path.join(HSR, "items", "*", "*.md"))
report = []
issues = 0
checked = 0
no_id = 0
for fp in files:
    fn = os.path.basename(fp).replace(".md", "")
    # 跳过索引文件（形如 分类.md / 分类_星级.md）
    if re.match(r"^[\u4e00-\u9fff]+(_[一二三四五六七]星)?$", fn):
        continue
    with open(fp, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r">\s*实体ID[：:]\s*(\d+)", text)
    if not m:
        no_id += 1
        continue
    iid = m.group(1)
    checked += 1
    diffs = []
    if iid not in items:
        diffs.append(f"  SRR 无此物品 (ID {iid})")
    else:
        it = items[iid]
        # 名称
        title = fn
        if title != it["name"]:
            diffs.append(f"  名称: 库={title} vs SRR={it['name']}")
        # 评级
        um = re.search(r"\|\s*评级\s*\|\s*([★☆]+)", text)
        if um:
            star = "★" * it["rarity"]
            if um.group(1) != star:
                diffs.append(f"  评级: 库={um.group(1)} vs SRR={star}")
    if diffs:
        issues += 1
        report.append(f"[{iid}] {fn}")
        report.extend(diffs)

print(f"已校验 {checked} 物品，无实体ID文件 {no_id}，发现差异 {issues}")
print("\n".join(report) if report else "（无差异）")
with open(r"G:/HSR/StarRailRes_data/validate_items.md", "w", encoding="utf-8") as f:
    f.write("# 物品库校验报告\n\n")
    f.write(f"已校验 {checked} 物品，无实体ID文件 {no_id}，发现差异 {issues}\n\n")
    f.write("\n".join(report) if report else "（无差异）")
