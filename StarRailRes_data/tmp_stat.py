# -*- coding: utf-8 -*-
import json, math
SRR = r'G:/HSR/StarRailRes_repo/index_new/cn'
promo = json.load(open(SRR + '/character_promotions.json', encoding='utf-8'))
vals = promo['1307']['values']
last = vals[-1]
for kk in ['hp', 'atk', 'def', 'spd']:
    v = last[kk]
    b = v['base']
    print(f"{kk}: base={b} -> floor={math.floor(b)} round={round(b)}")
