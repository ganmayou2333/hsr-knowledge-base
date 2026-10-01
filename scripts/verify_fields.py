# -*- coding: utf-8 -*-
"""字段级校验：扫描全库详情文件，检查元信息 / 基本信息必备字段 / 重复实体ID / 关键章节空值。
仅校验"详情文件"（含 实体ID 元信息）；索引文件与知识库文章跳过。
已知待补充状态（如物品缺说明/途径、祝福星级/命途待补充、事件文本待补充）单独归类报告，不计为异常。
"""
import os, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

skip_dirs = {'.obsidian', '.git', 'StarRailRes_repo', '.tmp_build', 'temp', 'node_modules', '货币战争', 'StarRailRes_data', 'StarRailRes-master'}

def walk_md():
    files = []
    for root, dirs, fs in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in fs:
            if f.endswith('.md'):
                files.append(os.path.join(root, f).replace(os.sep, '/')[2:])
    return files

def classify(path):
    # 先剥语言根目录（zh_cn/ en_us/ 等），使仓库根运行也能正确分类
    for lang in ('zh_cn/', 'zh_tw/', 'en_us/', 'ja_jp/', 'ko_kr/'):
        if path.startswith(lang):
            path = path[len(lang):]
            break
    if path.startswith('character/'): return 'character'
    if path.startswith('lightcone/'): return 'lightcone'
    if path.startswith('items/'):     return 'items'
    if path.startswith('relic/'):     return 'relic'
    if path.startswith('events/'):    return 'events'
    if path.startswith('stages/'):    return 'stages'
    if path.startswith('simulated/'):
        if '/祝福/' in path:   return 'blessing'
        if '/奇物/' in path:   return 'curio'
        if '/事件/' in path:   return 'event'
        if '/区块/' in path:   return 'block'
        if '/差分宇宙/' in path: return 'diff'
        return 'simulated_other'
    return 'other'

def parse_basic_table(txt):
    """提取基本信息表：| 字段 | 值 |（不跳过「属性」键——角色/事件的属性是真实字段）"""
    d = {}
    for m in re.finditer(r'^\| ([^|]+) \| ([^|]*) \|', txt, re.M):
        k, v = m.group(1).strip(), m.group(2).strip()
        if k and v and v != '值':  # 表头行 | 属性 | 值 | 的 v=='值' 自动跳过
            d[k] = v
    return d

def get_meta(txt):
    meta = {}
    m = re.search(r'> 数据来源：(.+)', txt)
    if m: meta['数据来源'] = m.group(1).strip()
    m = re.search(r'> 数据版本：(.+)', txt)
    if m: meta['数据版本'] = m.group(1).strip()
    m = re.search(r'> 实体ID：(.+)', txt)
    if m: meta['实体ID'] = m.group(1).strip()
    m = re.search(r'> 官方Wiki：(.+)', txt)
    if m: meta['官方Wiki'] = m.group(1).strip()
    return meta

# 各分类：必备元信息 / 必备基本信息字段
REQUIRE = {
    'character': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['角色名称', '命途', '属性', '稀有度'],
        'sections': ['## 配音演员', '## 基础属性', '## 战技'],
    },
    'lightcone': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['光锥名称', '命途', '评级'],
        'sections': ['## 背景故事', '## 基础属性', '## 叠影效果'],
    },
    'items': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['物品名称', '用途', '类型'],
        'sections': [],
        'optional_sections': ['## 说明', '## 获得途径'],  # 已知大量缺失，单独报告
    },
    'relic': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['名称', '类型'],
        'sections': ['## 套装效果', '## 部位'],
        'optional_sections': ['## 获取途径'],  # 4.5 新遗器官方 Wiki 未收录，属已知
    },
    'blessing': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['名称', '类型', '命途', '星级', '特殊类型'],
        'sections': ['## 效果'],
        'optional_basic': ['命途', '星级'],  # 待补充 属已知
    },
    'curio': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['名称', '类型', '星级'],
        'sections': ['## 效果'],
        'optional_basic': ['星级'],
    },
    'event': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['名称', '类型', '属性'],
        'sections': [],
        'optional_sections': ['## 事件文本'],
    },
    'block': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['名称', '类型'],
        'sections': [],
        'optional_sections': ['## 说明'],
    },
    'diff': {
        'meta': ['数据来源', '数据版本', '实体ID'],
        'basic': ['名称', '类型'],
        'sections': [],
        'optional_basic': ['命途', '星级'],
    },
}

files = walk_md()
issues = defaultdict(list)     # (分类, 问题类型) -> [(file, detail)]
known = defaultdict(list)      # 已知待补充 -> [(file, detail)]
ids = defaultdict(list)        # (分类, 实体ID) -> [file]  ← 按分类聚合，避免跨库 ID 伪重复
total_detail = 0

for f in files:
    txt = open(f, encoding='utf-8').read()
    meta = get_meta(txt)
    if '实体ID' not in meta:
        continue  # 索引/知识库文件
    total_detail += 1
    cat = classify(f)
    rule = REQUIRE.get(cat)
    if not rule:
        continue  # 根目录文档 / 未定义分类，不参与字段校验
    # 1. 元信息
    for k in rule['meta']:
        if k not in meta:
            issues[(cat, f'缺元信息:{k}')].append((f, ''))
    # 2. 基本信息必备字段
    basic = parse_basic_table(txt)
    opt_basic = rule.get('optional_basic', [])
    for k in rule['basic']:
        v = basic.get(k, '')
        if not v:
            if k in opt_basic:
                known[(cat, f'基本信息-{k}=待补充')].append((f, ''))
            else:
                issues[(cat, f'缺基本字段:{k}')].append((f, ''))
        elif v == '待补充' and k in opt_basic:
            known[(cat, f'基本信息-{k}=待补充')].append((f, ''))
    # 3. 必备章节（含已知缺失特判）
    known_missing = {}
    for frag, secs in rule.get('known_missing_sections', {}).items():
        if frag in f:
            known_missing = set(secs)
    for sec in rule['sections']:
        if sec not in txt:
            if sec in known_missing:
                known[(cat, f'已知缺章节:{sec}({f.split("/")[-1]})')].append((f, ''))
            else:
                issues[(cat, f'缺章节:{sec}')].append((f, ''))
    # 4. 可选章节（已知状态，单独报告）
    for sec in rule.get('optional_sections', []):
        if sec not in txt:
            known[(cat, f'缺可选章节:{sec}')].append((f, ''))
    # 5. 实体ID 重复（按分类）
    eid = meta['实体ID']
    ids[(cat, eid)].append(f)

# 输出
print('扫描 md 文件数:', len(files))
print('详情文件数:', total_detail)
print()

# 重复 ID（按分类）
dups = {k: fl for k, fl in ids.items() if len(fl) > 1}
print('=== 重复实体ID（同分类内） ===')
if dups:
    for (cat, e), fl in sorted(dups.items(), key=lambda x: -len(x[1])):
        print(f'  [{cat}] {e} x{len(fl)}: {fl[:5]}')
else:
    print('  无')

print()
print('=== 异常（需要关注） ===')
total_issue = 0
for (cat, itype), items in sorted(issues.items()):
    print(f'[{cat}] {itype}: {len(items)}')
    total_issue += len(items)
    for f, d in items[:8]:
        print(f'    - {f} {d}')
print(f'异常合计: {total_issue}')

print()
print('=== 已知待补充状态（不计异常，供维护参考） ===')
total_known = 0
for (cat, itype), items in sorted(known.items()):
    print(f'[{cat}] {itype}: {len(items)}')
    total_known += len(items)
print(f'已知待补充合计: {total_known}')
