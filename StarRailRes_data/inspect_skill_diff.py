# -*- coding: utf-8 -*-
"""输出9个战技倍率差异角色的用户文本与SRR参数对照"""
import json, os, re, glob

HSR = r"G:/HSR"
SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
skills = json.load(open(SRR + "/character_skills.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))
trees = json.load(open(SRR + "/character_skill_trees.json", encoding="utf-8"))

TYPE_HEAD = {"Normal": "普攻", "BPSkill": "战技", "Ultra": "终结技", "Talent": "天赋", "Maze": "秘技"}
TYPE_ANCHOR = {"Normal": "Point01", "BPSkill": "Point02", "Ultra": "Point03", "Talent": "Point04", "Maze": "Point08"}

targets = ['1001', '1107', '1310', '1404', '1406', '1407', '1408', '1506', '8007']

for cid in targets:
    fp = None
    for f in glob.glob(os.path.join(HSR, "character", "*", "*.md")):
        t = open(f, encoding="utf-8").read()
        if re.search(r">\s*实体ID[：:]\s*" + cid, t):
            fp = f
            text = t
            break
    if not fp:
        continue
    print("=" * 70)
    print(f"[{cid}] {os.path.basename(fp)}")
    # 用户战技章节
    vm = re.search(r"##\s*战技(.*?)(?=\n## |\Z)", text, re.S)
    if not vm:
        continue
    # 4个技能子章节
    for stype, head in TYPE_HEAD.items():
        m = re.search(r"###\s*" + head + r"[：:]([^\n]*)\n(.*?)(?=\n### |\n## |\Z)", vm.group(1), re.S)
        if not m:
            continue
        em = re.search(r"\*\*效果\*\*[：:]\s*([^\n]+)", m.group(2))
        ue = em.group(1).strip() if em else "(无效果行)"
        # SRR
        max_lv = None
        for tid in chars.get(cid, {}).get("skill_trees", []):
            t = trees.get(tid, {})
            if t.get("anchor") == TYPE_ANCHOR[stype]:
                max_lv = t.get("max_level")
                break
        srr_info = []
        for sid in chars.get(cid, {}).get("skills", []):
            s = skills.get(sid, {})
            if s.get("type") != stype:
                continue
            params = s.get("params") or []
            if params and max_lv:
                idx = min(max_lv - 1, len(params) - 1)
                srr_info.append(f"{sid}:{s.get('name','')} {max_lv}级={[round(v*100,2) for v in params[idx]]}")
        print(f"\n  【{head}】{m.group(1).strip()}")
        print(f"    用户: {ue}")
        for si in srr_info:
            print(f"    SRR: {si}")
