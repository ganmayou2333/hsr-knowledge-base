# -*- coding: utf-8 -*-
"""恢复备份 + 用正确处理转义的逻辑修正技能材料（v2）"""
import json, os, re, glob, shutil

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
BACKUP = r"G:/HSR/StarRailRes_data/backup_20260827"

# ===== 第一步：恢复备份 =====
restored = []
for bf in glob.glob(os.path.join(BACKUP, "技能材料修正前_*.md")):
    name = os.path.basename(bf).replace("技能材料修正前_", "")
    matches = glob.glob(os.path.join(HSR, "character", "**", name), recursive=True)
    if matches:
        shutil.copy2(bf, matches[0])
        restored.append(name)
        print(f"已恢复: {name}")
    else:
        print(f"!! 未找到原文件: {name}")
print(f"恢复 {len(restored)} 个文件\n")

# ===== 第二步：重新修正 =====
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

def fmt(n):
    return f"{n:,}"

targets = ['1402', '1407', '1409', '1413', '1415', '1512',
           '1501', '1502', '1505', '1506', '1513', '8007', '8009']

id2file = {}
for fp in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
    t = open(fp, encoding="utf-8").read()
    mm = re.search(r">\s*实体ID[：:]\s*(\d+)", t)
    if mm:
        id2file[mm.group(1)] = fp

total = 0
for cid in targets:
    fp = id2file[cid]
    text = open(fp, encoding="utf-8").read()
    srr = srr_skill_materials(cid)
    m = re.search(r"(##\s*技能材料[^\n]*\n)(.*?)(?=\n## |\Z)", text, re.S)
    if not m:
        print(f"[{cid}] 未找到技能材料章节")
        continue
    header, body = m.group(1), m.group(2)
    new_lines = []
    fixed = 0
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            new_lines.append(line)
            continue
        # 保护 \| 转义竖线
        le = line.replace(r"\|", "\x00")
        cells = [c.strip() for c in le.strip("|").split("|")]
        if len(cells) < 2:
            new_lines.append(line)
            continue
        k, v = cells[0], cells[1]
        if k in ("材料", "") or set(k) <= set("-:") or k.startswith("属性"):
            new_lines.append(line)
            continue
        # 提取材料显示名（\x00 为 \| 转义的占位符）
        m2 = re.search(r"\[\[([^\]]*?)[\x00|]([^\]]+)\]\]", k)
        if m2:
            kname = m2.group(2).strip()
        elif k.startswith("[["):
            kname = re.sub(r"\[\[|\]\]", "", k).split("/")[-1].strip()
        else:
            kname = k
        if kname in srr:
            target = srr[kname]
            cur = int(re.sub(r"[^\d]", "", v or "0"))
            if cur != target:
                # 只替换数量单元格，重组时还原转义
                cells[1] = fmt(target)
                newline = "| " + " | ".join(cells).replace("\x00", r"\|") + " |"
                new_lines.append(newline)
                fixed += 1
                print(f"  {kname}: {cur} -> {target}")
                continue
        new_lines.append(line)
    new_text = text[:m.start()] + header + "\n".join(new_lines) + text[m.end():]
    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"[{cid}] {os.path.basename(fp)} 修正 {fixed} 项")
    total += fixed

print(f"\n共修正 {total} 项")
