# -*- coding: utf-8 -*-
import json
b = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_blessings.json', encoding='utf-8'))
for t in ['回响构音', '回响交错', '体验']:
    print('=== %s ===' % t)
    for i, v in b.items():
        if v.get('name', '').startswith(t):
            print('  %s | %s' % (i, v['name']))
