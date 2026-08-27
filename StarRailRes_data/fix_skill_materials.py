# -*- coding: utf-8 -*-
"""备份 + 按 SRR 正确值修正 13 个角色的技能材料表格"""
import json, os, re, glob, shutil

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
BACKUP = r"G:/HSR/StarRailRes_data/backup_20260827"
os.makedirs(BACKUP, exist_ok=True)

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

targets = ['1402', '1407', '1409', '1413', '1415', '1512',
           '1501', '1502', '1505', '1506', '1513', '8007', '8009']

id2file = {}
for fp in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
    t = open(fp, encoding="utf-8").read()
    mm = re.search(r">\s*实体ID[：:]\s*(\d+)", t)
    if mm:
        id2file[mm.group(1)] = (fp, t)

def fmt(n):
    """千分位格式化"""
    return f"{n:,}"

total_fixed = 0
for cid in targets:
    fp, text = id2file[cid]
    srr = srr_skill_materials(cid)
    # 备份
    bname = os.path.join(BACKUP, f"技能材料修正前_{os.path.basename(fp)}")
    shutil.copy2(fp, bname)
    # 定位技能材料章节
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
        le = line.replace(r"\|", "\x00")
        cells = [c.strip() for c in le.strip("|").split("|")]
        if len(cells) < 2:
            new_lines.append(line)
            continue
        k = cells[0].replace("\x00", "|")
        v = cells[1].replace("\x00", "|")
        if k in ("材料", "") or set(k) <= set("-:") or k.startswith("属性"):
            new_lines.append(line)
            continue
        # 解析材料名
        m2 = re.search(r"\[\[([^\]]*?)\|([^\]]+)\]\]", k)
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
                # 替换该行的数量列（保持 | 分隔结构）
                # 重新按 | 切分原始行
                raw_cells = line.split("|")
                # raw_cells[0] 是空，[1] 材料，[2] 数量
                if len(raw_cells) >= 3:
                    raw_cells[2] = fmt(target)
                    new_line = "|".join(raw_cells)
                    new_lines.append(new_line)
                    fixed += 1
                    print(f"  {kname}: {cur} -> {target}")
                    continue
        new_lines.append(line)
    new_text = text[:m.start()] + header + "\n".join(new_lines) + text[m.end():]
    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"[{cid}] {os.path.basename(fp)} 修正 {fixed} 项")
    total_fixed += fixed

print(f"\n共修正 {total_fixed} 项")
