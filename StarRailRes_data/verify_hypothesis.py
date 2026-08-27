# -*- coding: utf-8 -*-
"""验证假设：用户库技能材料 = SRR正确值 + 普攻材料×2（普攻被算3遍）"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
items = json.load(open(SRR + "/items.json", encoding="utf-8"))
trees = json.load(open(SRR + "/character_skill_trees.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))

def skill_mats(cid, anchors):
    """按锚点集合汇总材料 {中文名: 数量}"""
    agg = {}
    seen = set()
    for tid in chars[cid]["skill_trees"]:
        t = trees.get(tid, {})
        a = t.get("anchor")
        if a not in anchors or a in seen:
            continue
        seen.add(a)
        for lv in t.get("levels", []):
            for m in lv.get("materials", []):
                name = items.get(m["id"], {}).get("name", m["id"])
                agg[name] = agg.get(name, 0) + m["num"]
    return agg

def total_credit(d):
    return d.get("信用点", 0)

targets = ['1402', '1407', '1409', '1413', '1415', '1501', '1502', '1505', '1506', '1512', '1513', '8007', '8009']
for cid in targets:
    all4 = skill_mats(cid, {"Point01", "Point02", "Point03", "Point04"})
    p_skill = skill_mats(cid, {"Point01"})  # 只有普攻
    others = {k: all4.get(k, 0) - p_skill.get(k, 0) for k in all4}
    # 用户库数值
    user = {}
    for fp in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
        t = open(fp, encoding="utf-8").read()
        if re.search(r">\s*实体ID[：:]\s*" + cid, t):
            m = re.search(r"##\s*技能材料[^\n]*\n(.*?)(?=\n## |\Z)", t, re.S)
            if m:
                for line in m.group(1).splitlines():
                    line = line.strip()
                    if not line.startswith("|"):
                        continue
                    le = line.replace(r"\|", "\x00")
                    cells = [c.strip() for c in le.strip("|").split("|")]
                    if len(cells) < 2:
                        continue
                    k = cells[0].replace("\x00", "|")
                    v = cells[1].replace("\x00", "|")
                    m2 = re.search(r"\[\[([^\]]*?)\|([^\]]+)\]\]", k)
                    if m2:
                        k = m2.group(2).strip()
                    elif k.startswith("[["):
                        k = re.sub(r"\[\[|\]\]", "", k).split("/")[-1].strip()
                    if k != "材料" and not set(k) <= set("-:"):
                        user[k] = int(re.sub(r"[^\d]", "", v or "0"))
            break
    # 假设：user = all4 + p_skill*2
    pred = {k: all4.get(k, 0) + 2 * p_skill.get(k, 0) for k in set(all4) | set(p_skill)}
    match = all(user.get(k, 0) == pred.get(k, 0) for k in set(user) | set(pred))
    p_credit = total_credit(p_skill)
    print(f"[{cid}] 普攻信用点={p_credit} 假设匹配={match}")
    if not match:
        # 打印明细
        for k in sorted(set(user) | set(pred)):
            uv, pv = user.get(k, 0), pred.get(k, 0)
            if uv != pv:
                print(f"     {k}: 库={uv} 假设={pv} SRR正确={all4.get(k,0)}")
