# -*- coding: utf-8 -*-
"""输出11个差异角色的双方明细，用于甄别真/伪差异"""
import json, re, glob, os

HSR = r'G:/HSR'
SRR = r'G:/HSR/StarRailRes_repo/index_new/cn'
chars = json.load(open(SRR + '/characters.json', encoding='utf-8'))
trees = json.load(open(SRR + '/character_skill_trees.json', encoding='utf-8'))

PROP = {'AttackAddedRatio': '攻击力', 'DefenceAddedRatio': '防御力', 'HPAddedRatio': '生命值',
        'SpeedDelta': '速度', 'CriticalDamageBase': '暴击伤害', 'CriticalChanceBase': '暴击率',
        'BreakDamageAddedRatioBase': '击破特攻', 'HealRatioBase': '治疗量加成',
        'EnergyRecovery': '能量恢复效率', 'StatusProbabilityBase': '效果命中',
        'StatusResistanceBase': '效果抵抗', 'PhysicalAddedRatio': '物理属性伤害提高',
        'FireAddedRatio': '火属性伤害提高', 'IceAddedRatio': '冰属性伤害提高',
        'ThunderAddedRatio': '雷属性伤害提高', 'WindAddedRatio': '风属性伤害提高',
        'QuantumAddedRatio': '量子属性伤害提高', 'ImaginaryAddedRatio': '虚数属性伤害提高',
        'ElationDamageAddedRatioBase': '欢愉度'}

targets = ['1001', '1004', '1220', '1225', '1321', '1404', '1405', '1408', '1410', '1502', '1513']

# 建立 实体ID -> 文件 映射
id2file = {}
for fp in glob.glob(os.path.join(HSR, 'character', '*', '*.md')):
    t = open(fp, encoding='utf-8').read()
    m = re.search(r'>\s*实体ID[：:]\s*(\d+)', t)
    if m:
        id2file[m.group(1)] = fp

out = []
for cid in targets:
    name = chars[cid]['name']
    out.append('=' * 60)
    out.append(f'[{cid}] {name} ({chars[cid]["path"]} {chars[cid]["element"]} {chars[cid]["rarity"]}星)')
    # SRR 属性节点明细（去重）
    seen = set()
    nodes = []
    for tid in chars[cid]['skill_trees']:
        t = trees.get(tid, {})
        anchor = t.get('anchor', '')
        if anchor in seen:
            continue
        seen.add(anchor)
        for lv in t.get('levels', []):
            for pr in lv.get('properties', []):
                nodes.append(f"{anchor}:{PROP.get(pr['type'], pr['type'])}={pr['value']}")
    out.append('  SRR属性节点: ' + ('; '.join(nodes) if nodes else '(无)'))
    fp = id2file.get(cid)
    if not fp:
        out.append('  库文件: 未找到')
        continue
    out.append('  库文件: ' + fp.replace(HSR + os.sep, ''))
    t = open(fp, encoding='utf-8').read()
    bm = re.search(r'##\s*基础属性.*?\n(.*?)(?=\n## |\Z)', t, re.S)
    if bm:
        out.append('  库-基础属性:')
        for line in bm.group(1).splitlines():
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(c) >= 2 and not c[0].startswith('属性'):
                out.append('    ' + c[0] + ' = ' + c[1])
    tm = re.search(r'##\s*总属性加成.*?\n(.*?)(?=\n## |\Z)', t, re.S)
    if tm:
        out.append('  库-总属性加成:')
        for line in tm.group(1).splitlines():
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(c) >= 2 and not c[0].startswith('属性'):
                out.append('    ' + c[0] + ' = ' + c[1])

print('\n'.join(out))
