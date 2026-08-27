# -*- coding: utf-8 -*-
"""校验遗器库：套装名、套装效果、部位 vs StarRailRes"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
sets = json.load(open(SRR + "/relic_sets.json", encoding="utf-8"))
rel = json.load(open(SRR + "/relics.json", encoding="utf-8"))

# 部位类型中文
TYPE_CN = {"HEAD": "头部", "HAND": "手部", "BODY": "躯干", "FOOT": "脚部",
           "NECK": "位面球", "OBJECT": "连结绳"}

def norm(s):
    return re.sub(r"\s+", "", s or "")

files = glob.glob(os.path.join(HSR, "relic", "*", "*.md"))
report = []
issues = 0
checked = 0
for fp in files:
    fn = os.path.basename(fp).replace(".md", "")
    with open(fp, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r">\s*实体ID[：:]\s*(\d+)", text)
    if not m:
        continue
    sid = m.group(1)
    if sid not in sets:
        report.append(f"[{sid}] {fn}: SRR 无此套装")
        issues += 1
        continue
    checked += 1
    s = sets[sid]
    diffs = []
    # 名称
    nm = re.search(r"\|\s*名称\s*\|\s*([^\s|]+)", text)
    if nm and nm.group(1) != s["name"]:
        diffs.append(f"  名称: 库={nm.group(1)} vs SRR={s['name']}")
    # 套装效果（每条 SRR desc 需出现在库文本中）
    eff_text = ""
    em = re.search(r"##\s*套装效果(.*?)(?=\n## |\Z)", text, re.S)
    if em:
        eff_text = em.group(1)
    for d in s.get("desc", []):
        if norm(d) not in norm(eff_text):
            diffs.append(f"  效果缺失: {d}")
    # 部位：SRR 该套装全部 unique 遗器名是否在库中出现
    srr_parts = []
    for r in rel.values():
        if r.get("set_id") == sid and r.get("name") not in srr_parts:
            srr_parts.append(r.get("name"))
    missing_parts = [p for p in srr_parts if norm(p) not in norm(text)]
    if missing_parts:
        diffs.append(f"  部位缺失: {missing_parts}")
    if diffs:
        issues += 1
        report.append(f"[{sid}] {fn}")
        report.extend(diffs)

print(f"已校验 {checked} 遗器套装，发现差异 {issues}")
print("\n".join(report) if report else "（无差异）")
with open(r"G:/HSR/StarRailRes_data/validate_relic.md", "w", encoding="utf-8") as f:
    f.write("# 遗器库校验报告\n\n")
    f.write(f"已校验 {checked} 遗器套装，发现差异 {issues}\n\n")
    f.write("\n".join(report) if report else "（无差异）")
