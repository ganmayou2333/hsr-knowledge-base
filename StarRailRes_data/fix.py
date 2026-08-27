# -*- coding: utf-8 -*-
"""按校验结论修正 11 个角色文件的「基础属性」与「总属性加成」"""
import re, os

HSR = r"G:/HSR"

# 规则定义
EDITS = {
    # 三月七：基础攻击力/嘲讽 修正；总属性加成 删"生命值"、防御32.5%→22.5%
    "1001": {
        "file": "character/存护/三月七_冰_四星.md",
        "base": {"基础攻击力": "512", "嘲讽": "150"},
        "bonus_del": ["生命值"],
        "bonus_map": {"防御力": {"32.5%": "22.5%"}},
    },
    # 瓦尔特：效果命中→攻击力
    "1004": {
        "file": "character/虚无/瓦尔特_虚数_五星.md",
        "bonus_rename": {"效果命中": "攻击力"},
    },
    # 飞霄：删欢愉度、速度
    "1220": {
        "file": "character/巡猎/飞霄_风_五星.md",
        "bonus_del": ["欢愉度", "速度"],
    },
    # 忘归人：删"生命"重复行
    "1225": {
        "file": "character/虚无/忘归人_火_五星.md",
        "bonus_del": ["生命"],
    },
    # 万敌：删"生命值上限"重复行
    "1404": {
        "file": "character/毁灭/万敌_虚数_五星.md",
        "bonus_del": ["生命值上限"],
    },
    # 那刻夏：删"生命值上限"重复行
    "1405": {
        "file": "character/智识/那刻夏_风_五星.md",
        "bonus_del": ["生命值上限"],
    },
    # 缺失行补充
    "1321": {"file": "character/虚无/大丽花_火_五星.md", "bonus_add": [("速度", "5")]},
    "1408": {"file": "character/毁灭/白厄_物理_五星.md", "bonus_add": [("速度", "5")]},
    "1410": {"file": "character/虚无/海瑟音_物理_五星.md", "bonus_add": [("速度", "14")]},
    "1502": {"file": "character/欢愉/爻光_物理_五星.md", "bonus_add": [("速度", "9")]},
    "1513": {"file": "character/欢愉/砂金•戏浪_量子_五星.md", "bonus_add": [("速度", "9")]},
}

def parse_table_rows(text, section_re):
    """定位 section 下的表格，返回 (起始行, 结束行, 数据行列表)"""
    m = re.search(section_re, text, re.S)
    if not m:
        return None
    body = m.group(1)
    lines = body.splitlines()
    data_rows = []
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and not cells[0].startswith("属性") and not set(cells[0]) <= set("-:"):
                data_rows.append((i, cells))
    return (m.start(1), m.end(1), data_rows)

def apply_edits(cid, spec):
    fp = os.path.join(HSR, spec["file"])
    with open(fp, encoding="utf-8") as f:
        text = f.read()
    log = []

    # 1) 基础属性修正
    if "base" in spec:
        m = re.search(r"##\s*基础属性.*?\n(.*?)(?=\n## |\Z)", text, re.S)
        if m:
            body = m.group(1)
            lines = body.splitlines()
            new_lines = []
            for line in lines:
                if line.strip().startswith("|"):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    if len(cells) >= 2 and cells[0] in spec["base"]:
                        old_v = cells[1]
                        new_v = spec["base"][cells[0]]
                        if old_v != new_v:
                            log.append(f"  基础属性 {cells[0]}: {old_v} -> {new_v}")
                            cells[1] = new_v
                            line = "| " + " | ".join(cells) + " |"
                new_lines.append(line)
            text = text[:m.start(1)] + "\n".join(new_lines) + text[m.end(1):]

    # 2) 总属性加成
    m = re.search(r"##\s*总属性加成.*?\n(.*?)(?=\n## |\Z)", text, re.S)
    if m:
        body = m.group(1)
        lines = body.splitlines()
        new_lines = []
        added = set()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if len(cells) >= 2 and not cells[0].startswith("属性") and not set(cells[0]) <= set("-:"):
                    key = cells[0]
                    # 删除
                    if "bonus_del" in spec and key in spec["bonus_del"]:
                        log.append(f"  删除行: {key}={cells[1]}")
                        continue
                    # 重命名
                    if "bonus_rename" in spec and key in spec["bonus_rename"]:
                        log.append(f"  重命名: {key} -> {spec['bonus_rename'][key]} (值 {cells[1]})")
                        cells[0] = spec["bonus_rename"][key]
                        line = "| " + " | ".join(cells) + " |"
                    # 值替换
                    if "bonus_map" in spec and key in spec["bonus_map"]:
                        if cells[1] in spec["bonus_map"][key]:
                            old_v = cells[1]
                            cells[1] = spec["bonus_map"][key][cells[1]]
                            log.append(f"  修改: {key}: {old_v} -> {cells[1]}")
                            line = "| " + " | ".join(cells) + " |"
                    added.add(key)
            new_lines.append(line)
        # 追加缺失行
        if "bonus_add" in spec:
            for k, v in spec["bonus_add"]:
                if k not in added:
                    new_lines.append(f"| {k} | {v} |")
                    log.append(f"  追加行: {k}={v}")
        text = text[:m.start(1)] + "\n".join(new_lines) + text[m.end(1):]

    with open(fp, "w", encoding="utf-8") as f:
        f.write(text)
    return log

for cid, spec in EDITS.items():
    print(f"[{cid}] {spec['file']}")
    logs = apply_edits(cid, spec)
    for l in logs:
        print(l)
    if not logs:
        print("  (无改动)")
