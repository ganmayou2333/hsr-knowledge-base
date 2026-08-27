# -*- coding: utf-8 -*-
"""
HSR 知识库 vs StarRailRes 校验
校验维度：
1. 基础属性（Lv.80）：promotions values 晋阶6 base + step*(79)
2. 总属性加成：skill_trees 属性节点汇总
输出差异报告
"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"

def load_srr(name):
    with open(os.path.join(SRR, name), encoding="utf-8") as f:
        return json.load(f)

chars = load_srr("characters.json")
trees = load_srr("character_skill_trees.json")
promo = load_srr("character_promotions.json")

# 属性类型 → 中文
PROP_CN = {
    "MaxHP": "生命值", "HPAddedRatio": "生命值",
    "Attack": "攻击力", "ATKAddedRatio": "攻击力", "AttackAddedRatio": "攻击力",
    "Defence": "防御力", "DEFAddedRatio": "防御力", "DefenceAddedRatio": "防御力",
    "Speed": "速度", "SpeedDelta": "速度",
    "CriticalChanceBase": "暴击率",
    "CriticalDamageBase": "暴击伤害",
    "BreakDamageAddedRatioBase": "击破特攻",
    "HealRatioBase": "治疗量加成",
    "EnergyRecovery": "能量恢复效率",
    "StatusProbabilityBase": "效果命中",
    "StatusResistanceBase": "效果抵抗",
    "PhysicalAddedRatio": "物理属性伤害提高",
    "FireAddedRatio": "火属性伤害提高",
    "IceAddedRatio": "冰属性伤害提高",
    "ThunderAddedRatio": "雷属性伤害提高",
    "WindAddedRatio": "风属性伤害提高",
    "QuantumAddedRatio": "量子属性伤害提高",
    "ImaginaryAddedRatio": "虚数属性伤害提高",
    "SPRatioBase": "能量恢复效率",
    "BaseHP": "生命值", "BaseAttack": "攻击力", "BaseDefence": "防御力",
    "ElationDamageAddedRatioBase": "欢愉度",
    "HPDelta": "生命值", "ATKDelta": "攻击力", "DEFDelta": "防御力",
    "CriticalChanceDelta": "暴击率", "CriticalDamageDelta": "暴击伤害",
    "BreakDamageAddedRatioDelta": "击破特攻",
    "StatusProbabilityDelta": "效果命中", "StatusResistanceDelta": "效果抵抗",
    "EnergyRecoveryDelta": "能量恢复效率",
    "PhysicalAddedRatioDelta": "物理属性伤害提高", "FireAddedRatioDelta": "火属性伤害提高",
    "IceAddedRatioDelta": "冰属性伤害提高", "ThunderAddedRatioDelta": "雷属性伤害提高",
    "WindAddedRatioDelta": "风属性伤害提高", "QuantumAddedRatioDelta": "量子属性伤害提高",
    "ImaginaryAddedRatioDelta": "虚数属性伤害提高",
    "HPDelta": "生命值", "AttackDelta": "攻击力", "DefenceDelta": "防御力",
    "HealRatioBaseDelta": "治疗量加成",
}

# ---------- 1. 扫描用户角色文件 ----------
def parse_char_files():
    """解析所有角色 .md 文件，返回 {实体ID: {name, file, base_attrs, total_bonus}}"""
    result = {}
    for fp in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
        fn = os.path.basename(fp)
        if fn in ("角色.md",) or re.match(r"^(丰饶|同谐|存护|巡猎|智识|毁灭|虚无|记忆|欢愉)(\.md|_五星\.md|_四星\.md|_三星\.md)$", fn):
            continue  # 跳过索引文件
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        m = re.search(r">\s*实体ID[：:]\s*(\d+)", text)
        if not m:
            result.setdefault("__NOID__", []).append(fp)
            continue
        cid = m.group(1)
        base = parse_base_attrs(text)
        bonus = parse_total_bonus(text)
        result[cid] = {
            "file": fp.replace(HSR + "\\", ""),
            "base": base,
            "bonus": bonus,
        }
    return result

def parse_base_attrs(text):
    """解析 ## 基础属性（Lv.80） 表格"""
    m = re.search(r"##\s*基础属性.*?\n(.*?)(?=\n## |\Z)", text, re.S)
    if not m:
        return None
    rows = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and not cells[0].startswith("属性"):
            rows[cells[0]] = cells[1]
    return rows

def parse_total_bonus(text):
    """解析 ## 总属性加成 表格"""
    m = re.search(r"##\s*总属性加成.*?\n(.*?)(?=\n## |\Z)", text, re.S)
    if not m:
        return None
    rows = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and not cells[0].startswith("属性"):
            rows[cells[0]] = cells[1]
    return rows

# ---------- 2. StarRailRes 计算 ----------
def srr_lv80_base(cid):
    """计算 Lv.80 基础属性（晋阶6 base + step*79）"""
    p = promo.get(cid)
    if not p or not p.get("values"):
        return None
    vals = p["values"][-1]
    out = {}
    for k, v in vals.items():
        out[k] = v["base"] + v["step"] * 79
    return out

def srr_total_bonus(cid):
    """汇总 skill_trees 属性节点加成（按锚点去重，双形态镜像节点只算一次）"""
    if cid not in chars:
        return None
    agg = {}
    seen_anchor = set()
    for tid in chars[cid]["skill_trees"]:
        t = trees.get(tid, {})
        anchor = t.get("anchor", "")
        if anchor in seen_anchor:
            continue
        seen_anchor.add(anchor)
        for lv in t.get("levels", []):
            for pr in lv.get("properties", []):
                agg[pr["type"]] = agg.get(pr["type"], 0) + pr.get("value", 0)
    out = {}
    for k, v in agg.items():
        cn = PROP_CN.get(k, k)
        out[cn] = round(v, 6)
    return out

# ---------- 3. 对比 ----------
def fmt_pct(v):
    return f"{v*100:.1f}%" if v < 1 else f"{v}"

def compare():
    user = parse_char_files()
    report = []
    issues = []
    matched = 0
    missing_srr = []
    noid = user.pop("__NOID__", [])
    for cid, u in sorted(user.items(), key=lambda x: int(x[0])):
        if cid not in chars:
            missing_srr.append((cid, u["file"]))
            continue
        matched += 1
        name = chars[cid]["name"]
        # 基础属性
        sb = srr_lv80_base(cid)
        base_issues = []
        if sb and u["base"]:
            mapk = {"hp": "基础生命值", "atk": "基础攻击力", "def": "基础防御力", "spd": "基础速度", "taunt": "嘲讽"}
            for k, cn in mapk.items():
                if cn in u["base"]:
                    try:
                        uv = float(u["base"][cn].replace(",", "").replace("%", ""))
                    except ValueError:
                        continue
                    sv = round(sb.get(k, 0))
                    if abs(uv - sv) > 1:
                        base_issues.append(f"  {cn}: 库={u['base'][cn]} vs SRR≈{sv}")
        # 总属性加成
        sb2 = srr_total_bonus(cid)
        bonus_issues = []
        if sb2 and u["bonus"]:
            # 库中有的每项
            for cn, uv_str in u["bonus"].items():
                try:
                    if uv_str.endswith("%"):
                        uv = float(uv_str.rstrip("%")) / 100
                    else:
                        uv = float(uv_str)
                except ValueError:
                    continue
                sv = sb2.get(cn)
                if sv is None:
                    bonus_issues.append(f"  库含SRR无: {cn}={uv_str}")
                else:
                    # 速度/数值型 vs 百分比型
                    if abs(uv - sv) > 0.005 and abs(uv - sv) > 0.5:
                        bonus_issues.append(f"  {cn}: 库={uv_str} vs SRR={fmt_pct(sv)}")
            # SRR 有而库没有的
            for cn, sv in sb2.items():
                if cn not in u["bonus"] and sv != 0:
                    bonus_issues.append(f"  SRR含库无: {cn}={fmt_pct(sv)}")
        if base_issues or bonus_issues:
            issues.append((cid, name, u["file"], base_issues, bonus_issues))
    # 写报告
    with open(r"G:/HSR/StarRailRes_data/validate_report.md", "w", encoding="utf-8") as f:
        f.write(f"# HSR 知识库 vs StarRailRes 校验报告\n\n")
        f.write(f"- 用户角色文件（含实体ID）: {matched + len(issues) + len(missing_srr)}\n")
        f.write(f"- StarRailRes 可匹配: {matched}\n")
        f.write(f"- 存在差异: {len(issues)}\n")
        f.write(f"- 无对应SRR数据: {len(missing_srr)}\n")
        f.write(f"- 无实体ID文件: {len(noid)}\n\n")
        if missing_srr:
            f.write("## 无对应 SRR 数据\n")
            for cid, fp in missing_srr:
                f.write(f"- ID {cid}: {fp}\n")
            f.write("\n")
        if noid:
            f.write("## 无实体ID（可能是索引文件）\n")
            for fp in noid:
                f.write(f"- {fp}\n")
            f.write("\n")
        f.write("## 差异明细\n")
        if not issues:
            f.write("（无差异）\n")
        for cid, name, fp, bi, bo in issues:
            f.write(f"\n### {name} (ID {cid}) — {fp}\n")
            if bi:
                f.write("基础属性差异：\n" + "\n".join(bi) + "\n")
            if bo:
                f.write("总属性加成差异：\n" + "\n".join(bo) + "\n")
    return {
        "matched": matched, "issues": issues,
        "missing": missing_srr, "noid": noid,
    }

if __name__ == "__main__":
    r = compare()
    print("matched:", r["matched"], "| issues:", len(r["issues"]), "| missing:", len(r["missing"]), "| noid:", len(r["noid"]))
    for cid, name, fp, bi, bo in sorted(r["issues"], key=lambda x: int(x[0])):
        print(f"[{cid}] {name} ({fp})")
        for x in bi: print("   ", x)
        for x in bo: print("   ", x)
