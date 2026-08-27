# -*- coding: utf-8 -*-
"""校验角色晋阶材料：SRR promotions.materials 汇总 vs 用户库「晋阶材料」表格"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"

items = json.load(open(SRR + "/items.json", encoding="utf-8"))
promo = json.load(open(SRR + "/character_promotions.json", encoding="utf-8"))

def srr_promo_materials(cid):
    """汇总 0-5 次晋阶的总材料 {中文名: 数量}"""
    j = promo.get(cid)
    if not j:
        return None
    agg = {}
    for step in j["materials"][:6]:
        for m in step:
            name = items.get(m["id"], {}).get("name", m["id"])
            agg[name] = agg.get(name, 0) + m["num"]
    return agg

def parse_user_table(text, section):
    """解析表格，返回 {显示名: 数量字符串}。section 形如 r'##\\s*晋阶材料'"""
    m = re.search(section + r"[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    if not m:
        return None
    rows = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # 保护 Obsidian 转义管道符 \|，避免被 split('|') 误拆
        line_esc = line.replace(r"\|", "\x00")
        cells = [c.strip() for c in line_esc.strip("|").split("|")]
        if len(cells) < 2:
            continue
        k = cells[0].replace("\x00", "|")
        v = cells[1].replace("\x00", "|")
        if k in ("材料", "") or set(k) <= set("-:") or k.startswith("属性"):
            continue
        # 提取双链显示名
        m2 = re.search(r"\[\[([^\]]*?)\|([^\]]+)\]\]", k)
        if m2:
            k = m2.group(2).strip()
        elif k.startswith("[["):
            k = re.sub(r"\[\[|\]\]", "", k).split("/")[-1].strip()
        rows[k] = v
    return rows

def to_num(s):
    return int(re.sub(r"[^\d]", "", s or "0"))

# 用户角色文件
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
    srr = srr_promo_materials(cid)
    if srr is None:
        continue
    user = parse_user_table(text, r"##\s*晋阶材料")
    if user is None:
        report.append(f"[{cid}] 无「晋阶材料」表格")
        issues += 1
        continue
    checked += 1
    diffs = []
    # SRR 有而用户缺 / 数量不同
    for name, num in srr.items():
        if name not in user:
            diffs.append(f"  缺 {name}={num}")
        elif to_num(user[name]) != num:
            diffs.append(f"  {name}: 库={user[name]} vs SRR={num}")
    # 用户有而 SRR 无
    for name, v in user.items():
        if name not in srr:
            diffs.append(f"  多余 {name}={v}")
    if diffs:
        issues += 1
        fname = os.path.basename(fp)
        report.append(f"[{cid}] {fname}")
        report.extend(diffs)

print(f"已校验 {checked} 角色，发现差异 {issues}")
print("\n".join(report))
with open(r"G:/HSR/StarRailRes_data/validate_promo_material.md", "w", encoding="utf-8") as f:
    f.write("# 晋阶材料校验报告\n\n")
    f.write(f"已校验 {checked} 角色，发现差异 {issues}\n\n")
    f.write("\n".join(report) if report else "（无差异）")
