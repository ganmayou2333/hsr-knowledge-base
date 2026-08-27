# -*- coding: utf-8 -*-
"""生成模拟宇宙知识库 v2：祝福/奇物/事件/区块（含同名合并）"""
import os, re, json
from collections import defaultdict

CN = 'G:/HSR/StarRailRes_repo/index_new/cn'
OUT = 'G:/HSR/simulated'
SRC = 'https://github.com/Mar-7th/StarRailRes（index_new/cn/'
VER = '4.5'

def load(fn):
    return json.load(open(os.path.join(CN, fn), encoding='utf-8'))

def clean_name(name):
    if not name:
        return '未命名'
    s = name.replace('<', '《').replace('>', '》')
    for ch in ':"/\\|?*':
        s = s.replace(ch, ' ')
    return re.sub(r'\s+', ' ', s).strip()

def header(src_file, eids, merge=False):
    eid_str = ' / '.join(eids)
    typ = '（同名合并）' if merge else ''
    return (f'> 数据来源：{SRC}{src_file}）\n'
            f'> 数据版本：{VER}\n'
            f'> 实体ID：{eid_str}\n\n---\n')

def table(d):
    rows = ['| 属性 | 值 |', '|---|---|']
    for k, v in d.items():
        rows.append(f'| {k} | {v} |')
    return '\n'.join(rows) + '\n'

def basic_table(name, kind, extra_rows, merge=False):
    d = {'名称': name, '类型': kind + ('（同名合并）' if merge else '')}
    d.update(extra_rows)
    return table(d)

def special_type(name):
    n = name.strip()
    if n.startswith('命途回响'):
        return '命途回响'
    if n.startswith('回响构音'):
        return '回响构音'
    if n.startswith('回响交错'):
        return '回响交错'
    if n.startswith('体验'):
        return '体验'
    return '普通祝福'

# ID 段 → 命途（依据命途回响锚点推导，6120-6128 经典模拟宇宙、6150-6158 黄金与机械）
ID_PATH = {
    '6120': '存护', '6121': '记忆', '6122': '虚无', '6123': '丰饶',
    '6124': '巡猎', '6125': '毁灭', '6126': '欢愉', '6127': '繁育', '6128': '智识',
    '6150': '存护', '6151': '记忆', '6152': '虚无', '6153': '丰饶',
    '6154': '巡猎', '6155': '毁灭', '6156': '欢愉', '6157': '繁育', '6158': '智识',
}

def path_from_id(eid, name=''):
    # 1) 名称含「命途名」（命途回响等）
    m = re.search(r'「(存护|记忆|虚无|丰饶|毁灭|巡猎|欢愉|智识|繁育)」', name)
    if m:
        return m.group(1)
    # 2) ID 段推断
    seg = eid[:4]
    if seg in ID_PATH:
        return ID_PATH[seg]
    return None

# 米游社 WIKI 767 命途回填（sid -> path，含双命途交错）
ENRICH = json.load(open('G:/HSR/StarRailRes_data/enrich_612.json', encoding='utf-8'))

def resolve_path(ids, name):
    # 1) wiki 命途（同组全部一致才用）
    wset = {ENRICH[i]['path'] for i in ids if i in ENRICH}
    if len(wset) == 1:
        return wset.pop()
    # 2) 名称含「命途名」
    m = re.search(r'「(存护|记忆|虚无|丰饶|毁灭|巡猎|欢愉|智识|繁育)」', name)
    if m:
        return m.group(1)
    # 3) ID 段推断（同组全部一致才用）
    pset = {ID_PATH[i[:4]] for i in ids if i[:4] in ID_PATH}
    if len(pset) == 1:
        return pset.pop()
    return '待补充'

def group_by_name(data):
    g = defaultdict(list)
    for i, v in data.items():
        g[clean_name(v.get('name', ''))].append((i, v))
    return g

# ============ 1. 祝福 ============
bless_dir = os.path.join(OUT, '祝福')
os.makedirs(bless_dir, exist_ok=True)
bless_groups = group_by_name(load('simulated_blessings.json'))
bless_index = []
bless_special = defaultdict(list)

for fname, items in sorted(bless_groups.items()):
    name = items[0][1].get('name', '') or fname
    ids = [i for i, _ in items]
    sp = special_type(name)
    merged = len(items) > 1
    # 命途：wiki 优先，其次名称/ID 推断
    path_val = resolve_path(ids, name)
    if merged:
        rows = ['| 实体ID | 效果 |', '|---|---|']
        seen = set()
        for i, v in items:
            desc = (v.get('desc') or '').strip() or '-'
            if desc in seen:
                rows.append(f'| {i} | （与上行效果相同） |')
            else:
                rows.append(f'| {i} | {desc} |')
                seen.add(desc)
        eff_section = '## 说明\n\n> 该名称对应 %d 个不同实体ID，效果如下：\n\n%s' % (len(items), '\n'.join(rows))
    else:
        v = items[0][1]
        desc = (v.get('desc') or '').strip() or '-'
        enh = (v.get('enhanced_desc') or '').strip() or '-'
        eff_section = f'## 效果\n\n{desc}\n\n## 强化效果\n\n{enh}'
    content = f"""# {name}

{header('simulated_blessings.json', ids, merged)}

## 基本信息

{basic_table(name, '祝福', {'命途': path_val, '星级': '待补充', '特殊类型': sp}, merged)}

{eff_section}
"""
    with open(os.path.join(bless_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    bless_index.append((fname, name, path_val))
    bless_special[sp].append(fname)

# 祝福索引
lines = ['# 祝福', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '', '## 按命途', '']
by_path = defaultdict(list)
for fname, name, p in bless_index:
    by_path[p].append(fname)
for p in ['存护', '记忆', '虚无', '丰饶', '毁灭', '巡猎', '欢愉', '智识', '繁育', '待补充']:
    items = by_path.get(p, [])
    if items:
        lines.append(f'### {p}（{len(items)}）')
        lines.append('')
        for it in sorted(items):
            lines.append(f'- [[simulated/祝福/{it}|{it}]]')
        lines.append('')
lines.append('## 按特殊类型')
lines.append('')
for sp in ['命途回响', '回响构音', '回响交错', '体验', '普通祝福']:
    items = [n for n in bless_special.get(sp, [])]
    if items:
        lines.append(f'### {sp}（{len(items)}）')
        lines.append('')
        for it in sorted(items):
            lines.append(f'- [[simulated/祝福/{it}|{it}]]')
        lines.append('')
lines.append('## 全部祝福（%d）' % len(bless_index))
lines.append('')
lines.append('> 星级：待补充')
lines.append('')
for fname, name, _ in bless_index:
    lines.append(f'- [[simulated/祝福/{fname}|{name}]]')
open(os.path.join(bless_dir, '祝福.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 2. 奇物 ============
curio_dir = os.path.join(OUT, '奇物')
os.makedirs(curio_dir, exist_ok=True)
curio_groups = group_by_name(load('simulated_curios.json'))
curio_index = []

for fname, items in sorted(curio_groups.items()):
    name = items[0][1].get('name', '') or fname
    ids = [i for i, _ in items]
    merged = len(items) > 1
    if merged:
        rows = ['| 实体ID | 效果 |', '|---|---|']
        seen = set()
        for i, v in items:
            desc = (v.get('desc') or '').strip() or '-'
            if desc in seen:
                rows.append(f'| {i} | （与上行效果相同） |')
            else:
                rows.append(f'| {i} | {desc} |')
                seen.add(desc)
        eff_section = '## 说明\n\n> 该名称对应 %d 个不同实体ID，效果如下：\n\n%s' % (len(items), '\n'.join(rows))
        bg = (items[0][1].get('bg_desc') or '').strip() or '-'
        eff_section += f'\n\n## 背景故事\n\n{bg}'
    else:
        v = items[0][1]
        desc = (v.get('desc') or '').strip() or '-'
        bg = (v.get('bg_desc') or '').strip() or '-'
        eff_section = f'## 效果\n\n{desc}\n\n## 背景故事\n\n{bg}'
    content = f"""# {name}

{header('simulated_curios.json', ids, merged)}

## 基本信息

{basic_table(name, '奇物', {'星级': '待补充'}, merged)}

{eff_section}
"""
    with open(os.path.join(curio_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    curio_index.append((fname, name))

lines = ['# 奇物', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '', '## 全部奇物（%d）' % len(curio_index), '', '> 星级：待补充', '']
for fname, name in sorted(curio_index):
    lines.append(f'- [[simulated/奇物/{fname}|{name}]]')
open(os.path.join(curio_dir, '奇物.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 3. 事件 ============
ev_dir = os.path.join(OUT, '事件')
os.makedirs(ev_dir, exist_ok=True)
events = load('simulated_events.json')
ev_groups = group_by_name(events)
ev_index = []
img_count = defaultdict(int)
for v in events.values():
    img_count[v.get('image') or ''] += 1
shared_imgs = {k: v for k, v in img_count.items() if v > 1}

for fname, items in sorted(ev_groups.items()):
    name = items[0][1].get('name', '') or fname
    ids = [i for i, _ in items]
    merged = len(items) > 1
    types = sorted(set((v.get('type') or '-') for _, v in items))
    imgs = sorted(set((v.get('image') or '-') for _, v in items))
    img_str = '、'.join(f'`{x}`' for x in imgs) if imgs else '-'
    img_note = ''
    if merged:
        img_note = f'\n\n> 注：该事件有 {len(ids)} 个实体（不同难度/选项），合并记录。'
    # 图片共用标注
    shared_txt = []
    for im in imgs:
        if im in shared_imgs:
            shared_txt.append(f'`{im}` 与另外 {shared_imgs[im]-1} 个事件共用')
    img_note += ('\n\n> 图片共用：' + '；'.join(shared_txt)) if shared_txt else ''
    rows = ['| 实体ID | 属性 | 图片 |', '|---|---|---|']
    for i, v in items:
        rows.append(f'| {i} | {v.get("type") or "-"} | `{v.get("image") or "-"}` |')
    content = f"""# {name}

{header('simulated_events.json', ids, merged)}

## 基本信息

{basic_table(name, '事件', {'属性': ' / '.join(types), '图片': img_str}, merged)}

## 事件文本

待补充
{img_note}

## 实体记录

{chr(10).join(rows)}
"""
    with open(os.path.join(ev_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    ev_index.append((fname, name))

lines = ['# 事件', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '', '## 全部事件（%d）' % len(ev_index), '', '> 事件文本：待补充', '']
for fname, name in sorted(ev_index):
    lines.append(f'- [[simulated/事件/{fname}|{name}]]')
open(os.path.join(ev_dir, '事件.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 4. 区块 ============
blk_dir = os.path.join(OUT, '区块')
os.makedirs(blk_dir, exist_ok=True)
blk_groups = group_by_name(load('simulated_blocks.json'))
blk_index = []

for fname, items in sorted(blk_groups.items()):
    name = items[0][1].get('name', '') or fname
    ids = [i for i, _ in items]
    merged = len(items) > 1
    v = items[0][1]
    desc = (v.get('desc') or '').strip() or '-'
    if merged:
        desc_sec = '## 说明\n\n> 该名称对应 %d 个实体ID：%s\n\n%s' % (len(items), ' / '.join(ids), desc)
    else:
        desc_sec = f'## 说明\n\n{desc}'
    content = f"""# {name}

{header('simulated_blocks.json', ids, merged)}

## 基本信息

{basic_table(name, '区块', {}, merged)}

{desc_sec}
"""
    with open(os.path.join(blk_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    blk_index.append((fname, name))

lines = ['# 区块', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '', '## 全部区块（%d）' % len(blk_index), '']
for fname, name in sorted(blk_index):
    lines.append(f'- [[simulated/区块/{fname}|{name}]]')
open(os.path.join(blk_dir, '区块.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 5. 主索引 ============
main = f"""# 模拟宇宙

> 数据版本：{VER}
> 数据来源：https://github.com/Mar-7th/StarRailRes

## 分类

- [[simulated/祝福/祝福|祝福]]（{len(bless_index)}）— 部分命途已按 ID 段推断，星级待补充
- [[simulated/奇物/奇物|奇物]]（{len(curio_index)}）— 星级 待补充
- [[simulated/事件/事件|事件]]（{len(ev_index)}）— 事件文本待补充
- [[simulated/区块/区块|区块]]（{len(blk_index)}）

## 说明

- 数据基于 StarRailRes v4.5 全量生成。
- 同名实体（不同难度/版本/选项的同一对象）已合并为单一文件，正文聚合全部实体ID。
- 祝福命途：6120-6128（经典模拟宇宙）、6150-6158（黄金与机械）两套 ID 段按命途锚点推断，其余待补充。
- 奇物星级、事件文本暂无结构化数据源，标注「待补充」。
- 事件图片存在共用情况，已在详情中标注。
"""
open(os.path.join(OUT, '模拟宇宙.md'), 'w', encoding='utf-8').write(main)

print('=== 生成统计（唯一名） ===')
print('  祝福: %d 个文件' % len(bless_index))
print('  奇物: %d 个文件' % len(curio_index))
print('  事件: %d 个文件' % len(ev_index))
print('  区块: %d 个文件' % len(blk_index))
known_path = sum(1 for _, _, p in bless_index if p != '待补充')
print('祝福命途已推断: %d / %d' % (known_path, len(bless_index)))
print('事件共用图片组数: %d' % len(shared_imgs))
