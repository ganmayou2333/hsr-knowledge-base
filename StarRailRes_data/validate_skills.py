# -*- coding: utf-8 -*-
"""校验战技倍率：用户战技章节效果文本百分数 vs SRR 对应技能满级参数"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
skills = json.load(open(SRR + "/character_skills.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))

# type → 用户子标题关键词
TYPE_HEAD = {"Normal": "普攻", "BPSkill": "战技", "Ultra": "终结技", "Talent": "天赋", "Maze": "秘技"}
# type → skill_trees 锚点（用于取实际等级上限）
TYPE_ANCHOR = {"Normal": "Point01", "BPSkill": "Point02", "Ultra": "Point03", "Talent": "Point04", "Maze": "Point08"}

trees = json.load(open(SRR + "/character_skill_trees.json", encoding="utf-8"))

def actual_max_level(cid, stype):
    """从 skill_trees 取该类型技能的实际等级上限（普攻6、其他10、秘技1）"""
    anchor = TYPE_ANCHOR[stype]
    for tid in chars.get(cid, {}).get("skill_trees", []):
        t = trees.get(tid, {})
        if t.get("anchor") == anchor:
            return t.get("max_level") or 1
    return None

def get_user_effect(text, head):
    """解析用户 ### {head}：xxx 子章节的 - **效果** 行"""
    m = re.search(r"###\s*" + head + r"[：:][^\n]*\n(.*?)(?=\n### |\n## |\Z)", text, re.S)
    if not m:
        return None
    em = re.search(r"\*\*效果\*\*[：:]\s*([^\n]+)", m.group(1))
    if em:
        return em.group(1).strip()
    return None

def extract_pcts(s):
    """提取文本中所有 X% 数字（保留两位小数）"""
    return [round(float(x), 2) for x in re.findall(r"([\d.]+)%", s or "")]

def srr_full_params(cid, stype):
    """返回该角色某类型技能（含多形态）实际等级上限 params 的百分数集合"""
    res = []
    max_lv = actual_max_level(cid, stype)
    if max_lv is None:
        return res
    for sid in chars.get(cid, {}).get("skills", []):
        s = skills.get(sid, {})
        if s.get("type") != stype:
            continue
        params = s.get("params") or []
        if not params:
            continue
        idx = min(max_lv - 1, len(params) - 1)
        full = params[idx]
        res.append([round(v * 100, 2) for v in full])
    return res

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
    checked += 1
    diffs = []
    for stype, head in TYPE_HEAD.items():
        ue = get_user_effect(text, head)
        if ue is None:
            continue
        upcts = extract_pcts(ue)
        if not upcts:
            continue
        srr_sets = srr_full_params(cid, stype)
        if not srr_sets:
            diffs.append(f"  {head}: SRR 无对应技能")
            continue
        for up in upcts:
            if not any(any(abs(up - sp) <= 0.51 for sp in sps) for sps in srr_sets):
                diffs.append(f"  {head} 倍率 {up}%: 用户文本中找不到于SRR满级params {srr_sets}")
    if diffs:
        issues += 1
        report.append(f"[{cid}] {os.path.basename(fp)}")
        report.extend(diffs)

print(f"已校验 {checked} 角色，发现差异 {issues}")
print("\n".join(report) if report else "（无差异）")
with open(r"G:/HSR/StarRailRes_data/validate_skill_value.md", "w", encoding="utf-8") as f:
    f.write("# 战技倍率校验报告\n\n")
    f.write(f"已校验 {checked} 角色，发现差异 {issues}\n\n")
    f.write("\n".join(report) if report else "（无差异）")
