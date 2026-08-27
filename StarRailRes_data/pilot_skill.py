# -*- coding: utf-8 -*-
"""试点：镜流战技文本 vs SRR 技能参数"""
import json, re

SRR = r"G:/HSR/StarRailRes_repo/index_new/cn"
skills = json.load(open(SRR + "/character_skills.json", encoding="utf-8"))
chars = json.load(open(SRR + "/characters.json", encoding="utf-8"))

# 镜流技能（双形态）
for sid in ['121201', '121202', '121203', '121204', '1121201', '1121202', '1121203', '1121204']:
    s = skills.get(sid, {})
    params = s.get('params') or []
    l1 = params[0] if params else None
    print(f"[{sid}] {s.get('name','')} ({s.get('type','')})")
    print(f"  desc: {s.get('desc','')}")
    print(f"  1级params: {l1}")
    print()
