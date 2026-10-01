# -*- coding: utf-8 -*-
"""StarRailRes-master 实体ID 与 HSR 知识库实体ID 对照报告"""
import os, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

SRR = 'StarRailRes-master/index_new/cn'

def load_srr_ids(fn, name_key='name'):
    """加载 SRR JSON，返回 {id: name}"""
    d = json.load(open(f'{SRR}/{fn}', encoding='utf-8'))
    out = {}
    for k, v in d.items():
        name = v.get(name_key, v.get('item_name', v.get('title', str(v)[:30]))) if isinstance(v, dict) else str(v)
        out[str(k)] = name
    return out

def scan_kb_ids(directory, skip_files=None):
    """扫描知识库目录，提取实体ID（处理 'id1 / id2' 合并形式），返回 {id: [文件名]}"""
    skip_files = skip_files or set()
    result = {}
    for root, dirs, fs in os.walk(directory):
        for f in fs:
            if not f.endswith('.md') or f in skip_files:
                continue
            fp = os.path.join(root, f)
            txt = open(fp, encoding='utf-8').read()
            m = re.search(r'> 实体ID：(.+)', txt)
            if not m:
                continue
            raw = m.group(1).strip()
            # 拆分合并形式："612830 / 615830" 或 "612830/615830"
            ids = [x.strip() for x in re.split(r'[/／]', raw) if x.strip()]
            for eid in ids:
                result.setdefault(eid, []).append(f)
    return result

def compare(category, srr_fn, kb_dir, skip_files=None, name_key='name'):
    srr = load_srr_ids(srr_fn, name_key)
    kb = scan_kb_ids(kb_dir, skip_files)
    srr_ids = set(srr.keys())
    kb_ids = set(kb.keys())
    matched = srr_ids & kb_ids
    missing = srr_ids - kb_ids   # SRR 有但知识库无
    extra = kb_ids - srr_ids     # 知识库有但 SRR 无
    return {
        'category': category,
        'srr_count': len(srr_ids),
        'kb_entity_count': len(kb_ids),
        'kb_file_count': len(set(f for fl in kb.values() for f in fl)),
        'matched': len(matched),
        'missing': sorted(missing, key=lambda x: (len(x), x)),
        'extra': sorted(extra, key=lambda x: (len(x), x)),
        'srr_names': srr,
        'kb_files': kb,
    }

# 索引/评级文件跳过（非详情文件）
blessing_skip = {'祝福.md', '祝福_三星.md', '祝福_二星.md', '祝福_一星.md', '祝福_四星.md'}
curio_skip = {'奇物.md'}
event_skip = {'事件.md'}
block_skip = {'区块.md'}
char_skip = {'角色.md'}
lc_skip = {'光锥.md'}
item_skip = {'物品.md'}
relic_skip = {'遗器.md'}

results = []
results.append(compare('角色', 'characters.json', 'character', char_skip))
results.append(compare('光锥', 'light_cones.json', 'lightcone', lc_skip))
results.append(compare('物品', 'items.json', 'items', item_skip))
results.append(compare('遗器(套装)', 'relic_sets.json', 'relic', relic_skip))
results.append(compare('模拟宇宙·祝福', 'simulated_blessings.json', 'simulated/祝福', blessing_skip))
results.append(compare('模拟宇宙·奇物', 'simulated_curios.json', 'simulated/奇物', curio_skip))
results.append(compare('模拟宇宙·事件', 'simulated_events.json', 'simulated/事件', event_skip))
results.append(compare('模拟宇宙·区块', 'simulated_blocks.json', 'simulated/区块', block_skip))

# 输出报告
lines = []
lines.append('# StarRailRes-master 与 HSR 知识库 实体ID 对照报告')
lines.append('')
lines.append(f'> SRR 数据源：`StarRailRes-master/index_new/cn/`')
lines.append(f'> 知识库版本基线：4.6（真珠已正式纳入 4.6）')
lines.append('')
lines.append('## 一、总览')
lines.append('')
lines.append('| 分类 | SRR 实体数 | 知识库实体数 | 知识库文件数 | 匹配 | SRR有但库无(缺失) | 库有但SRR无(多余) |')
lines.append('|---|---|---|---|---|---|---|')
for r in results:
    lines.append(f"| {r['category']} | {r['srr_count']} | {r['kb_entity_count']} | {r['kb_file_count']} | {r['matched']} | {len(r['missing'])} | {len(r['extra'])} |")

lines.append('')
lines.append('## 二、各类明细')
lines.append('')

for r in results:
    lines.append(f"### {r['category']}")
    lines.append('')
    lines.append(f"- SRR 实体数：{r['srr_count']}")
    lines.append(f"- 知识库覆盖实体数：{r['kb_entity_count']}（文件数 {r['kb_file_count']}，同名合并已拆分）")
    lines.append(f"- 匹配：{r['matched']}")
    lines.append('')
    if r['missing']:
        lines.append(f"**SRR 有但知识库缺失（{len(r['missing'])}）：**")
        lines.append('')
        lines.append('| ID | SRR 名称 |')
        lines.append('|---|---|')
        for eid in r['missing']:
            name = r['srr_names'].get(eid, '?')
            lines.append(f'| {eid} | {name} |')
        lines.append('')
    else:
        lines.append('**SRR 有但知识库缺失：无**')
        lines.append('')
    if r['extra']:
        lines.append(f"**知识库有但 SRR 无（{len(r['extra'])}）：**")
        lines.append('')
        lines.append('| ID | 知识库文件 |')
        lines.append('|---|---|')
        for eid in r['extra']:
            fl = ', '.join(r['kb_files'].get(eid, []))
            lines.append(f'| {eid} | {fl} |')
        lines.append('')
    else:
        lines.append('**知识库有但 SRR 无：无**')
        lines.append('')
    lines.append('---')
    lines.append('')

report = '\n'.join(lines)
open('SRR_ID对照报告.md', 'w', encoding='utf-8').write(report)

# 打印摘要
print('=== 对照摘要 ===')
print(f"{'分类':<16} {'SRR':>6} {'库实体':>6} {'库文件':>6} {'匹配':>6} {'缺失':>6} {'多余':>6}")
for r in results:
    print(f"{r['category']:<16} {r['srr_count']:>6} {r['kb_entity_count']:>6} {r['kb_file_count']:>6} {r['matched']:>6} {len(r['missing']):>6} {len(r['extra']):>6}")
print()
print('报告已写入: SRR_ID对照报告.md')
