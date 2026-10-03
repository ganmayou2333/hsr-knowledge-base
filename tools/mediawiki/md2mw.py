#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2mw.py — 把 vault 的 zh_cn/*.md 转成 MediaWiki wikitext（模板 {{实体}} + 正文）

设计（对齐本库规范）：
  * 头部 `# 标题` → 页面标题
  * 头部 `> 数据来源：/ > 实体ID：/ > 数据版本：/ > 官方Wiki：` → 填进 {{实体}} 参数
  * `> 创建时间：/ > 更新时间：` → 丢弃（vault 专用字段）
  * 路径 → 类型/分类：`character/…`→角色，`lightcone/…`→光锥，`items/…`→物品，
    `relic/…`→遗器，`音乐/…`→音乐，`events/…`→活动，`enemies/…`→敌人，`stages/…`→关卡
  * `[[zh_cn/路径|显示名]]` → `[[页面标题|显示名]]`（标题取自映射表；未收录则降级为纯文本）
  * `## / ###` → `== / ===`；markdown 表格 → MediaWiki 表格；列表 → `*` / `#`；
    `**粗**` → `'''粗'''`；`[文字](url)` → `[url 文字]`

用法：
  python md2mw.py --only 音乐 --limit 5 --out <目录>
  python md2mw.py --only character --limit 50 --out <目录>
"""
import os, re, sys, json, argparse

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'G:\HSR'
SRC = os.path.join(ROOT, 'zh_cn')

CAT_MAP = {
    'character': ('角色', '角色'), 'lightcone': ('光锥', '光锥'), 'relic': ('遗器', '遗器'),
    'items': ('物品', '物品'), 'music': ('原声带', '音乐'), '音乐': ('原声带', '音乐'),
    'events': ('活动', '活动'), 'enemies': ('敌人', '敌人'), 'stages': ('关卡', '关卡'),
    'quest': ('剧情', '剧情'), 'simulated': ('模拟宇宙', '模拟宇宙'),
    'worldview': ('世界观', '世界观'), 'rules': ('规则', '规则'), '货币战争': ('货币战争', '货币战争'),
}
SKIP_META = ('创建时间', '更新时间')


def read(p):
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
        return f.read().replace('\r\n', '\n')


def collect(only=None, limit=None):
    """收集可转换的文件：rel(相对 zh_cn, 无 .md) -> (abs, title, meta)"""
    out = {}
    for dp, dns, fns in os.walk(SRC):
        for fn in sorted(fns):
            if not fn.endswith('.md'):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, SRC).replace(os.sep, '/')[:-3]
            if only and not rel.startswith(only + '/') and rel.split('/')[0] != only:
                continue
            txt = read(p)
            m = re.search(r'^#\s+(.+?)\s*$', txt, re.M)
            title = m.group(1).strip() if m else os.path.basename(rel)
            meta = {}
            for line in txt.split('\n')[:40]:
                mm = re.match(r'^>\s*([^：:]+)[：:]\s*(.*)$', line)
                if mm:
                    k, v = mm.group(1).strip().strip('*'), mm.group(2).strip()
                    if k and k not in SKIP_META:
                        meta[k] = v
            out[rel] = (p, title, meta)
    items = sorted(out.items())
    if limit:
        items = items[:limit]
    return dict(items)


def conv_inline(s, tmap):
    s = re.sub(r'\*\*(.+?)\*\*', r"'''\1'''", s)
    s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r"''\1''", s)
    s = re.sub(r'!?\[([^\]]+)\]\((https?://[^)]+)\)', r'[\2 \1]', s)
    s = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', s)

    def wl(m):
        raw = m.group(1).replace('\\|', '|')
        parts = raw.split('|', 1)
        tgt = parts[0].strip()
        disp = parts[1].strip() if len(parts) > 1 else ''
        t = tgt[:-3] if tgt.endswith('.md') else tgt
        t = re.sub(r'^zh_cn/', '', t)
        if t in tmap:
            return f'[[{tmap[t]}|{disp or tmap[t]}]]'
        fallback = disp or tgt.split('/')[-1]
        return fallback
    s = re.sub(r'\[\[([^\]]+)\]\]', wl, s)
    s = s.replace('\\|', '|')
    return s


def conv_body(body, tmap):
    lines = body.split('\n')
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        # markdown 表格
        if line.strip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            header = [c.strip() for c in line.strip().strip('|').split('|')]
            out.append('{| class="wikitable"')
            out.append('! ' + ' !! '.join(conv_inline(h, tmap) for h in header))
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                out.append('| ' + ' || '.join(conv_inline(c, tmap) for c in cells))
                i += 1
            out.append('|}')
            continue
        if re.match(r'^\s*```', line):
            out.append('<pre>')
            i += 1
            while i < len(lines) and not re.match(r'^\s*```', lines[i]):
                out.append(lines[i]); i += 1
            out.append('</pre>')
            i += 1
            continue
        m = re.match(r'^(#{2,6})\s+(.+?)\s*$', line)
        if m:
            lvl = len(m.group(1))
            out.append(f"{'=' * lvl} {conv_inline(m.group(2), tmap)} {'=' * lvl}")
            i += 1; continue
        m = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        if m:
            out.append(f"{m.group(1)}* {conv_inline(m.group(2), tmap)}")
            i += 1; continue
        m = re.match(r'^\s*\d+\.\s+(.+)$', line)
        if m:
            out.append(f"# {conv_inline(m.group(1), tmap)}")
            i += 1; continue
        if line.strip() == '---':
            out.append('----'); i += 1; continue
        out.append(conv_inline(line, tmap))
        i += 1
    return '\n'.join(out).strip()


def convert(rel, full_map, title_map):
    p, _raw_title, meta = full_map[rel]
    title = title_map[rel]
    txt = read(p)
    cat = CAT_MAP.get(rel.split('/')[0], ('', ''))
    params = [('名称', title)]
    if meta.get('实体ID'):
        params.append(('实体ID', meta['实体ID']))
    params.append(('数据版本', meta.get('数据版本', '4.6')))
    params.append(('类型', cat[0]))
    params.append(('分类', cat[1]))
    src = meta.get('数据来源', '')
    if meta.get('官方Wiki'):
        src = (src + ' ；' + meta['官方Wiki']).strip(' ；')
    if src:
        params.append(('数据来源', src))
    # 去掉首个 H1 与头部 meta 行（注意 H1 后可能先有空行）
    body = re.sub(r'^#\s+.+?\n', '', txt, count=1)
    body = re.sub(r'^\s*(>\s*.+\n)+', '', body, count=1)
    tpl = '{{实体\n' + '\n'.join(f'|{k}={v}' for k, v in params) + '\n}}'
    return title, tpl + '\n' + conv_body(body, title_map)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--out', default=os.path.join(ROOT, '.tmp_mediawiki', 'export'))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    tmap = collect(args.only, args.limit or None)
    # 标题去重：同名文件（如各目录的「索引」「丰饶」）加「（一级目录）」后缀
    title_map = {}
    used = {}
    for rel in sorted(tmap):
        raw = tmap[rel][1]
        if raw not in used:
            used[raw] = 1
            title_map[rel] = raw
        else:
            used[raw] += 1
            top = rel.split('/')[0]
            cand = f'{raw}（{top}）'
            i = used[raw]
            while cand in used:
                i += 1
                cand = f'{raw}（{top}·{i}）'
            used[cand] = 1
            title_map[rel] = cand
    n = 0
    manifest = []
    for rel in sorted(tmap):
        title, wikitext = convert(rel, tmap, title_map)
        safe = re.sub(r'[\\/:*?"<>|]', '_', title)
        fn = os.path.join(args.out, f'{safe}.wiki')
        with open(fn, 'w', encoding='utf-8', newline='\n') as f:
            f.write(wikitext)
        manifest.append({'rel': rel, 'title': title, 'file': os.path.basename(fn),
                         'bytes': len(wikitext.encode('utf-8'))})
        n += 1
    with open(os.path.join(args.out, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f'转换 {n} 个文件 → {args.out}')
    for m in manifest[:8]:
        print(f"  {m['title']:<28} {m['bytes']:>7} B   {m['rel']}")
    if n > 8:
        print(f'  …共 {n} 个')


if __name__ == '__main__':
    main()
