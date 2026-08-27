# -*- coding: utf-8 -*-
"""匹配 7483 奇物星级到本地奇物文件"""
import os, json, re, glob


def norm(s):
    s = s.strip()
    s = s.replace('「', '').replace('」', '').replace('《', '').replace('》', '').replace('“', '').replace('”', '')
    s = re.sub(r'（.*?）', '', s)  # 去括号内容
    s = re.sub(r'\(.*?\)', '', s)
    return s


# 读取提取的星级
star = json.load(open('StarRailRes_data/curio_star_7483.json', encoding='utf-8'))
star_map = {}  # 归一化名称 -> 星级
for group, names in star.items():
    for n in names:
        star_map[norm(n)] = group[0] + '星'

# 名称别名（米游社 vs SRR 翻译差异）
ALIAS = {'香涎干酪': '香涎奶酪'}

# 读取本地奇物文件
files = sorted(f for f in glob.glob('simulated/奇物/*.md') if not f.endswith('奇物.md'))
matched, unmatched = [], []
for f in files:
    txt = open(f, encoding='utf-8').read()
    # 提取名称（标题或基本信息）
    m = re.search(r'^# (.+)$', txt, re.M)
    name = m.group(1).strip() if m else os.path.basename(f)[:-3]
    key = norm(name)
    if key in ALIAS:
        key = ALIAS[key]
    if key in star_map:
        matched.append((os.path.basename(f), name, star_map[key]))
    else:
        unmatched.append((os.path.basename(f), name))

print('=== 匹配成功:', len(matched), '===')
for f, name, s in matched:
    print('  %s  (%s)  -> %s' % (f, name, s))
print()
print('=== 未匹配:', len(unmatched), '===')
for f, name in unmatched:
    print('  %s  (%s)' % (f, name))
print()
print('=== 7483 有但本地无的奇物名 ===')
local_names = {norm(f[:-3]) for f in glob.glob('simulated/奇物/*.md')}
extra = [n for n in star_map if n not in local_names]
print(len(extra), '个:')
print('  ' + '、'.join(extra[:80]))
