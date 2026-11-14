#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_site.py — 静态站回归自检（工单 W-4.6-67）

用法（仓库根目录）：python tools/verify_site.py
零依赖：仅 Python 标准库。只读：不生成、不修改任何文件。
退出码：0 = 全部通过；1 = 存在失败项（失败项逐条打印样例）。

覆盖 6 项（对应工单 §3.A）：
  [1] 每页恰好 1 个 <h1>，且其文本 == <title> 去掉尾部 " — HSR Wiki"
  [2] 面包屑形如 首页 / <a> / <b> / <名称>（</a> 之后紧跟 " / "）
  [3] data/titles.js：无 BOM、无 "# " / "> " 开头的标题、category 无空值
  [4] 死链：link_report.json 的 dead == 0，且与生成页里 class="dead" 的独立复算一致
  [5] 禁用项扫描：border-radius 非 0 / box-shadow / linear-gradient / <img> / 外链脚本 / 外链样式
  [6] 搜索静态检查：esc(h.t.title) / #search[role=combobox] / #results[role=listbox]

说明（第 5 项 <img>）：生成页里的实体图标 <img class="entity-icon" src="…/assets/icons/…">
由 wiki/copy_icons.py 在 CI 构建期产出，按工单 §1.2 不属本次范围；本项只统计**非图标** <img>
（即 src 不指向 assets/icons/ 的图片），同时在结果里附带输出图标 <img> 数量，便于人工核对。
"""
import html
import json
import pathlib
import re
import sys
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
PAGES = WIKI / "pages"
DATA = WIKI / "data"
INDEX = WIKI / "index.html"
STYLE = WIKI / "assets" / "style.css"
APPJS = WIKI / "assets" / "app.js"
THEMEJS = WIKI / "assets" / "theme.js"
TITLES_JS = DATA / "titles.js"
LINK_REPORT = DATA / "link_report.json"

TITLE_SUFFIX = " — HSR Wiki"
RADIUS_ZERO = {"0", "0px", "0%", "0em", "0rem", "0pt", "0pc", "0cm", "0mm", "0in", "0q"}

fails = []


def read(p):
    return p.read_text(encoding="utf-8", errors="replace")


def rel(f):
    try:
        return str(f.relative_to(PAGES))
    except ValueError:
        return str(f)


def fail(item, msg):
    fails.append("[%d] %s" % (item, msg))


def show_sample(item, bad, n=5):
    for f, why in bad[:n]:
        print("      ! %s — %s" % (rel(f), why))
    if len(bad) > n:
        print("      ! …另有 %d 项，略" % (len(bad) - n))
    fail(item, "%d 项不合规" % len(bad))


# ---------------- [1] H1 唯一且正确 ----------------
def check_h1(files):
    ok = 0
    bad = []
    for f in files:
        s = read(f)
        h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", s, re.S | re.I)
        tm = re.search(r"<title\b[^>]*>(.*?)</title>", s, re.S | re.I)
        if not tm:
            bad.append((f, "缺少 <title>"))
            continue
        title = html.unescape(tm.group(1)).strip()
        if not title.endswith(TITLE_SUFFIX):
            bad.append((f, "title 未以「%s」结尾：%s" % (TITLE_SUFFIX, title[:80])))
            continue
        expect = title[: -len(TITLE_SUFFIX)].strip()
        got = [html.unescape(x).strip() for x in h1s]
        if len(got) != 1:
            bad.append((f, "本页 <h1> 数量=%d（应为 1）" % len(got)))
            continue
        if got[0] != expect:
            bad.append((f, "h1 文本≠title：h1=%r title=%r" % (got[0][:60], expect[:60])))
            continue
        ok += 1
    print("[1] H1: %d/%d 合规" % (ok, len(files)))
    if bad:
        show_sample(1, bad)


# ---------------- [2] 面包屑格式 ----------------
def check_crumbs(files):
    ok = 0
    bad = []
    for f in files:
        m = re.search(r'<nav class="crumbs">(.*?)</nav>', read(f), re.S)
        if not m:
            bad.append((f, '缺少 <nav class="crumbs">'))
            continue
        inner = m.group(1)
        if "</a> / " not in inner:
            bad.append((f, '</a> 之后未紧跟 " / "'))
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        if not text.startswith("首页 / "):
            bad.append((f, "面包屑文本未以「首页 / 」开头：%s" % text[:60]))
            continue
        ok += 1
    print("[2] 面包屑: %d/%d 合规" % (ok, len(files)))
    if bad:
        show_sample(2, bad)


# ---------------- [3] titles.js 健康 ----------------
def check_titles():
    if not TITLES_JS.exists():
        print("[3] titles.js: 文件缺失 %s" % TITLES_JS)
        fail(3, "缺少 %s（先运行 python wiki/build_wiki.py）" % TITLES_JS)
        return
    m = re.search(r"window\.TITLES\s*=\s*(\[.*\])\s*;?\s*$", read(TITLES_JS).strip(), re.S)
    if not m:
        print("[3] titles.js: 无法解析 window.TITLES = [...] 结构")
        fail(3, "titles.js 结构不可解析")
        return
    arr = json.loads(m.group(1))
    bom = [a for a in arr if "\ufeff" in (a.get("title") or "")]
    hashy = [a for a in arr if (a.get("title") or "").startswith("# ")]
    quoted = [a for a in arr if (a.get("title") or "").startswith("> ")]
    nocat = [a for a in arr if not (a.get("category") or "").strip()]
    print("[3] titles.js: %d 条, BOM=%d, 井号标题=%d, 元信息标题=%d, 空分类=%d"
          % (len(arr), len(bom), len(hashy), len(quoted), len(nocat)))
    for label, bad in (("BOM 污染", bom), ("以 '# ' 开头", hashy),
                       ("以 '> ' 开头", quoted), ("category 为空", nocat)):
        if bad:
            print("      ! %s：%d 例，如 %r" % (label, len(bad), (bad[0].get("title") or "")[:60]))
            fail(3, "%s %d 例" % (label, len(bad)))


# ---------------- [4] 死链为 0（报告 + 独立复算） ----------------
def check_dead(files):
    report_dead = None
    if LINK_REPORT.exists():
        try:
            report_dead = json.loads(read(LINK_REPORT)).get("dead")
        except Exception as e:
            print("[4] 死链: link_report.json 解析失败：%r" % e)
    hits = 0
    samples = []
    for f in files:
        for m in re.finditer(r'<a href="[^"]*pages/[^"]+\.html" class="dead">', read(f)):
            hits += 1
            if len(samples) < 5:
                samples.append((f, m.group(0)[:100]))
    consistent = (report_dead == hits)
    print("[4] 死链: report=%s, 独立复算=%d  (一致=%s)"
          % ("缺失" if report_dead is None else report_dead, hits, consistent))
    if report_dead != 0:
        fail(4, "link_report.json 的 dead=%s（要求 0）" % report_dead)
    if hits != 0:
        fail(4, "生成页里 class=\"dead\" 链接 %d 条（要求 0）" % hits)
    if not consistent:
        fail(4, "报告 dead=%s 与独立复算 %d 不一致" % (report_dead, hits))
    for f, s in samples:
        print("      ! %s — %s" % (rel(f), s))


# ---------------- [5] 禁用项扫描 ----------------
def check_banned(files):
    radius, shadow, gradient, img, img_icon, ext_script, ext_style = 0, 0, 0, 0, 0, 0, 0
    hit_samples = {}

    def note(key, text):
        hit_samples.setdefault(key, []).append(text)

    targets = [INDEX] + ([STYLE] if STYLE.exists() else []) + files
    for f in targets:
        s = read(f)
        for m in re.finditer(r"border-radius\s*:\s*([^;}\"']*)", s, re.I):
            v = m.group(1).strip().lower()
            if v not in RADIUS_ZERO:
                radius += 1
                note("radius", "%s — border-radius:%s" % (rel(f), m.group(1).strip()[:40]))
        for m in re.finditer(r"box-shadow", s, re.I):
            shadow += 1
            note("shadow", "%s — %s" % (rel(f), m.group(0)))
        for m in re.finditer(r"linear-gradient", s, re.I):
            gradient += 1
            note("gradient", "%s — %s" % (rel(f), m.group(0)))
        for m in re.finditer(r"<img\b[^>]*>", s, re.I):
            if "assets/icons/" in m.group(0):
                img_icon += 1
            else:
                img += 1
                note("img", "%s — %s" % (rel(f), m.group(0)[:90]))
        for m in re.finditer(r"<script\b[^>]*\bsrc\s*=\s*[\"']https?:", s, re.I):
            ext_script += 1
            note("ext_script", "%s — %s" % (rel(f), m.group(0)[:90]))
        for m in re.finditer(r"<link\b[^>]*\bhref\s*=\s*[\"']https?:", s, re.I):
            ext_style += 1
            note("ext_style", "%s — %s" % (rel(f), m.group(0)[:90]))

    print("[5] 禁用项: radius=%d shadow=%d gradient=%d img=%d 外链脚本=%d 外链样式=%d"
          % (radius, shadow, gradient, img, ext_script, ext_style))
    print("      说明: 已跳过 CI 构建期生成的图标 <img> %d 个（src 含 assets/icons/，见工单 §1.2）" % img_icon)
    for key, label in (("radius", "非 0 border-radius"), ("shadow", "box-shadow"),
                       ("gradient", "linear-gradient"), ("img", "非图标 <img>"),
                       ("ext_script", "外链脚本"), ("ext_style", "外链样式")):
        if hit_samples.get(key):
            for s in hit_samples[key][:3]:
                print("      ! %s" % s)
            fail(5, "%s 命中 %d 处" % (label, len(hit_samples[key])))


# ---------------- [6] 搜索可用性静态检查 ----------------
def check_search():
    app = read(APPJS) if APPJS.exists() else ""
    idx = read(INDEX) if INDEX.exists() else ""

    def tag(idv, src):
        m = re.search(r"<[a-zA-Z][^<>]*\bid\s*=\s*[\"']" + re.escape(idv) + r"[\"'][^<>]*>", src)
        return m.group(0) if m else ""

    esc_ok = "esc(h.t.title)" in app
    combobox_ok = 'role="combobox"' in tag("search", idx)
    listbox_ok = 'role="listbox"' in tag("results", idx)
    print("[6] 静态检查: esc=%s combobox=%s listbox=%s" % (esc_ok, combobox_ok, listbox_ok))
    if not esc_ok:
        fail(6, "app.js 未使用 esc(h.t.title) 转义搜索结果标题")
    if not combobox_ok:
        fail(6, "#search 缺少 role=\"combobox\"")
    if not listbox_ok:
        fail(6, "#results 缺少 role=\"listbox\"")


# ---------------- [7] 搜索链接编码 ----------------
def check_search_links():
    app = read(APPJS) if APPJS.exists() else ""
    if not TITLES_JS.exists():
        print("[7] 搜索链接编码: 缺少 %s" % TITLES_JS)
        fail(7, "缺少 %s（先运行 build_wiki.py）" % TITLES_JS)
        return
    m = re.search(r"window\.TITLES\s*=\s*(\[.*\])\s*;?\s*$", read(TITLES_JS).strip(), re.S)
    paths = []
    if m:
        try:
            arr = json.loads(m.group(1))
            paths = [a.get("path") or "" for a in arr]
        except Exception as e:
            print("[7] 搜索链接编码: titles.js 解析失败 %r" % e)
            fail(7, "titles.js 解析失败")
            return
    # 含 URL 保留字符的 path（# / ? / %）与含半角空格的 path，分开统计
    reserved = [p for p in paths if re.search(r"[#?%]", p)]
    space = [p for p in paths if " " in p]
    # 不允许把 h.t.path 直接塞进 href；必须使用 encodeURIComponent 按段编码
    direct = re.search(r'href="pages/\$\{h\.t\.path\}', app)
    encoded = "encodeURIComponent" in app
    print("[7] 搜索链接编码: 含保留字符 path=%d, 空格 path=%d; app.js 已按段 encodeURIComponent = %s"
          % (len(reserved), len(space), encoded))
    if direct:
        print("      ! app.js 仍存在直接把 h.t.path 塞进 href 的写法（应为按段 encodeURIComponent）")
        fail(7, "app.js 把 h.t.path 直接塞进 href")
    if not encoded:
        print("      ! app.js 未使用 encodeURIComponent 按段编码")
        fail(7, "app.js 缺少 encodeURIComponent 按段编码写法")


# ---------------- [8] 未收录链接（明示降级，不再静默） ----------------
def check_missing_links(files):
    report = None
    if LINK_REPORT.exists():
        try:
            report = json.loads(read(LINK_REPORT)).get("missing")
        except Exception as e:
            print("[8] 未收录链接: link_report.json 解析失败 %r" % e)
    if report is None:
        print("[8] 未收录链接: link_report.json 缺 missing 字段（生成器疑似退回旧版）")
        fail(8, "link_report.json 缺 missing 字段")
        return
    hits = 0
    samples = []
    for f in files:
        content = read(f)
        for m in re.finditer(r'<span class="missing"', content):
            hits += 1
            if len(samples) < 5:
                seg = content[m.start():m.start()+90]
                txt = re.sub(r"<[^>]+>", "", seg.split(">", 1)[-1])[:40]
                samples.append((f, txt))
    consistent = (report == hits)
    print("[8] 未收录链接: report=%d, 独立复算=%d (一致=%s)"
          % (report, hits, consistent))
    if hits > 0:
        print("      未收录 %d 处（合规未入库内容，属预期，不算失败）。样例：" % hits)
        for f, txt in samples:
            print("      ! %s — %s" % (rel(f), txt))
    if not consistent:
        fail(8, "report missing=%d 与独立复算 %d 不一致" % (report, hits))


# ---------------- [9] 表格结构 ----------------
def check_tables(files):
    table_n = thead_n = follow_n = 0
    for f in files:
        s = read(f)
        table_n += len(re.findall(r"<table[ >]", s))
        thead_n += len(re.findall(r"<thead", s))
        follow_n += len(re.findall(r"<\s*table[^>]*>\s*<\s*thead", s))
    eq = (table_n == thead_n and table_n > 0)
    print("[9] 表格结构: table=%d thead=%d 紧跟thead=%d (table==thead>0=%s 紧跟==table=%s)"
          % (table_n, thead_n, follow_n, eq, follow_n == table_n))
    if not eq:
        fail(9, "table(%d) 与 thead(%d) 数量不一致或为 0" % (table_n, thead_n))
    if follow_n != table_n:
        fail(9, "<table> 之后紧跟 <thead> 仅 %d/%d（应全部紧跟）" % (follow_n, table_n))


# ---------------- [10] 首页可访问名称 ----------------
def check_search_accessibility():
    idx = read(INDEX) if INDEX.exists() else ""
    m = re.search(r"<[a-zA-Z][^<>]*\bid\s*=\s*[\"']search[\"'][^<>]*>", idx)
    tag = m.group(0) if m else ""
    aria_ok = 'aria-label="搜索页面标题"' in tag
    label_ok = re.search(r"<label\b[^>]*\bfor\s*=\s*[\"']search[\"']", idx, re.I) is not None
    name_ok = aria_ok or label_ok
    combobox_ok = 'role="combobox"' in tag
    controls_ok = 'aria-controls="results"' in tag
    print("[10] 首页可访问名称: aria-label=%s label-for=%s combobox=%s aria-controls=%s"
          % (aria_ok, label_ok, combobox_ok, controls_ok))
    if not name_ok:
        fail(10, '#search 缺少 aria-label="搜索页面标题" 或 <label for="search">')
    if not combobox_ok:
        fail(10, '#search 缺少 role="combobox"')
    if not controls_ok:
        fail(10, '#search 缺少 aria-controls="results"')


# ---------------- [11] 小屏导航 ----------------
def check_small_nav():
    theme = read(THEMEJS) if THEMEJS.exists() else ""
    style = read(STYLE) if STYLE.exists() else ""
    t_matchmedia = "matchMedia" in theme
    t_media = "max-width:640px" in theme
    t_details = ".sidenav details" in theme
    s_small = (re.search(r"@media\s*\(\s*max-width:640px\s*\)\s*\{[^}]*\.sidenav\{max-height",
                         style, re.S) is not None)
    theme_ok = t_matchmedia and t_media and t_details
    print("[11] 小屏导航: theme.js matchMedia=%s max-width:640px=%s .sidenav details=%s ; style.css 小屏.sidenav{max-height=%s"
          % (t_matchmedia, t_media, t_details, s_small))
    if not theme_ok:
        fail(11, "theme.js 缺小屏收起逻辑（matchMedia / max-width:640px / .sidenav details）")
    if not s_small:
        fail(11, "style.css 缺小屏 @media(max-width:640px) 段内 .sidenav{max-height 规则")


# ---------------- [12] 打印样式 ----------------
def check_print():
    style = read(STYLE) if STYLE.exists() else ""
    m = re.search(r"@media\s*print\b\s*\{", style)
    body = ""
    if m:
        start = m.end()
        depth = 1
        i = start
        while i < len(style) and depth > 0:
            ch = style[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        body = style[start:i - 1] if i <= len(style) else ""
    has_print = bool(m)
    has_display_none = "display:none" in body
    print("[12] 打印样式: @media print=%s 块内 display:none=%s" % (has_print, has_display_none))
    if not has_print:
        fail(12, "style.css 缺 @media print 块")
    if not has_display_none:
        fail(12, "@media print 块内缺 display:none（未隐藏界面元素）")


# ---------------- [13] 剧情时间线（W-4.6-85） ----------------
def check_timeline(files):
    """只在剧情索引页出现；数据文件结构正确；版本轴按官方顺序；无外部资源。"""
    timeline_js = WIKI / "assets" / "timeline.js"
    data_js = DATA / "timeline.js"
    index_quest = PAGES / "quest" / "索引.html"

    if not data_js.exists():
        print("[13] 剧情时间线: 缺少 %s（先运行 python wiki/build_wiki.py）" % data_js)
        fail(13, "缺少 wiki/data/timeline.js")
        return
    m = re.search(r"window\.TIMELINE\s*=\s*(\{.*\})\s*;?\s*$", read(data_js).strip(), re.S)
    if not m:
        print("[13] 剧情时间线: data/timeline.js 结构不可解析")
        fail(13, "timeline.js 结构不可解析")
        return
    try:
        data = json.loads(m.group(1))
    except Exception as e:
        print("[13] 剧情时间线: data/timeline.js JSON 解析失败 %r" % e)
        fail(13, "timeline.js 内容不是合法 JSON")
        return

    units = data.get("units") or []
    orders = [u.get("order") or [] for u in units]
    monotonic = orders == sorted(orders)
    dated = [u for u in units if u.get("start")]
    anchors = [u for u in units if u.get("anchor")]

    # 容器只应在剧情索引页出现
    holders = [f for f in files if 'id="timeline-root"' in read(f)]
    only_index = len(holders) == 1 and holders[0].resolve() == index_quest.resolve()
    # 索引页里时间线节点数 == 数据单元数，且必须在 prose 之前
    idx = read(index_quest) if index_quest.exists() else ""
    node_n = len(re.findall(r'class="tl-item"', idx))
    before_prose = ('id="timeline-root"' in idx) and (
        idx.find('id="timeline-root"') < idx.find('<div class="prose'))
    # 增强脚本只在索引页引入，且不得引用外部资源
    has_script = bool(re.search(r'<script src="[^"]*assets/timeline\.js"></script>', idx))
    ext = bool(re.search(r'(?:src|href)\s*=\s*["\']https?://', read(timeline_js) if timeline_js.exists() else ""))

    print("[13] 剧情时间线: 单元=%d(带日期=%d 带锚点=%d) 版本序单调=%s | 节点=%d | 仅索引页=%s 在prose前=%s | timeline.js=%s 外链=%s"
          % (len(units), len(dated), len(anchors), monotonic, node_n,
             only_index, before_prose, has_script, ext))

    if len(units) < 2:
        fail(13, "时间线单元数 %d（应 ≥2，疑似解析退化）" % len(units))
    if len(dated) < 2:
        fail(13, "含官方日期的单元仅 %d 个（应 ≥2）" % len(dated))
    if not monotonic:
        fail(13, "单元 order 序列非单调递增（未按官方版本发布顺序）")
    if node_n != len(units):
        fail(13, "索引页时间线节点 %d 个 ≠ 数据单元 %d 个" % (node_n, len(units)))
    if not only_index:
        print("      ! 含时间线容器页数=%d（应恰为 quest/索引.html）：%s"
              % (len(holders), [rel(f) for f in holders[:5]]))
        fail(13, "时间线容器未恰好出现在剧情索引页")
    if not before_prose:
        fail(13, "时间线容器未出现在 <div class=\"prose\"> 之前")
    if not has_script:
        fail(13, "剧情索引页未引入 assets/timeline.js")
    if not timeline_js.exists():
        fail(13, "缺少 wiki/assets/timeline.js")
    if ext:
        fail(13, "timeline.js 引用了外部资源（图片零入库 / 不得外链）")


# ---------------- [14] 首页仪表盘（W-4.6-87） ----------------
def check_dashboard():
    """stats.js 与 titles.js 一致；最新收录已排序；首页三个容器与脚本齐备。"""
    stats_js = DATA / "stats.js"
    if not stats_js.exists():
        print("[14] 首页仪表盘: 缺少 %s（先运行 python wiki/build_wiki.py）" % stats_js)
        fail(14, "缺少 wiki/data/stats.js")
        return
    m = re.search(r"window\.STATS\s*=\s*(\{.*\})\s*;?\s*$", read(stats_js).strip(), re.S)
    if not m:
        print("[14] 首页仪表盘: stats.js 结构不可解析")
        fail(14, "stats.js 结构不可解析")
        return
    try:
        st = json.loads(m.group(1))
    except Exception as e:
        print("[14] 首页仪表盘: stats.js JSON 解析失败 %r" % e)
        fail(14, "stats.js 内容不是合法 JSON")
        return

    # 与 titles.js 的条数交叉核对（防止统计与实际页数脱节）
    titles_n = None
    if TITLES_JS.exists():
        tm = re.search(r"window\.TITLES\s*=\s*(\[.*\])\s*;?\s*$", read(TITLES_JS).strip(), re.S)
        if tm:
            try:
                titles_n = len(json.loads(tm.group(1)))
            except Exception:
                titles_n = None
    pages_ok = (titles_n is not None and st.get("pages") == titles_n)

    recent = st.get("recent") or []
    ups = [r.get("updated") or "" for r in recent]
    sorted_ok = ups == sorted(ups, reverse=True)
    fields_ok = all(r.get("path") and r.get("title") is not None for r in recent)
    versions = st.get("versions") or {}

    idx = read(INDEX) if INDEX.exists() else ""
    ids = {k: ('id="%s"' % k) in idx for k in
           ("dash-root", "dash-version", "dash-pages", "dash-updated", "dash-recent")}
    quick_ok = 'class="quick"' in idx and idx.count('class="quick-a"') >= 2
    script_ok = bool(re.search(r'<script src="assets/home\.js"', idx))
    stats_ref = bool(re.search(r'<script src="data/stats\.js"', idx))
    # 无 JS 降级文案必须在 HTML 里（不能只由 JS 生成）
    fallback_ok = 'dash-empty' in idx

    print("[14] 首页仪表盘: pages=%s(titles=%s 一致=%s) latestVersion=%s 版本数=%d | recent=%d 倒序=%s 字段齐=%s | 容器齐=%s quick=%s home.js=%s stats.js=%s 无JS降级=%s"
          % (st.get("pages"), titles_n, pages_ok, st.get("latestVersion"),
             len(versions), len(recent), sorted_ok, fields_ok,
             all(ids.values()), quick_ok, script_ok, stats_ref, fallback_ok))

    if not pages_ok:
        fail(14, "stats.pages=%s 与 titles.js 条数=%s 不一致" % (st.get("pages"), titles_n))
    if not versions:
        fail(14, "stats.versions 为空（未解析到任何数据版本）")
    if not st.get("latestVersion"):
        fail(14, "stats.latestVersion 为空")
    if not recent:
        fail(14, "stats.recent 为空（无带更新时间的条目）")
    if not sorted_ok:
        fail(14, "recent 未按 updated 倒序")
    if not fields_ok:
        fail(14, "recent 条目缺 path/title")
    if not all(ids.values()):
        print("      ! 缺失容器：%s" % [k for k, v in ids.items() if not v])
        fail(14, "首页缺仪表盘容器")
    if not quick_ok:
        fail(14, "首页缺「快速访问」区（class=quick / quick-a×2）")
    if not stats_ref or not script_ok:
        fail(14, "首页未同时引入 data/stats.js 与 assets/home.js")
    if not fallback_ok:
        fail(14, "首页缺无 JS 降级文案（dash-empty）")


# ---------------- [15] 角色直达面板（W-4.6-94） ----------------
CHARACTERS_JS = DATA / "characters.js"
CHAR_PANEL_PAGE = PAGES / "character" / "角色.html"


def _basic_fields_from_src(text):
    """机械解析单个源文件的 `## 基本信息` 节字段（与生成器同法，供独立复算）。"""
    bi = re.search(r"^## 基本信息\s*$", text, re.M)
    if not bi:
        return {}
    seg = text[bi.end():]
    cut = re.search(r"^### |^## |^---+", seg, re.M)
    if cut:
        seg = seg[:cut.start()]
    fields = {}
    for row in re.finditer(r"^\| ([^|]+) \| ([^|]*) \|", seg, re.M):
        k = row.group(1).strip(); v = row.group(2).strip()
        if v == "值":
            continue
        fields[k] = v
    return fields


def check_character_panel(files):
    """[15] 角色直达面板：数据文件结构、独立复算、逐条字段比对、页面注入、无JS降级、缺图一致性。"""
    src_chars = ROOT / "zh_cn" / "character"
    if not CHARACTERS_JS.exists():
        print("[15] 角色直达面板: 缺少 %s（先运行 python wiki/build_wiki.py）" % CHARACTERS_JS)
        fail(15, "缺少 wiki/data/characters.js")
        return
    raw = read(CHARACTERS_JS)
    if raw.startswith("\ufeff"):
        print("[15] 角色直达面板: characters.js 含 BOM")
        fail(15, "characters.js 含 BOM")
    m = re.search(r"window\.CHARACTERS\s*=\s*(\{.*\})\s*;?\s*$", raw.strip(), re.S)
    if not m:
        print("[15] 角色直达面板: characters.js 结构不可解析")
        fail(15, "characters.js 结构不可解析")
        return
    try:
        data = json.loads(m.group(1))
    except Exception as e:
        print("[15] 角色直达面板: characters.js JSON 解析失败 %r" % e)
        fail(15, "characters.js 内容不是合法 JSON")
        return

    items = data.get("items") or []
    count = data.get("count")
    ok_count = (count == len(items))
    if not ok_count:
        fail(15, "count=%s ≠ items.length=%d" % (count, len(items)))

    # c. 独立复算：扫描含 实体ID 的源文件数 == items.length；同时逐条提取基本信息字段供 e 比对
    src_map = {}   # 实体ID -> (path, element, rarity)
    src_n = 0
    for p in sorted(src_chars.rglob("*.md")):
        t = read(p)
        if not re.search(r"^>\s*实体ID[：:]\s*[0-9]+\s*$", t, re.M):
            continue
        src_n += 1
        eid_m = re.search(r"^>\s*实体ID[：:]\s*([0-9]+)\s*$", t, re.M)
        f = _basic_fields_from_src(t)
        if eid_m:
            src_map[eid_m.group(1)] = (f.get("命途", "").strip(),
                                       f.get("属性", "").strip(),
                                       f.get("稀有度", "").strip())
    ok_src_n = (src_n == len(items))
    if not ok_src_n:
        fail(15, "独立复算：含实体ID 的源文件 %d 个 ≠ items.length %d" % (src_n, len(items)))

    # d. 字段非空
    d_missing = [i for i in items
                 if not all(i.get(k) for k in ("id", "name", "h1", "path", "element", "rarity", "url"))]
    if d_missing:
        fail(15, "%d 个 item 缺 id/name/h1/path/element/rarity/url 之一" % len(d_missing))

    # e. 逐条与源文件基本信息表比对 path/element/rarity
    e_bad = []
    for i in items:
        got = src_map.get(i.get("id"))
        if not got:
            e_bad.append((i.get("id"), "源文件未找到"))
            continue
        want = (i.get("path"), i.get("element"), i.get("rarity"))
        if got != want:
            e_bad.append((i.get("id"), "源=%s ≠ 数据=%s" % (got, want)))
    if e_bad:
        fail(15, "%d 个 item 的 path/element/rarity 与源文件不一致" % len(e_bad))
        for _id, why in e_bad[:5]:
            print("      ! %s — %s" % (_id, why))

    # f. url 指向真实存在的生成页
    f_bad = []
    for i in items:
        target = PAGES / i["url"]
        if not target.exists():
            f_bad.append((i["url"], "生成页不存在"))
    if f_bad:
        fail(15, "%d 个 item.url 指向不存在的生成页" % len(f_bad))
        for u, why in f_bad[:5]:
            print("      ! %s — %s" % (u, why))

    # g. 角色.html 含 .cpanel 容器；li.citem 数 == items.length
    page = read(CHAR_PANEL_PAGE) if CHAR_PANEL_PAGE.exists() else ""
    has_cpanel = 'class="cpanel' in page
    citem_n = len(re.findall(r'class="citem"', page))
    g_ok = has_cpanel and citem_n == len(items)
    if not has_cpanel:
        fail(15, "角色.html 缺 .cpanel 容器")
    if citem_n != len(items):
        fail(15, "角色.html li.citem=%d ≠ items.length=%d" % (citem_n, len(items)))

    # h. 卡片 href 指向存在的生成页；页面无外链（script/link http）
    h_bad = []
    for href in re.findall(r'<a class="ccard"[^>]*href="([^"]+)"', page):
        inner = re.sub(r"^.*?pages/", "", urllib.parse.unquote(href))
        if not (PAGES / inner).exists():
            h_bad.append(href)
    ext_script = bool(re.search(r'<script\b[^>]*\bsrc\s*=\s*["\']https?:', page))
    ext_style = bool(re.search(r'<link\b[^>]*\bhref\s*=\s*["\']https?:', page))
    if h_bad:
        fail(15, "%d 张卡片 href 指向不存在的生成页" % len(h_bad))
        for h_ in h_bad[:5]:
            print("      ! %s" % h_)
    if ext_script or ext_style:
        fail(15, "角色.html 存在外链脚本/样式")

    # i. 无 JS 降级：head 内 noscript style + 说明文案（含「需 JavaScript」）
    head_noscript = bool(re.search(
        r'<noscript><style>\s*\.cp-filters\s*\{\s*display\s*:\s*none\s*\}\s*</style></noscript>', page))
    noscript_note = bool(re.search(r'<noscript>[^<]*<p[^>]*class="cp-noscript"[^>]*>[^<]*需 JavaScript', page))
    if not head_noscript:
        fail(15, "角色.html 缺 head 内 <noscript><style>.cp-filters{display:none}</style></noscript>")
    if not noscript_note:
        fail(15, "角色.html 缺 <noscript> 说明文案（含「需 JavaScript」）")

    # j. 缺图一致性：hasIcon:false 条目页面上无 <img>，且有 icon-fallback 占位
    noicon = [i for i in items if not i.get("hasIcon")]
    j_bad_imgs = [i["id"] for i in noicon
                  if re.search(r'<img\b[^>]*src="[^"]*assets/icons/avatar/%s\.png"' % re.escape(i["id"]), page)]
    fb_n = len(re.findall(r'icon-fallback', page))
    if j_bad_imgs:
        fail(15, "hasIcon:false 条目仍输出了 <img>：%s" % j_bad_imgs)
    if noicon and fb_n < len(noicon):
        fail(15, "icon-fallback 占位 %d 个 < 缺图条目 %d 个" % (fb_n, len(noicon)))

    # k. 该页所有 <img> 的 src 均含 assets/icons/
    k_bad = [m.group(0) for m in re.finditer(r"<img\b[^>]*>", page)
             if "assets/icons/" not in m.group(0)]
    if k_bad:
        fail(15, "%d 个 <img> 的 src 不含 assets/icons/" % len(k_bad))
        for s in k_bad[:3]:
            print("      ! %s" % s[:90])

    print("[15] 角色直达面板: count=%s items=%d 独立复算=%d 字段齐=%d 逐条比对错=%d url=%d "
          "citem=%d 卡片href错=%d 外链=%s/%s head-noscript=%s 说明=%s 缺图img=%d fallback=%d 非图标img=%d"
          % (count, len(items), src_n, len(items) - len(d_missing), len(e_bad), len(f_bad),
             citem_n, len(h_bad), ext_script, ext_style, head_noscript, noscript_note,
             len(j_bad_imgs), fb_n, len(k_bad)))


def main():
    print("=== 静态站回归自检（W-4.6-67） ===")
    print("root: %s" % ROOT)
    if not PAGES.exists():
        print("生成页目录不存在：%s" % PAGES)
        print("请先运行：python wiki/build_wiki.py")
        print("RESULT: FAIL")
        return 1
    files = sorted(PAGES.rglob("*.html"))
    print("pages: %d 个生成页" % len(files))
    check_h1(files)
    check_crumbs(files)
    check_titles()
    check_dead(files)
    check_banned(files)
    check_search()
    check_search_links()
    check_missing_links(files)
    check_tables(files)
    check_search_accessibility()
    check_small_nav()
    check_print()
    check_timeline(files)
    check_dashboard()
    check_character_panel(files)
    if fails:
        print("RESULT: FAIL  失败项 %d：" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
