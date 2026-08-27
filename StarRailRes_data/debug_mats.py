# -*- coding: utf-8 -*-
import json
SRR = r'G:/HSR/StarRailRes_repo/index_new/cn'
trees = json.load(open(SRR + '/character_skill_trees.json', encoding='utf-8'))
items = json.load(open(SRR + '/items.json', encoding='utf-8'))

for tid, label in [('1402002', '阿格莱雅战技(1402002)'), ('1212002', '镜流战技(1212002)'),
                   ('1402001', '阿格莱雅普攻(1402001)'), ('1212001', '镜流普攻(1212001)')]:
    t = trees.get(tid, {})
    print(label)
    for lv in t.get('levels', []):
        mats = lv.get('materials', [])
        if mats:
            s = ' + '.join(f"{items.get(m['id'], {}).get('name', m['id'])}x{m['num']}" for m in mats)
            print(f"  promo{lv.get('promotion')}: {s}")
    print()
