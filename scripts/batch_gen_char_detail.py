# -*- coding: utf-8 -*-
"""批量生成所有角色的详细数据（技能等级数值表 + 行迹解锁条件/材料）"""
import json, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

base = 'StarRailRes-master/index_new/cn'
chars_srr = json.load(open(f'{base}/characters.json', encoding='utf-8'))
skills_srr = json.load(open(f'{base}/character_skills.json', encoding='utf-8'))
trees_srr = json.load(open(f'{base}/character_skill_trees.json', encoding='utf-8'))
items_srr = json.load(open(f'{base}/items.json', encoding='utf-8'))

def render_desc(desc, params, level_idx=None):
    if level_idx is None:
        level_idx = len(params) - 1
    if not params:
        return desc
    p = params[level_idx] if level_idx < len(params) else params[-1]
    def repl(m):
        idx = int(m.group(1)) - 1
        after = m.group(2) or ''
        if idx < len(p):
            val = p[idx]
            if after == '%':
                return f'{val*100:g}%'
            else:
                if isinstance(val, float) and val == int(val):
                    return str(int(val)) + after
                return str(val) + after
        return m.group(0)
    return re.sub(r'#(\d+)\[i\](.)?', repl, desc)

def get_item_name(item_id):
    item = items_srr.get(str(item_id), {})
    return item.get('name', f'未知({item_id})')

def format_val(v, is_percent=False):
    if is_percent:
        if isinstance(v, (int, float)):
            return f'{v*100:g}%'
    if isinstance(v, float):
        if 0 < v < 1:
            return f'{v*100:g}%'
        if v == int(v):
            return str(int(v))
    return str(v)

def extract_placeholder_info(desc, num_params):
    info = {}
    for m in re.finditer(r'#(\d+)\[i\](.)?', desc):
        n = int(m.group(1))
        after = m.group(2) or ''
        is_pct = (after == '%')
        name = f'参数{n}(%)' if is_pct else f'参数{n}'
        start = max(0, m.start()-10)
        end = min(len(desc), m.end()+8)
        ctx = desc[start:end].replace(f'#{n}[i]', '___').replace('\n', ' ').strip()
        info[n] = {'is_pct': is_pct, 'ctx': ctx, 'after': after, 'name': name}
    return info

def gen_skill_section(eid):
    """生成技能详细数据（去重，只保留基础形态）"""
    if eid not in chars_srr:
        return None
    ch = chars_srr[eid]
    VALID_TYPES = {'普攻', '战技', '终结技', '天赋', '秘技'}
    out = []
    seen_types = set()
    for sid in ch.get('skills', []):
        sk = skills_srr.get(sid, {})
        stype = sk.get('type_text', '')
        if not stype or stype not in VALID_TYPES or stype in seen_types:
            continue
        seen_types.add(stype)
        name = sk.get('name', '')
        desc = sk.get('desc', '')
        params = sk.get('params', [])
        max_lv = sk.get('max_level', 10)
        effect_text = sk.get('effect_text', '')
        simple_desc = sk.get('simple_desc', '')
        
        out.append(f'### {stype}：{name}')
        out.append(f'- **类型**：{effect_text or stype}')
        out.append(f'- **简述**：{simple_desc}')
        out.append(f'- **最大等级**：{max_lv}')
        out.append(f'- **效果模板**：{desc}')
        out.append('')
        
        if params and len(params) > 0:
            num_params = len(params[0])
            ph_info = extract_placeholder_info(desc, num_params)
            labels = []
            is_pct_list = []
            for i in range(1, num_params+1):
                if i in ph_info:
                    labels.append(ph_info[i]['name'])
                    is_pct_list.append(ph_info[i]['is_pct'])
                else:
                    labels.append(f'参数{i}')
                    is_pct_list.append(False)
            
            out.append(f'- **等级数值表**：')
            out.append(f'  | 等级 | {" | ".join(labels)} |')
            out.append(f'  |{"---|" * (num_params+1)}')
            for lv_idx, p in enumerate(params):
                vals = [format_val(v, is_pct_list[i]) for i, v in enumerate(p)]
                out.append(f'  | Lv.{lv_idx+1} | {" | ".join(vals)} |')
            out.append('')
            
            out.append(f'- **参数说明**：')
            for i in range(1, num_params+1):
                if i in ph_info:
                    pi = ph_info[i]
                    out.append(f'  - `#{i}[i]`{pi["after"]} → {pi["name"]}：上下文「{pi["ctx"]}」')
                else:
                    out.append(f'  - 参数{i}：效果模板中无对应 `#{i}[i]` 占位符（预留参数/其他属性）')
            out.append('')
        
        full_desc = render_desc(desc, params)
        out.append(f'- **满级效果**：{full_desc}')
        out.append('')
    return '\n'.join(out)

def gen_trace_section(eid, existing_traces=None):
    """生成行迹详细数据（去重，只保留Point06-08基础形态，保留知识库额外行迹）"""
    if eid not in chars_srr:
        return None
    ch = chars_srr[eid]
    ABILITY_ANCHORS = {'Point06': '附加能力1', 'Point07': '附加能力2', 'Point08': '附加能力3'}
    out = []
    out.append('')
    out.append('| 编号 | 名称 | 解锁条件 | 效果模板 | 效果 | 解锁材料 |')
    out.append('|---|---|---|---|---|---|')
    
    seen_anchors = set()
    for tid in ch.get('skill_trees', []):
        t = trees_srr.get(tid, {})
        anchor = t.get('anchor', '')
        if anchor not in ABILITY_ANCHORS or anchor in seen_anchors:
            continue
        seen_anchors.add(anchor)
        name = t.get('name', '')
        desc = t.get('desc', '')
        params = t.get('params', [])
        full_desc = render_desc(desc, params)
        levels = t.get('levels', [])
        promo = levels[0].get('promotion', '?') if levels else '?'
        materials = levels[0].get('materials', []) if levels else []
        mat_str = '、'.join([f'{get_item_name(m["id"])}×{m["num"]}' for m in materials])
        out.append(f'| {ABILITY_ANCHORS[anchor]} | {name} | 晋阶{promo} | {desc} | {full_desc} | {mat_str} |')
    
    # 保留知识库中已有的额外行迹（第4个及以上，如开拓者记忆的"未完的尾声"）
    if existing_traces:
        for i, trace in enumerate(existing_traces):
            if i >= 3:  # 第4个及以上
                out.append(f'| 附加能力{i+1} | {trace["name"]} | 待补充 | {trace.get("desc", "")} | {trace.get("effect", "")} | 待补充 |')
    
    out.append('')
    return '\n'.join(out)

def extract_existing_traces(txt):
    """从知识库文件中提取已有的附加能力（用于保留额外行迹）"""
    traces = []
    m = re.search(r'## 附加能力（行迹）\n(.*?)(?=## 总属性加成)', txt, re.DOTALL)
    if not m:
        return traces
    section = m.group(1)
    for tm in re.finditer(r'\| 附加能力(\d+) \| ([^|]+) \| ([^|]+) \|', section):
        traces.append({'num': int(tm.group(1)), 'name': tm.group(2).strip(), 'effect': tm.group(3).strip()})
    return traces

# 遍历知识库角色
skip_files = {'角色.md'}
processed = 0
skipped = []
errors = []

for root, dirs, fs in os.walk('character'):
    for f in fs:
        if not f.endswith('.md') or f in skip_files:
            continue
        fp = os.path.join(root, f)
        txt = open(fp, encoding='utf-8').read()
        m = re.search(r'> 实体ID：(.+)', txt)
        if not m:
            continue
        eid = m.group(1).strip()
        
        if eid not in chars_srr:
            skipped.append((eid, f, 'SRR中无此角色'))
            continue
        
        try:
            # 提取已有额外行迹
            existing_traces = extract_existing_traces(txt)
            
            # 生成技能和行迹
            skill_section = gen_skill_section(eid)
            trace_section = gen_trace_section(eid, existing_traces)
            
            if skill_section is None or trace_section is None:
                skipped.append((eid, f, '生成失败'))
                continue
            
            # 替换技能部分
            skill_pattern = r'(## 战技\n).*?(?=## 附加能力（行迹）)'
            txt = re.sub(skill_pattern, r'\1' + skill_section + '\n', txt, flags=re.DOTALL)
            
            # 替换行迹部分
            trace_pattern = r'(## 附加能力（行迹）\n).*?(?=## 总属性加成)'
            txt = re.sub(trace_pattern, r'\1' + trace_section + '\n', txt, flags=re.DOTALL)
            
            # 写回文件
            open(fp, 'w', encoding='utf-8').write(txt)
            processed += 1
            print(f'[OK] {eid} {f}')
        except Exception as e:
            errors.append((eid, f, str(e)))
            print(f'[ERROR] {eid} {f}: {e}')

print(f'\n=== 批量生成完成 ===')
print(f'成功: {processed}')
print(f'跳过: {len(skipped)}')
for eid, f, reason in skipped:
    print(f'  {eid} {f}: {reason}')
print(f'错误: {len(errors)}')
for eid, f, err in errors:
    print(f'  {eid} {f}: {err}')
