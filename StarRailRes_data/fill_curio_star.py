# -*- coding: utf-8 -*-
"""回填奇物星级：7483(差分宇宙·乐园漫记) + 游戏8差分宇宙页补充"""
import os, json, re, glob


def norm(s):
    s = s.strip().replace('「', '').replace('」', '').replace('《', '').replace('》', '')
    s = re.sub(r'（.*?）', '', s)
    return s


# 7483 星级
star7483 = json.load(open('StarRailRes_data/curio_star_7483.json', encoding='utf-8'))
# 游戏8 差分宇宙页补充（日文确认）
extra = {
    '万识囊': '1星', '塔拉毒火焰': '1星', '粉红冲撞': '1星', '虫网': '1星',
}
star_map = {}
for group, names in star7483.items():
    for n in names:
        star_map[norm(n)] = group[0] + '星'
for k, v in extra.items():
    star_map[norm(k)] = v

ALIAS = {'香涎干酪': '香涎奶酪'}

changed = []
unmatched = []
for f in glob.glob('simulated/奇物/*.md'):
    if f.endswith('奇物.md'):
        continue
    name = os.path.basename(f)[:-3]
    key = norm(name)
    if key in ALIAS:
        key = ALIAS[key]
    star = star_map.get(key)
    if star is None:
        unmatched.append(name)
        continue
    txt = open(f, encoding='utf-8').read()
    if '| 星级 | 待补充 |' in txt:
        txt = txt.replace('| 星级 | 待补充 |', '| 星级 | %s |' % star)
        open(f, 'w', encoding='utf-8').write(txt)
        changed.append((name, star))
    else:
        # 已有星级则跳过
        m = re.search(r'\| 星级 \| ([^|]+) \|', txt)
        print('  已存在星级:', name, '->', m.group(1) if m else '?')

print('=== 已回填:', len(changed), '===')
for n, s in changed:
    print('  %s -> %s' % (n, s))
print()
print('=== 未匹配(需人工确认):', len(unmatched), '===')
for n in unmatched:
    print('  ', n)
