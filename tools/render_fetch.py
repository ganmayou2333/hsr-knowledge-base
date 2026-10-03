#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_fetch.py —— 浏览器渲染抓取 / 核验（Lead 工具，零依赖）

为什么需要它：不少官方站点（如 sr.mihoyo.com）是 **Nuxt/SPA**，纯 HTTP 抓取只能拿到
外壳（`window.__NUXT__`），正文由 JS 渲染。本工具用本机 Chrome/Edge 的 headless 模式
**真正执行 JS**，输出渲染后的 DOM 或纯文本，用于「来源逐字核实」。

用法：
  # 1) 渲染并保存 DOM（留证）
  python tools/render_fetch.py --url "https://sr.mihoyo.com/news/166235" --out .tmp_build/x.html

  # 2) 只输出纯文本
  python tools/render_fetch.py --url "https://..." --text

  # 3) 关键词核验（逐条 OK/MISS）
  python tools/render_fetch.py --url "https://..." --keyword 云边拾暖 风堇

  # 4) 命中时打印上下文（前后各 N 字）
  python tools/render_fetch.py --url "https://..." --keyword 云边拾暖 --context 60

依赖：本机已装 Chrome 或 Edge（Windows 10/11 默认带 Edge）。无需 pip 安装任何东西。
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"(?s)<script.*?</script>")
STYLE_RE = re.compile(r"(?s)<style.*?</style>")
WS_RE = re.compile(r"[ \t\u3000]+")
NL_RE = re.compile(r"\n{2,}")


def find_browser():
    for p in BROWSERS:
        if p and os.path.isfile(p):
            return p
    return None


def strip_html(html: str) -> str:
    s = SCRIPT_RE.sub(" ", html)
    s = STYLE_RE.sub(" ", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|li|tr|h[1-6])>", "\n", s)
    s = TAG_RE.sub(" ", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    s = WS_RE.sub(" ", s)
    s = NL_RE.sub("\n", s)
    return s.strip()


def render(url: str, browser: str, budget_ms: int) -> str:
    fd, tmp = tempfile.mkstemp(suffix=".html", prefix="renderfetch-")
    os.close(fd)
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--hide-scrollbars", f"--virtual-time-budget={budget_ms}",
           "--dump-dom", url]
    with open(tmp, "wb") as fh:
        proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.DEVNULL,
                              timeout=max(60, budget_ms // 1000 * 4))
    with open(tmp, "rb") as fh:
        raw = fh.read()
    try:
        os.remove(tmp)
    except OSError:
        pass
    return raw.decode("utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--url", required=True, help="要渲染的 URL")
    ap.add_argument("--out", default="", help="把渲染后的 DOM 存到该路径（留证）")
    ap.add_argument("--text", action="store_true", help="输出纯文本")
    ap.add_argument("--keyword", nargs="*", default=[], help="要核验的关键词")
    ap.add_argument("--context", type=int, default=0, help="命中时打印前后各 N 字")
    ap.add_argument("--budget-ms", type=int, default=15000, help="JS 执行虚拟时间预算")
    args = ap.parse_args()

    browser = find_browser()
    if not browser:
        print("[render_fetch] 找不到 Chrome 或 Edge，无法渲染。", file=sys.stderr)
        return 2
    print(f"[render_fetch] 浏览器: {browser}")
    print(f"[render_fetch] URL    : {args.url}")

    dom = render(args.url, browser, args.budget_ms)
    text = strip_html(dom)
    print(f"[render_fetch] 渲染完成: DOM {len(dom):,} B / 文本 {len(text):,} 字")

    if args.out:
        d = os.path.dirname(os.path.abspath(args.out))
        os.makedirs(d, exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dom)
        print(f"[render_fetch] DOM 已存: {args.out}")

    if args.text:
        print(text)

    if args.keyword:
        print("[render_fetch] 关键词核验：")
        for k in args.keyword:
            hit = k in text
            print(f"  {k:<18} {'OK' if hit else 'MISS'}")
            if hit and args.context > 0:
                start = 0
                while True:
                    i = text.find(k, start)
                    if i < 0:
                        break
                    a = max(0, i - args.context)
                    seg = re.sub(r"\s+", " ", text[a:a + args.context * 2 + len(k)])
                    print(f"    …{seg}…")
                    start = i + len(k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
