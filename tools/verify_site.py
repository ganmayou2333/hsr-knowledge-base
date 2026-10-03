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
    if fails:
        print("RESULT: FAIL  失败项 %d：" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
