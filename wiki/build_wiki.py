#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_wiki.py — 零依赖静态 Wiki 生成器
用法：python wiki/build_wiki.py
扫描 zh_cn/ 下所有 .md，生成 wiki/pages/ 静态 HTML + data/ 索引。
不改任何 .md 源文件。
"""
import os, re, json, html, pathlib, shutil, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
PAGES = WIKI / "pages"
DATA = WIKI / "data"
SRC = ROOT / "zh_cn"

# 顶层类别目录（**动态推导**，避免新增类别时白名单漏项 —— 见 D-041）
# 旧实现把类别名硬编码进 resolve()，新增 `enemies/`、`音乐/` 后未同步，
# 导致链接被当作相对路径拼接，产生 9 条死链。
try:
    TOP_DIRS = tuple(sorted(d.name + "/" for d in SRC.iterdir() if d.is_dir()))
except OSError:
    TOP_DIRS = ()

def esc(s): return html.escape(s, quote=False)

def urlq(path):
    """把页面相对路径编码为合法 URL（含全角引号/空格/中文）。保留 '/'。
    修复 D-030：库内存在含 “ ” 的文件名（线索信息·“香味”.md），未编码时浏览器请求会破链。"""
    return urllib.parse.quote(path, safe="/")

# 全站侧边导航：13 个类别（顺序/锚定与 index.html 完全一致）
# 每项 = (顶层目录名, pages/ 下相对路径, 显示名)；顶层目录名用于当前类别高亮。
SIDENAV = [
    ("character",  "character/角色.html",         "角色"),
    ("lightcone",  "lightcone/光锥.html",         "光锥"),
    ("relic",      "relic/遗器.html",             "遗器"),
    ("items",      "items/物品总索引.html",       "物品"),
    ("simulated",  "simulated/模拟宇宙.html",     "模拟宇宙"),
    ("quest",      "quest/索引.html",             "剧情"),
    ("events",     "events/活动.html",            "活动"),
    ("enemies",    "enemies/敌人.html",           "敌人"),
    ("stages",     "stages/关卡.html",            "关卡"),
    ("音乐",        "音乐/音乐.html",              "音乐"),
    ("rules",      "rules/规则.html",             "规则"),
    ("货币战争",    "货币战争/货币战争.html",       "货币战争"),
    ("worldview",  "worldview/世界观总览.html",    "世界观"),
]

def sidenav_html(up, cur_top):
    """生成可折叠、零 JS 的侧边导航；cur_top = 当前页顶层目录，命中则高亮。"""
    rows = []
    for top, href, label in SIDENAV:
        cls = ' class="cur"' if top == cur_top else ""
        rows.append(f'<li{cls}><a href="{up}pages/{href}">{label}</a></li>')
    lis = "\n".join(rows)
    return f'''<nav class="sidenav">
<details open>
<summary>分类导航</summary>
<ul>
{lis}
</ul>
</details>
<ul class="sidenav-aux">
<li><a href="{up}index.html">首页 / 搜索</a></li>
</ul>
</nav>'''

# 全局：所有页面 key 集合（剥 zh_cn/ 前缀，相对 pages/ 根，无后缀）
PAGE_SET = set()
# 全局：源路径(去.md) → 页面键（有数值实体ID时换成 <目录>/<ID>）
SRC2KEY = {}

def convert_inline(text, depth, current_rel=""):
    """depth = 当前页面在 pages/ 下的目录层数；current_rel = 当前页面相对 pages/ 根的路径（无后缀）"""
    up = "../" * depth
    codes = []
    def stash_code(m):
        codes.append(m.group(1)); return f"\x00CODE{len(codes)-1}\x00"
    text = re.sub(r"`([^`]+)`", stash_code, text)

    def resolve(t):
        """把链接目标解析为 PAGE_SET key（剥 zh_cn/、.md，相对路径基于 current_rel 所在目录）"""
        if t.endswith(".md"):
            t = t[:-3]
        if t.startswith("zh_cn/"):
            t = t[6:]
        # 相对路径：不以顶层目录开头时，基于当前页面所在目录拼接
        if not t.startswith(TOP_DIRS):
            base = current_rel.rsplit("/", 1)[0] if "/" in current_rel else ""
            t = (base + "/" + t).replace("//", "/") if base else t
        t = SRC2KEY.get(t, t)
        return t

    # ---- Markdown 链接 [text](path.md) → .html 内链 ----
    def md_link(m):
        disp = m.group(1)
        href_raw = m.group(2).strip()
        if href_raw.startswith("http"):
            return f'<a href="{esc(href_raw)}">{esc(disp)}</a>'
        t = resolve(href_raw)
        if t not in PAGE_SET:
            # 目标不在本次构建范围内（如按合规决定不入库的 quest/剧情文本/）
            # → 降级为纯文本，避免在 CI/公开站产生死链（W-4.6-59）
            return f'<span class="missing">{esc(disp)}</span>'
        return f'<a href="{up}pages/{urlq(t)}.html">{esc(disp)}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", md_link, text)

    # ---- 双链 [[a|b]] ----
    def wikilink(m):
        raw = m.group(0)[2:-2]
        raw = raw.replace("\\|", "|")
        parts = raw.split("|", 1)
        target = parts[0].strip()
        disp = parts[1].strip() if len(parts) > 1 else target
        if not target:
            return f"<span>{esc(disp)}</span>"
        target = resolve(target)
        if target not in PAGE_SET:
            return f'<span class="missing">{esc(disp)}</span>'
        return f'<a href="{up}pages/{urlq(target)}.html">{esc(disp)}</a>'
    text = re.sub(r"\[\[[^\]]+\]\]", wikilink, text)

    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    for i, c in enumerate(codes):
        text = text.replace(f"\x00CODE{i}\x00", f"<code>{esc(c)}</code>")
    return text

def md_to_html(md, depth, current_rel=""):
    lines = md.split("\n")
    out = []
    i = 0
    in_ul = in_ol = in_quote = False
    def close_all():
        nonlocal in_ul,in_ol,in_quote
        if in_ul: out.append("</ul>"); in_ul=False
        if in_ol: out.append("</ol>"); in_ol=False
        if in_quote: out.append("</blockquote>"); in_quote=False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            close_all(); i += 1; buf=[]
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            out.append("<pre><code>"+esc("\n".join(buf))+"</code></pre>"); i += 1; continue
        if line.strip().startswith("|") and i+1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i+1]):
            close_all(); out.append("<table>")
            def split_row(row):
                row = row.replace("\\|", "\x01")
                cells = [c.strip().replace("\x01","|") for c in row.strip().strip("|").split("|")]
                return cells
            cells = split_row(line)
            out.append("<tr>"+"".join(f"<th>{convert_inline(c, depth, current_rel)}</th>" for c in cells)+"</tr>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = split_row(lines[i])
                out.append("<tr>"+"".join(f"<td>{convert_inline(c, depth, current_rel)}</td>" for c in cells)+"</tr>")
                i += 1
            out.append("</table>"); continue
        if line.startswith(">"):
            if not in_quote:
                close_all(); out.append("<blockquote>"); in_quote=True
            out.append("<p>"+convert_inline(line[1:].strip(), depth, current_rel)+"</p>"); i += 1; continue
        else:
            if in_quote: out.append("</blockquote>"); in_quote=False
        h = re.match(r"^(#{1,6})\s+(.*)", line)
        if h:
            lvl = len(h.group(1)); close_all()
            out.append(f"<h{lvl}>"+convert_inline(h.group(2), depth, current_rel)+f"</h{lvl}>"); i += 1; continue
        if re.match(r"^\s*[-*]\s+", line):
            if in_ol: out.append("</ol>"); in_ol=False
            if not in_ul: out.append("<ul>"); in_ul=True
            out.append("<li>"+convert_inline(re.sub(r"^\s*[-*]\s+","",line), depth, current_rel)+"</li>"); i += 1; continue
        if re.match(r"^\s*\d+\.\s+", line):
            if in_ul: out.append("</ul>"); in_ul=False
            if not in_ol: out.append("<ol>"); in_ol=True
            out.append("<li>"+convert_inline(re.sub(r"^\s*\d+\.\s+","",line), depth, current_rel)+"</li>"); i += 1; continue
        else:
            if in_ul: out.append("</ul>"); in_ul=False
            if in_ol: out.append("</ol>"); in_ol=False
        if re.match(r"^---+\s*$", line):
            out.append("<hr/>"); i+=1; continue
        if not line.strip(): i += 1; continue
        out.append("<p>"+convert_inline(line, depth, current_rel)+"</p>"); i += 1
    close_all()
    return "\n".join(out)

META_KEYS = ["数据来源","官方Wiki","数据版本","实体ID","来源","状态","任务地区","任务类型"]
def parse_meta(md):
    meta = {}; body = []
    for line in md.split("\n"):
        m = re.match(r"^>\s*(.+?)[:：]\s*(.+)$", line)
        if m and m.group(1).strip() in META_KEYS:
            meta[m.group(1).strip()] = m.group(2).strip()
        else:
            body.append(line)
    return meta, "\n".join(body)

# 图标映射：KB 顶层目录 → (SRR icon 子目录, 文件命名, 显示尺寸)
ICON_CONF = {
    "character": [("avatar", "{id}.png", 96, 96), ("character", "{id}.png", 200, 280)],
    "lightcone": [("light_cone", "{id}.png", 96, 96)],
    "relic":     [("relic", "{id}.png", 64, 64)],
    "items":     [("item", "{id}.png", 48, 48)],
    "simulated": [("curio", "{id}.png", 64, 64)],
}

def inject_icon(meta, rel, depth, title):
    up = "../" * depth
    eid = meta.get("实体ID", "")
    if not eid or eid.startswith("无"):
        return ""
    m = re.match(r"(\d+)", eid)
    if not m:
        return ""
    eid = m.group(1)
    top = rel.split("/")[0]
    if top not in ICON_CONF:
        return ""
    parts = []
    for sub, tpl, w, h in ICON_CONF[top]:
        fname = tpl.format(id=eid)
        rel_path = f"assets/icons/{sub}/{fname}"
        abs_path = WIKI / rel_path
        if abs_path.exists():
            cls = "entity-icon" + (" entity-big" if w >= 200 else "")
            parts.append(f'<img class="{cls}" src="{up}{rel_path}" alt="{esc(title)}" loading="lazy" width="{w}" height="{h}">')
        else:
            parts.append(f'<div class="icon-fallback" style="width:{w}px;height:{h}px"></div>')
    return '<div class="entity-card">' + "".join(parts) + "</div>"

def main():
    global PAGE_SET, SRC2KEY
    if PAGES.exists(): shutil.rmtree(PAGES)
    PAGES.mkdir(parents=True); DATA.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.rglob("*.md"))
    rel_paths = [(p, str(p.relative_to(SRC).with_suffix("")).replace(os.sep,"/")) for p in files]
    # 源路径(去.md) → 页面键：有数值实体ID则用 <目录>/<ID>，否则保留原相对路径
    SRC2KEY = {}
    for p, rel in rel_paths:
        head = p.read_text(encoding="utf-8", errors="ignore")[:2048]
        m = re.search(r"^>\s*实体ID[：:]\s*([0-9]+)\s*$", head, re.M)
        if m:
            d = rel.rsplit("/", 1)[0] if "/" in rel else ""
            key = (d + "/" + m.group(1)) if d else m.group(1)
        else:
            key = rel
        SRC2KEY[rel] = key
    # 冲突保护：同 key 重复则后者退回原文件名并告警
    _seen = {}
    for rel, key in list(SRC2KEY.items()):
        if key in _seen:
            print(f"WARN key conflict: {rel} vs {_seen[key]} -> keep filename for {rel}")
            SRC2KEY[rel] = rel
        else:
            _seen[key] = rel
    # 第一遍：填充 PAGE_SET
    PAGE_SET = set(SRC2KEY.values())
    titles = []
    for idx, (p, rel) in enumerate(rel_paths):
        md = p.read_text(encoding="utf-8", errors="ignore")
        meta, body = parse_meta(md)
        title = md.split("\n",1)[0].lstrip("# ").strip() or rel
        body = re.sub(r"^#\s+.*\n", "", body, count=1)
        parts = rel.split("/")
        depth = len(parts)
        up = "../" * depth
        crumbs = '<a href="'+up+'index.html">首页</a>'
        crumbs += " / ".join(f"<span>{esc(x)}</span>" for x in parts[:-1])
        crumbs += f" / <strong>{esc(parts[-1])}</strong>"
        prev_nxt = ""
        if idx > 0:
            pr = rel_paths[idx-1][1]; pt = pr.split("/")[-1]; prk = SRC2KEY[pr]
            prev_nxt += f'<a class="navprev" href="{up}pages/{urlq(prk)}.html">← {esc(pt)}</a>'
        else: prev_nxt += '<span class="navprev"></span>'
        if idx < len(rel_paths)-1:
            nr = rel_paths[idx+1][1]; nt = nr.split("/")[-1]; nrk = SRC2KEY[nr]
            prev_nxt += f'<a class="navnext" href="{up}pages/{urlq(nrk)}.html">{esc(nt)} →</a>'
        else: prev_nxt += '<span class="navnext"></span>'
        meta_html = '<div class="meta">'+"".join(f"<div><b>{esc(k)}:</b> {esc(v)}</div>" for k,v in meta.items())+"</div>" if meta else ""
        icon_html = inject_icon(meta, rel, depth, title)
        sidenav = sidenav_html(up, parts[0])
        doc = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — HSR Wiki</title>
<link rel="stylesheet" href="{up}assets/style.css"></head><body>
<div class="topbar"><button id="theme-toggle" class="theme-toggle" type="button">跟随系统</button></div>
<nav class="crumbs">{crumbs}</nav>
{sidenav}
<main>
{icon_html}
{md_to_html(body, depth, rel)}
{meta_html}
<nav class="pager">{prev_nxt}</nav>
<footer class="site-footer">© 米哈游版权所有 · 本站为非官方、非商业同人整理，与 HoYoverse 无关联 · 由 AGPL-3.0 项目（许可仅覆盖代码与编排）hsr-knowledge-base 生成 · 图标数据来自 StarRailRes（AGPL-3.0）</footer>
</main>
<script src="{up}assets/theme.js"></script>
</body></html>"""
        key = SRC2KEY[rel]
        outp = (PAGES / key.replace("/", os.sep)).with_suffix(".html")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(doc, encoding="utf-8")
        titles.append({"path": key+".html", "title": title, "category": parts[0] if len(parts)>1 else "", "lang":"zh_cn"})

    # 死链统计
    link_report = {"total":0, "dead":0, "dead_list":[]}
    for htmlf in PAGES.rglob("*.html"):
        rel = str(htmlf.relative_to(PAGES)).replace(os.sep,"/")
        content = htmlf.read_text(encoding="utf-8")
        for m in re.finditer(r'<a href="[^"]*pages/([^"]+\.html)"( class="dead")?>([^<]+)</a>', content):
            link_report["total"] += 1
            target_decoded = urllib.parse.unquote(m.group(1))
            if m.group(2):
                link_report["dead"] += 1
                link_report["dead_list"].append({"source": rel, "target": target_decoded, "text": m.group(3)})

    (DATA/"titles.js").write_text("window.TITLES = "+json.dumps(titles,ensure_ascii=False)+";", encoding="utf-8")
    (DATA/"link_report.json").write_text(json.dumps(link_report,ensure_ascii=False,indent=2), encoding="utf-8")
    (DATA/"link_report.js").write_text("window.LINK_REPORT = "+json.dumps(link_report,ensure_ascii=False)+";", encoding="utf-8")
    print(f"生成页面: {len(rel_paths)}")
    print(f"总链接: {link_report['total']}, 死链: {link_report['dead']}")

if __name__ == "__main__":
    main()
