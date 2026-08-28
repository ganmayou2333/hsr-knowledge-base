# -*- coding: utf-8 -*-
"""HSR 知识库角色行迹/技能 与 SRR 数据对比报告"""
import json, re, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

SRR = 'StarRailRes-master/index_new/cn'
CHAR_DIR = 'character'

# 1. 加载 SRR 数据
chars = json.load(open(f'{SRR}/characters.json', encoding='utf-8'))
skills = json.load(open(f'{SRR}/character_skills.json', encoding='utf-8'))
skill_trees = json.load(open(f'{SRR}/character_skill_trees.json', encoding='utf-8'))

# 2. 扫描知识库角色文件
skip = {'角色.md'}
kb_chars = {}  # eid -> {file, skills: [(type, name)], traces: [name]}
for root, dirs, fs in os.walk(CHAR_DIR):
    for f in fs:
        if not f.endswith('.md') or f in skip:
            continue
        fp = os.path.join(root, f)
        txt = open(fp, encoding='utf-8').read()
        m = re.search(r'> 实体ID：(.+)', txt)
        if not m:
            continue
        eid = m.group(1).strip()
        # 提取技能：### 普攻：xxx / ### 战技：xxx / ### 终结技：xxx / ### 天赋：xxx / ### 秘技：xxx
        kb_skills = []
        for sm in re.finditer(r'^### (普攻|战技|终结技|天赋|秘技)：(.+)$', txt, re.M):
            kb_skills.append((sm.group(1), sm.group(2).strip()))
        # 提取附加能力：| 附加能力N | 名称 | 效果 |
        kb_traces = []
        for tm in re.finditer(r'^\| 附加能力\d+ \| ([^|]+) \|', txt, re.M):
            name = tm.group(1).strip()
            if name and name != '名称':
                kb_traces.append(name)
        kb_chars[eid] = {'file': f, 'skills': kb_skills, 'traces': kb_traces}

def norm(s):
    """名称归一化：去除所有空格，便于比较"""
    return s.replace(' ', '').replace('\u3000', '').strip()

# 3. 对比
results = []
for eid, kc in sorted(kb_chars.items()):
    if eid not in chars:
        results.append({'eid': eid, 'file': kc['file'], 'error': 'SRR 中无此角色', 'srr_skills': [], 'srr_traces': []})
        continue
    ch = chars[eid]
    # SRR 技能（只保留 5 种常规类型，按类型去重——排除 MazeNormal"攻击"和星魂升级后变体）
    VALID_TYPES = {'普攻', '战技', '终结技', '天赋', '秘技'}
    srr_skill_list = []
    seen_types = set()
    for sid in ch.get('skills', []):
        sk = skills.get(sid, {})
        stype = sk.get('type_text', '')
        if stype in VALID_TYPES and stype not in seen_types:
            srr_skill_list.append({
                'id': sid,
                'type': stype,
                'name': sk.get('name', ''),
            })
            seen_types.add(stype)
    # SRR 行迹（附加能力节点 = Point06/07/08，共 3 个，按 anchor 去重——排除星魂升级后变体）
    ABILITY_ANCHORS = {'Point06', 'Point07', 'Point08'}
    srr_trace_list = []
    seen_anchors = set()
    for tid in ch.get('skill_trees', []):
        st = skill_trees.get(tid, {})
        name = st.get('name', '')
        anchor = st.get('anchor', '')
        if anchor in ABILITY_ANCHORS and name and name.strip() and anchor not in seen_anchors:
            srr_trace_list.append({'id': tid, 'name': name.strip(), 'anchor': anchor})
            seen_anchors.add(anchor)
    results.append({
        'eid': eid, 'file': kc['file'],
        'char_name': ch.get('name', ''),
        'srr_skills': srr_skill_list, 'kb_skills': kc['skills'],
        'srr_traces': srr_trace_list, 'kb_traces': kc['traces'],
    })

# 4. 统计
skill_count_mismatch = []
skill_name_mismatch = []
trace_count_mismatch = []
trace_name_mismatch = []
no_issue = []

for r in results:
    if 'error' in r:
        continue
    issues = []
    # 技能数量
    if len(r['srr_skills']) != len(r['kb_skills']):
        skill_count_mismatch.append(r)
        issues.append('skill_count')
    # 技能名称匹配（按类型对齐）
    srr_by_type = defaultdict(list)
    for s in r['srr_skills']:
        srr_by_type[s['type']].append(s['name'])
    kb_by_type = defaultdict(list)
    for t, n in r['kb_skills']:
        kb_by_type[t].append(n)
    name_diff = False
    for t in set(list(srr_by_type.keys()) + list(kb_by_type.keys())):
        srr_names = sorted([norm(n) for n in srr_by_type.get(t, [])])
        kb_names = sorted([norm(n) for n in kb_by_type.get(t, [])])
        if srr_names != kb_names:
            name_diff = True
    if name_diff:
        skill_name_mismatch.append(r)
        issues.append('skill_name')
    # 行迹数量
    if len(r['srr_traces']) != len(r['kb_traces']):
        trace_count_mismatch.append(r)
        issues.append('trace_count')
    # 行迹名称
    if sorted(r['srr_traces'][0]['name'] if r['srr_traces'] else '' for _ in [0]) != ['']:
        pass  # placeholder
    srr_trace_names = sorted([norm(t['name']) for t in r['srr_traces']])
    kb_trace_names = sorted([norm(n) for n in r['kb_traces']])
    if srr_trace_names != kb_trace_names:
        trace_name_mismatch.append(r)
        issues.append('trace_name')
    if not issues:
        no_issue.append(r)

# 5. 输出报告
lines = []
lines.append('# HSR 知识库角色行迹/技能 与 SRR 数据对比报告')
lines.append('')
lines.append(f'> 对比时间：2026-08-29')
lines.append(f'> SRR 数据源：StarRailRes-master/index_new/cn/')
lines.append(f'> 知识库角色数：{len(kb_chars)}')
lines.append('')
lines.append('## 一、总览统计')
lines.append('')
lines.append('| 对比项 | 有差异角色数 | 无差异角色数 |')
lines.append('|---|---|---|')
lines.append(f'| 技能数量 | {len(skill_count_mismatch)} | {len(kb_chars)-len(skill_count_mismatch)} |')
lines.append(f'| 技能名称 | {len(skill_name_mismatch)} | {len(kb_chars)-len(skill_name_mismatch)} |')
lines.append(f'| 行迹(附加能力)数量 | {len(trace_count_mismatch)} | {len(kb_chars)-len(trace_count_mismatch)} |')
lines.append(f'| 行迹(附加能力)名称 | {len(trace_name_mismatch)} | {len(kb_chars)-len(trace_name_mismatch)} |')
lines.append(f'| 完全无差异 | {len(no_issue)} | - |')
lines.append('')

def diff_detail(r, label):
    lines.append(f'### {r["file"]} (ID: {r["eid"]}, {r.get("char_name","")})')
    lines.append('')
    if label in ('skill_count', 'skill_name', 'all'):
        lines.append('**SRR 技能：**')
        for s in r['srr_skills']:
            lines.append(f'- [{s["type"]}] {s["name"]} (id={s["id"]})')
        lines.append('')
        lines.append('**知识库技能：**')
        for t, n in r['kb_skills']:
            lines.append(f'- [{t}] {n}')
        lines.append('')
    if label in ('trace_count', 'trace_name', 'all'):
        lines.append('**SRR 附加能力：**')
        for t in r['srr_traces']:
            lines.append(f'- {t["name"]} (id={t["id"]}, anchor={t["anchor"]})')
        lines.append('')
        lines.append('**知识库附加能力：**')
        for n in r['kb_traces']:
            lines.append(f'- {n}')
        lines.append('')
    lines.append('---')
    lines.append('')

lines.append('## 二、技能数量差异明细')
lines.append('')
if skill_count_mismatch:
    for r in skill_count_mismatch:
        diff_detail(r, 'skill_count')
else:
    lines.append('无差异。')
    lines.append('')

lines.append('## 三、技能名称差异明细')
lines.append('')
if skill_name_mismatch:
    for r in skill_name_mismatch:
        diff_detail(r, 'skill_name')
else:
    lines.append('无差异。')
    lines.append('')

lines.append('## 四、行迹(附加能力)数量差异明细')
lines.append('')
if trace_count_mismatch:
    for r in trace_count_mismatch:
        diff_detail(r, 'trace_count')
else:
    lines.append('无差异。')
    lines.append('')

lines.append('## 五、行迹(附加能力)名称差异明细')
lines.append('')
if trace_name_mismatch:
    for r in trace_name_mismatch:
        diff_detail(r, 'trace_name')
else:
    lines.append('无差异。')
    lines.append('')

report = '\n'.join(lines)
open('角色行迹_SRR对比报告.md', 'w', encoding='utf-8').write(report)

# 打印摘要
print('=== 对比摘要 ===')
print(f'知识库角色数: {len(kb_chars)}')
print(f'技能数量差异: {len(skill_count_mismatch)}')
print(f'技能名称差异: {len(skill_name_mismatch)}')
print(f'行迹数量差异: {len(trace_count_mismatch)}')
print(f'行迹名称差异: {len(trace_name_mismatch)}')
print(f'完全无差异: {len(no_issue)}')
print()
print('报告已写入: 角色行迹_SRR对比报告.md')
