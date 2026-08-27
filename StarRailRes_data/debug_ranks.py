# -*- coding: utf-8 -*-
import json
SRR = r'G:/HSR/StarRailRes_repo/index_new/cn'
ranks = json.load(open(SRR + '/character_ranks.json', encoding='utf-8'))
chars = json.load(open(SRR + '/characters.json', encoding='utf-8'))
for cid in ['1001', '1212']:
    print('===', cid, chars[cid]['name'])
    for i, rid in enumerate(chars[cid]['ranks']):
        r = ranks.get(rid, {})
        print(f"  E{i+1} [{rid}] {r.get('name')}: {r.get('desc')[:70]}")
