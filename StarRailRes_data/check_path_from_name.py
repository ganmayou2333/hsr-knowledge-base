# -*- coding: utf-8 -*-
"""检查祝福名称中可提取命途的数量与结构"""
import json
from collections import defaultdict

b = json.load(open('G:/HSR/StarRailRes_repo/index_new/cn/simulated_blessings.json', encoding='utf-8'))
paths = ['存护', '记忆', '虚无', '丰饶', '毁灭', '巡猎', '欢愉', '智识', '繁育']

# 名称含「命途名」的祝福
cnt = 0
by_type = defaultdict(list)
for i, v in b.items():
    n = v.get('name', '')
    for p in paths:
        if p in n:
            cnt += 1
            # 判断名称类型
            if n.startswith('命途回响'):
                t = '命途回响'
            elif n.startswith('回响构音'):
                t = '回响构音'
            elif n.startswith('回响交错'):
                t = '回响交错'
            elif n.startswith('体验'):
                t = '体验'
            else:
                t = '其他'
            by_type[t].append((i, n))
            break

print('名称含命途词: %d/%d' % (cnt, len(b)))
for t in ['命途回响', '回响构音', '回响交错', '体验', '其他']:
    items = by_type.get(t, [])
    print('\n[%s] %d 条' % (t, len(items)))
    for i, n in items[:5]:
        print('  %s: %s' % (i, n))

# 特殊类型祝福总数（不含命途词的）
print('\n=== 特殊类型但名称不含命途词 ===')
for t in ['命途回响', '回响构音', '回响交错', '体验']:
    items = [x for x in by_type.get(t, [])]
    total = sum(1 for v in b.values() if v.get('name','').startswith(t))
    print('%s: 总数%d, 含命途词%d, 缺命途%d' % (t, total, len(items), total - len(items)))
    for i, n in [x for x in by_type.get(t, [])]:
        pass
