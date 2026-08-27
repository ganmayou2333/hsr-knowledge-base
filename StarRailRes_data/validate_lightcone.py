# -*- coding: utf-8 -*-
"""校验光锥库：基础属性(Lv.80)、晋阶材料、评级、命途 vs StarRailRes"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
lc = json.load(open(SRR + "/light_cones.json", encoding="utf-8"))
lcp = json.load(open(SRR + "/light_cone_promotions.json", encoding="utf-8"))
items = json.load(open(SRR + "/items.json", encoding="utf-8"))

PATH_CN = {"Knight": "存护", "Rogue": "巡猎", "Mage": "智识", "Warlock": "虚无",
           "Warrior": "毁灭", "Shaman": "同谐", "Priest": "丰饶", "Memory": "记忆",
           "Elation": "欢愉"}

def srr_lv80(cid):
    p = lcp.get(cid)
    if not p or not p.get("values"):
        return None
    v = p["values"][-1]
    return {k: round(v[k]["base"] + v[k]["step"] * 79) for k in v}

def srr_materials(cid):
    """汇总光锥 0-5 晋阶材料，返回 (信用点, 材料名列表[按出现顺序聚合])"""
    p = lcp.get(cid)
    if not p:
        return None, None
    agg = {}
    order = []
    for step in p["materials"][:6]:
        for m in step:
            name = items.get(m["id"], {}).get("name", m["id"])
            if name == "信用点":
                continue
            if name not in agg:
                order.append(name)
            agg[name] = agg.get(name, 0) + m["num"]
    credit = sum(m["num"] for step in p["materials"][:6] for m in step if m["id"] == "2")
    return credit, [(n, agg[n]) for n in order]

# 扫描用户光锥文件
files = glob.glob(os.path.join(HSR, "lightcone", "*", "*.md"))
report = []
issues = 0
checked = 0
for fp in files:
    fn = os.path.basename(fp).replace(".md", "")
    with open(fp, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r">\s*实体ID[：:]\s*(\d+)", text)
    if not m:
        continue  # 索引文件
    cid = m.group(1)
    if cid not in lc:
        report.append(f"[{cid}] {fn}: SRR 无此光锥")
        issues += 1
        continue
    checked += 1
    diffs = []
    # 评级
    rar = lc[cid]["rarity"]
    star = "★" * rar
    um = re.search(r"\|\s*评级\s*\|\s*([★☆]+)", text)
    if um and um.group(1) != star:
        diffs.append(f"  评级: 库={um.group(1)} vs SRR={star}")
    # 命途
    path = PATH_CN.get(lc[cid]["path"], lc[cid]["path"])
    pm = re.search(r"\|\s*命途\s*\|\s*([^\s|]+)", text)
    if pm and pm.group(1) != path:
        diffs.append(f"  命途: 库={pm.group(1)} vs SRR={path}")
    # 基础属性
    sb = srr_lv80(cid)
    if sb:
        bm = re.search(r"##\s*基础属性.*?\n\|\s*(生命值|生命)\s*\|\s*(攻击力)\s*\|\s*(防御力)[^\n]*\n\|[-:|\s]+\|\n\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)", text, re.S)
        if bm:
            uh, ua, ud = int(bm.group(4).replace(",", "")), int(bm.group(5).replace(",", "")), int(bm.group(6).replace(",", ""))
            if abs(uh - sb["hp"]) > 1: diffs.append(f"  生命: 库={uh} vs SRR≈{sb['hp']}")
            if abs(ua - sb["atk"]) > 1: diffs.append(f"  攻击: 库={ua} vs SRR≈{sb['atk']}")
            if abs(ud - sb["def"]) > 1: diffs.append(f"  防御: 库={ud} vs SRR≈{sb['def']}")
        else:
            diffs.append("  基础属性表格未解析到")
    # 晋阶材料
    credit, mats = srr_materials(cid)
    if credit is not None:
        mm = re.search(r"-\s*(?:晋阶材料\s*/)?\s*Level\s*80\s*/(.*)", text)
        if mm:
            parts = [x.strip() for x in mm.group(1).split("/")]
            nums = [int(re.sub(r"[^\d]", "", x)) for x in parts if re.sub(r"[^\d]", "", x)]
            # 第一个是信用点
            if nums:
                uc = nums[0]
                unums = nums[1:]
                if uc != credit:
                    diffs.append(f"  晋阶信用点: 库={uc:,} vs SRR={credit:,}")
                srr_nums = [n for _, n in mats]
                # 多重集合对比
                if sorted(unums) != sorted(srr_nums):
                    diffs.append(f"  晋阶材料数量: 库={unums} vs SRR={srr_nums}")
        else:
            diffs.append("  晋阶材料行未解析到")
    if diffs:
        issues += 1
        report.append(f"[{cid}] {fn}")
        report.extend(diffs)

print(f"已校验 {checked} 光锥，发现差异 {issues}")
print("\n".join(report) if report else "（无差异）")
with open(r"G:/HSR/StarRailRes_data/validate_lightcone.md", "w", encoding="utf-8") as f:
    f.write("# 光锥库校验报告\n\n")
    f.write(f"已校验 {checked} 光锥，发现差异 {issues}\n\n")
    f.write("\n".join(report) if report else "（无差异）")
