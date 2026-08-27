# -*- coding: utf-8 -*-
"""生成模拟宇宙知识库：祝福/奇物/事件/区块 详情 + 索引 + 主索引（纯 SRR 数据）"""
import os, re, json

CN = 'G:/HSR/StarRailRes_repo/index_new/cn'
OUT = 'G:/HSR/simulated'
SRC = 'https://github.com/Mar-7th/StarRailRes（index_new/cn/'
VER = '4.5'

os.makedirs(OUT, exist_ok=True)

def load(fn):
    return json.load(open(os.path.join(CN, fn), encoding='utf-8'))

blessings = load('simulated_blessings.json')
curios = load('simulated_curios.json')
events = load('simulated_events.json')
blocks = load('simulated_blocks.json')

def clean_name(name):
    """文件名清洗：尖括号→书名号，其余非法字符→空格"""
    if not name:
        return '未命名'
    s = name.replace('<', '《').replace('>', '》')
    for ch in ':"/\\|?*':
        s = s.replace(ch, ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def header(src_file, eid, extra=None):
    lines = [f'> 数据来源：{SRC}{src_file}）', f'> 数据版本：{VER}', f'> 实体ID：{eid}']
    if extra:
        lines.append(extra)
    return '\n'.join(lines) + '\n\n---\n'

def table(d):
    rows = ['| 属性 | 值 |', '|---|---|']
    for k, v in d.items():
        rows.append(f'| {k} | {v} |')
    return '\n'.join(rows) + '\n'

# ============ 祝福特殊类型识别 ============
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
    if n.startswith('方程式') or '方程' in n[:6]:
        return '方程'
    return '普通祝福'

# ============ 1. 祝福 ============
bless_dir = os.path.join(OUT, '祝福')
os.makedirs(bless_dir, exist_ok=True)
bless_index_rows = []
bless_special = {}
stats = {'祝福': 0, '奇物': 0, '事件': 0, '区块': 0}

for bid, v in blessings.items():
    name = v.get('name', '未命名')
    fname = clean_name(name)
    sp = special_type(name)
    if sp != '普通祝福':
        bless_special.setdefault(sp, []).append(fname)
    desc = (v.get('desc') or '').strip() or '-'
    enh = (v.get('enhanced_desc') or '').strip() or '-'
    content = f"""# {name}

{header('simulated_blessings.json', bid)}

## 基本信息

{table({
    '祝福名称': name,
    '类型': '祝福',
    '命途': '待补充',
    '星级': '待补充',
    '特殊类型': sp,
})}

## 效果

{desc}

## 强化效果

{enh}
"""
    with open(os.path.join(bless_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    bless_index_rows.append((fname, name))
    stats['祝福'] += 1

# 祝福分类索引
lines = ['# 祝福', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '', '## 特殊类型', '']
for sp, items in sorted(bless_special.items()):
    lines.append(f'### {sp}（{len(items)}）')
    lines.append('')
    for it in sorted(items):
        lines.append(f'- [[simulated/祝福/{it}|{it}]]')
    lines.append('')
lines.append('## 全部祝福（' + str(len(bless_index_rows)) + '）')
lines.append('')
lines.append('> 命途 / 星级：待补充')
lines.append('')
# 全部祝福列表（分块，避免单个索引过大）
for fname, name in sorted(bless_index_rows):
    lines.append(f'- [[simulated/祝福/{fname}|{name}]]')
open(os.path.join(bless_dir, '祝福.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 2. 奇物 ============
curio_dir = os.path.join(OUT, '奇物')
os.makedirs(curio_dir, exist_ok=True)
curio_rows = []
for cid, v in curios.items():
    name = v.get('name', '未命名')
    fname = clean_name(name)
    desc = (v.get('desc') or '').strip() or '-'
    bg = (v.get('bg_desc') or '').strip() or '-'
    content = f"""# {name}

{header('simulated_curios.json', cid)}

## 基本信息

{table({
    '奇物名称': name,
    '类型': '奇物',
    '星级': '待补充',
})}

## 效果

{desc}

## 背景故事

{bg}
"""
    with open(os.path.join(curio_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    curio_rows.append((fname, name))
    stats['奇物'] += 1

lines = ['# 奇物', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '']
lines.append(f'## 全部奇物（{len(curio_rows)}）')
lines.append('')
lines.append('> 星级：待补充')
lines.append('')
for fname, name in sorted(curio_rows):
    lines.append(f'- [[simulated/奇物/{fname}|{name}]]')
open(os.path.join(curio_dir, '奇物.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 3. 事件 ============
ev_dir = os.path.join(OUT, '事件')
os.makedirs(ev_dir, exist_ok=True)
ev_rows = []
# 图片复用统计
img_count = {}
for eid, v in events.items():
    img = v.get('image') or ''
    img_count[img] = img_count.get(img, 0) + 1
shared_imgs = {k: v for k, v in img_count.items() if v > 1}

for eid, v in events.items():
    name = v.get('name', '未命名')
    fname = clean_name(name)
    img = v.get('image') or '-'
    img_note = ''
    if img in shared_imgs:
        img_note = f'\n> 注：该图片与另外 {shared_imgs[img]-1} 个事件共用'
    content = f"""# {name}

{header('simulated_events.json', eid)}

## 基本信息

{table({
    '事件名称': name,
    '类型': '事件',
    '属性': v.get('type') or '-',
    '图片': f'`{img}`' if img != '-' else '-',
})}

## 事件文本

待补充
{img_note}
"""
    with open(os.path.join(ev_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    ev_rows.append((fname, name))
    stats['事件'] += 1

lines = ['# 事件', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '']
lines.append(f'## 全部事件（{len(ev_rows)}）')
lines.append('')
lines.append('> 事件文本：待补充')
lines.append('')
for fname, name in sorted(ev_rows):
    lines.append(f'- [[simulated/事件/{fname}|{name}]]')
open(os.path.join(ev_dir, '事件.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 4. 区块 ============
blk_dir = os.path.join(OUT, '区块')
os.makedirs(blk_dir, exist_ok=True)
blk_rows = []
for bid, v in blocks.items():
    name = v.get('name', '未命名')
    fname = clean_name(name)
    desc = (v.get('desc') or '').strip() or '-'
    content = f"""# {name}

{header('simulated_blocks.json', bid)}

## 基本信息

{table({
    '区块名称': name,
    '类型': '区块',
})}

## 说明

{desc}
"""
    with open(os.path.join(blk_dir, fname + '.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    blk_rows.append((fname, name))
    stats['区块'] += 1

lines = ['# 区块', '', '> 返回 [[simulated/模拟宇宙|模拟宇宙主索引]]', '']
lines.append(f'## 全部区块（{len(blk_rows)}）')
lines.append('')
for fname, name in sorted(blk_rows):
    lines.append(f'- [[simulated/区块/{fname}|{name}]]')
open(os.path.join(blk_dir, '区块.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# ============ 5. 主索引 ============
main = f"""# 模拟宇宙

> 数据版本：{VER}
> 数据来源：{SRC[:-3]}

## 分类

- [[simulated/祝福/祝福|祝福]]（{stats['祝福']}）— 命途 / 星级 待补充
- [[simulated/奇物/奇物|奇物]]（{stats['奇物']}）— 星级 待补充
- [[simulated/事件/事件|事件]]（{stats['事件']}）— 事件文本待补充
- [[simulated/区块/区块|区块]]（{stats['区块']}）

## 说明

- 数据基于 StarRailRes v4.5 全量生成。
- 祝福的命途 / 星级、奇物星级、事件文本暂无结构化数据源，标注「待补充」。
- 事件图片存在共用情况，已在详情中标注。
"""
open(os.path.join(OUT, '模拟宇宙.md'), 'w', encoding='utf-8').write(main)

print('=== 生成统计 ===')
for k, v in stats.items():
    print(f'  {k}: {v}')
print(f'祝福特殊类型分布:')
for sp, items in sorted(bless_special.items()):
    print(f'  {sp}: {len(items)}')
print(f'事件共用图片组数: {len(shared_imgs)}（涉及 {sum(shared_imgs.values())} 条事件）')
# 名称清洗检查
import collections
bad = collections.Counter()
for v in list(blessings.values()) + list(curios.values()) + list(events.values()) + list(blocks.values()):
    n = v.get('name', '')
    for ch in '<>:"/\\|?*':
        if ch in n:
            bad[ch] += 1
print(f'需清洗的非法字符分布: {dict(bad)}')
