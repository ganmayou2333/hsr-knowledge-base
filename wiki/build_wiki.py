#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_wiki.py — 零依赖静态 Wiki 生成器
用法：python wiki/build_wiki.py
扫描 zh_cn/ 下所有 .md，生成 wiki/pages/ 静态 HTML + data/ 索引。
不改任何 .md 源文件。
"""
import os, re, json, html, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
PAGES = WIKI / "pages"
DATA = WIKI / "data"
SRC = ROOT / "zh_cn"

def esc(s): return html.escape(s, quote=False)

# 全局：所有页面 key 集合（剥 zh_cn/ 前缀，相对 pages/ 根，无后缀）
PAGE_SET = set()

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
        if not t.startswith(("character/","lightcone/","relic/","items/","quest/","events/","stages/","simulated/","worldview/","rules/","货币战争/")):
            base = current_rel.rsplit("/", 1)[0] if "/" in current_rel else ""
            t = (base + "/" + t).replace("//", "/") if base else t
        return t

    # ---- Markdown 链接 [text](path.md) → .html 内链 ----
    def md_link(m):
        disp = m.group(1)
        href_raw = m.group(2).strip()
        if href_raw.startswith("http"):
            return f'<a href="{esc(href_raw)}">{esc(disp)}</a>'
        t = resolve(href_raw)
        exists = t in PAGE_SET
        cls = ' class="dead"' if not exists else ""
        return f'<a href="{up}pages/{t}.html"{cls}>{esc(disp)}</a>'
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
        exists = target in PAGE_SET
        cls = ' class="dead"' if not exists else ""
        return f'<a href="{up}pages/{target}.html"{cls}>{esc(disp)}</a>'
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
    global PAGE_SET
    if PAGES.exists(): shutil.rmtree(PAGES)
    PAGES.mkdir(parents=True); DATA.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.rglob("*.md"))
    rel_paths = [(p, str(p.relative_to(SRC).with_suffix("")).replace(os.sep,"/")) for p in files]
    # 第一遍：填充 PAGE_SET
    PAGE_SET = set(r for _, r in rel_paths)
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
            pr = rel_paths[idx-1][1]; pt = pr.split("/")[-1]
            prev_nxt += f'<a class="navprev" href="{up}pages/{pr}.html">← {esc(pt)}</a>'
        else: prev_nxt += '<span class="navprev"></span>'
        if idx < len(rel_paths)-1:
            nr = rel_paths[idx+1][1]; nt = nr.split("/")[-1]
            prev_nxt += f'<a class="navnext" href="{up}pages/{nr}.html">{esc(nt)} →</a>'
        else: prev_nxt += '<span class="navnext"></span>'
        meta_html = '<div class="meta">'+"".join(f"<div><b>{esc(k)}:</b> {esc(v)}</div>" for k,v in meta.items())+"</div>" if meta else ""
        icon_html = inject_icon(meta, rel, depth, title)
        doc = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — HSR Wiki</title>
<link rel="stylesheet" href="{up}assets/style.css"></head><body>
<nav class="crumbs">{crumbs}</nav>
<main>
{icon_html}
{md_to_html(body, depth, rel)}
{meta_html}
<nav class="pager">{prev_nxt}</nav>
<footer class="site-footer">© 米哈游版权所有 · 本站为非官方、非商业同人整理，与 HoYoverse 无关联 · 由 AGPL-3.0 项目（许可仅覆盖代码与编排）hsr-knowledge-base 生成 · 图标数据来自 StarRailRes（AGPL-3.0）</footer>
</main></body></html>"""
        outp = (PAGES / rel.replace("/", os.sep)).with_suffix(".html")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(doc, encoding="utf-8")
        titles.append({"path": rel+".html", "title": title, "category": parts[0] if len(parts)>1 else "", "lang":"zh_cn"})

    # 死链统计
    link_report = {"total":0, "dead":0, "dead_list":[]}
    for htmlf in PAGES.rglob("*.html"):
        rel = str(htmlf.relative_to(PAGES)).replace(os.sep,"/")
        content = htmlf.read_text(encoding="utf-8")
        for m in re.finditer(r'<a href="[^"]*pages/([^"]+\.html)"( class="dead")?>([^<]+)</a>', content):
            link_report["total"] += 1
            if m.group(2):
                link_report["dead"] += 1
                link_report["dead_list"].append({"source": rel, "target": m.group(1), "text": m.group(3)})

    (DATA/"titles.js").write_text("window.TITLES = "+json.dumps(titles,ensure_ascii=False)+";", encoding="utf-8")
    (DATA/"link_report.json").write_text(json.dumps(link_report,ensure_ascii=False,indent=2), encoding="utf-8")
    (DATA/"link_report.js").write_text("window.LINK_REPORT = "+json.dumps(link_report,ensure_ascii=False)+";", encoding="utf-8")
    print(f"生成页面: {len(rel_paths)}")
    print(f"总链接: {link_report['total']}, 死链: {link_report['dead']}")

if __name__ == "__main__":
    main()
