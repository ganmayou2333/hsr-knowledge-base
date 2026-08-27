# -*- coding: utf-8 -*-
"""提取镜流(1212)的完整角色档案 v2，含行迹属性与晋阶成长数值"""
import json, os

base = r"G:/HSR/StarRailRes_repo/index_new/cn"
char_id = "1212"

def load(name):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return json.load(f)

chars = load("characters.json")
ranks = load("character_ranks.json")
skills = load("character_skills.json")
trees = load("character_skill_trees.json")
promo = load("character_promotions.json")

out = []
c = chars[char_id]
out.append("=" * 56)
out.append(f"【角色档案】{c['name']}  (ID: {c['id']}, tag: {c['tag']})")
out.append(f"稀有度: {c['rarity']}星 | 命途: {c['path']} | 属性: {c['element']} | 能量上限: {c['max_sp']}")
out.append(f"图标: {c['icon']}")
out.append(f"预览图: {c['preview']}")
out.append(f"立绘: {c['portrait']}")
out.append("")

out.append("-" * 56)
out.append("【基础成长数值 (character_promotions.json)】")
p = promo[char_id]
for i, v in enumerate(p["values"]):
    items = ", ".join(f"{k} {v[k]['base']}+{v[k]['step']}/级" for k in v)
    out.append(f"  晋阶{i}: {items}")
out.append("")

out.append("-" * 56)
out.append("【星魂 (character_ranks.json)】")
for rid in c["ranks"]:
    r = ranks.get(rid, {})
    out.append(f"[{rid}] {r.get('name','')}")
    out.append(f"  {r.get('desc','')}")
out.append("")

out.append("-" * 56)
out.append("【技能 (character_skills.json)】")
for sid in c["skills"]:
    s = skills.get(sid, {})
    out.append(f"[{sid}] {s.get('name','')} | 类型: {s.get('type','')} | 最大等级: {s.get('max_level','')}")
    out.append(f"  {s.get('desc','')}")
out.append("")

out.append("-" * 56)
out.append("【行迹 (character_skill_trees.json)】")
for tid in c["skill_trees"]:
    t = trees.get(tid, {})
    desc = t.get("desc", "") or ""
    props = []
    for lv in t.get("levels", []):
        for pr in lv.get("properties", []):
            props.append(pr.get("type", "") + "=" + str(pr.get("value", "")))
    propstr = (" | 属性加成: " + ", ".join(props)) if props else ""
    lvskills = [ls.get("id", "") for ls in t.get("level_up_skills", [])]
    lvstr = (" | 升级技能: " + ", ".join(lvskills)) if lvskills else ""
    out.append(f"[{tid}] {t.get('name','')} (锚点{t.get('anchor','')}, 最大等级{t.get('max_level','')}){lvstr}{propstr}")
    if desc:
        out.append(f"  {desc}")
out.append("")

with open(r"G:/HSR/StarRailRes_data/jingliu_profile_full.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("written lines:", len(out))
