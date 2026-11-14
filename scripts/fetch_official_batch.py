#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量抓取《崩坏：星穹铁道》官方内容 API（hoyoverse content_v2_user）。

背景：官方站 hsr.hoyoverse.com 是 SPA，HTML 直取只有 "Loading..."（W-4.7 取证实测）。
本脚本直接调官方内容 API 批量取全文，避免逐页渲染。

用法：
  python scripts/fetch_official_batch.py probe                 # 探测 iChanId 范围内的内容量
  python scripts/fetch_official_batch.py fetch --chan 250      # 抓某频道全部条目（默认 zh-cn）
  python scripts/fetch_official_batch.py manifest              # 由缓存生成 Markdown 清单
  python scripts/fetch_official_batch.py get --id 167246       # 单条（含多语言）

约定：
  * 缓存目录 .tmp_build/official_api/（.gitignore，不入库），可断点续抓；
  * 请求间隔 >=1.2s，失败重试 3 次（指数退避），全程只读、不改仓库数据；
  * 清单只输出「窗口内 + 命中关键词」的条目，供工单当输入。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

APP_ID = "113fe6d3b4514cdd"
BASE = f"https://sg-public-api-static.hoyoverse.com/content_v2_user/app/{APP_ID}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) hsr-knowledge-base/1.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".tmp_build", "official_api")
MANIFEST = os.path.join(ROOT, "docs", "pipeline", "4.7_官方公告批量清单.md")
LANGS = ["zh-cn", "zh-tw", "en-us", "ja-jp", "ko-kr"]
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t\u00a0]+")


def _get(url: str, retries: int = 3) -> dict:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise SystemExit(f"[FAIL] {url} -> {last}")


def plain(html: str) -> str:
    """HTML -> 纯文本（保留换行，便于逐行读表）。"""
    s = (html or "").replace("</p>", "\n").replace("<br>", "\n").replace("<br/>", "\n")
    s = s.replace("</tr>", "\n").replace("</td>", " | ").replace("</th>", " | ")
    s = TAG_RE.sub("", s)
    s = WS_RE.sub(" ", s)
    return "\n".join(line.strip() for line in s.splitlines()).strip()


def page_list(chan: int, page: int, size: int, lang: str) -> dict:
    q = urllib.parse.urlencode({"iChanId": chan, "iPage": page, "iPageSize": size, "sLangKey": lang})
    return _get(f"{BASE}/getContentList?{q}")


def save(obj: dict, lang: str) -> str:
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{obj['iInfoId']}_{lang}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    return path


def cmd_probe(args) -> int:
    print(f"{'chan':>5} {'iTotal':>7}  first-title")
    for chan in range(args.start, args.end + 1):
        try:
            d = page_list(chan, 1, 5, args.lang).get("data") or {}
        except SystemExit as e:
            print(f"{chan:>5}   ERR  {e}")
            continue
        total = d.get("iTotal", 0)
        first = (d.get("list") or [{}])[0].get("sTitle", "")
        if total:
            print(f"{chan:>5} {total:>7}  {first[:48]}")
        time.sleep(1.2)
    return 0


def cmd_fetch(args) -> int:
    got, page, size = {}, 1, 20
    while True:
        d = page_list(args.chan, page, size, args.lang).get("data") or {}
        lst = d.get("list") or []
        if not lst:
            break
        for it in lst:
            got[it["iInfoId"]] = it
            save(it, args.lang)
        total = d.get("iTotal", 0)
        print(f"  page {page}: +{len(lst)} (cum {len(got)}/{total})")
        if len(got) >= total or page * size >= total:
            break
        page += 1
        time.sleep(1.2)
    print(f"[OK] chan={args.chan} lang={args.lang} 条目 {len(got)} -> {CACHE}")
    return 0


def cmd_get(args) -> int:
    langs = LANGS if args.all_langs else [args.lang]
    for lang in langs:
        q = urllib.parse.urlencode({"iInfoId": args.id, "sLangKey": lang})
        d = _get(f"{BASE}/getContent?{q}").get("data") or {}
        if not d:
            print(f"[WARN] {lang}: 无数据")
            continue
        save(d, lang)
        print(f"[OK] {lang}: {d.get('sTitle')} ({len(plain(d.get('sContent')))} 字)")
        time.sleep(1.2)
    return 0


def load_cache() -> list[dict]:
    if not os.path.isdir(CACHE):
        return []
    out, seen = [], set()
    for name in sorted(os.listdir(CACHE)):
        if not name.endswith("_zh-cn.json"):
            continue
        with open(os.path.join(CACHE, name), encoding="utf-8") as f:
            obj = json.load(f)
        if obj["iInfoId"] in seen:
            continue
        seen.add(obj["iInfoId"])
        out.append(obj)
    return out


def cmd_manifest(args) -> int:
    items = load_cache()
    if not items:
        print("[FAIL] 缓存为空，先跑 fetch")
        return 2
    win = args.since
    hits = [o for o in items if (o.get("dtCreateTime") or "") >= win]
    hits.sort(key=lambda o: o.get("dtCreateTime") or "", reverse=True)

    lines = [
        "# 4.7 官方公告批量清单（脚本生成，勿手改）",
        "",
        f"> 生成：`python scripts/fetch_official_batch.py manifest --since {win}`｜缓存 `.tmp_build/official_api/`（gitignore）",
        f"> 数据源：官方内容 API `{BASE}`（`getContentList` / `getContent`）",
        f"> 口径：`dtCreateTime >= {win}` 的条目；共缓存 **{len(items)}** 条，命中 **{len(hits)}** 条。",
        "",
        "| iInfoId | 创建时间 | 起始时间 | 标题 | 纯文本字数 | 官方 URL |",
        "|---|---|---|---|---|---|",
    ]
    for o in hits:
        title = (o.get("sTitle") or "").replace("|", "\\|")
        body_len = len(plain(o.get("sContent")))
        lines.append(
            f"| {o['iInfoId']} | {o.get('dtCreateTime','')} | {o.get('dtStartTime','')} | {title} "
            f"| {body_len} | https://hsr.hoyoverse.com/zh-cn/news/{o['iInfoId']} |"
        )
    lines += [
        "",
        "## 复跑",
        "",
        "```powershell",
        "python scripts/fetch_official_batch.py probe --start 240 --end 260",
        "python scripts/fetch_official_batch.py fetch --chan 250",
        "python scripts/fetch_official_batch.py manifest",
        "```",
        "",
        "正文全文：`python -c \"import json;print(json.load(open('.tmp_build/official_api/167246_zh-cn.json',encoding='utf-8'))['sContent'])\"`"
        " 或直接读缓存 JSON（`sContent` 字段）。",
    ]
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] 清单写入 {MANIFEST}（{len(hits)} 条）")
    for o in hits[:40]:
        print(f"  {o['iInfoId']} {o.get('dtCreateTime')} {o.get('sTitle')}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="官方内容 API 批量抓取")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe", help="探测 iChanId 范围")
    sp.add_argument("--start", type=int, default=240)
    sp.add_argument("--end", type=int, default=260)
    sp.add_argument("--lang", default="zh-cn")
    sp.set_defaults(func=cmd_probe)

    sf = sub.add_parser("fetch", help="抓整个频道")
    sf.add_argument("--chan", type=int, required=True)
    sf.add_argument("--lang", default="zh-cn")
    sf.set_defaults(func=cmd_fetch)

    sg = sub.add_parser("get", help="抓单条")
    sg.add_argument("--id", type=int, required=True)
    sg.add_argument("--lang", default="zh-cn")
    sg.add_argument("--all-langs", action="store_true")
    sg.set_defaults(func=cmd_get)

    sm = sub.add_parser("manifest", help="生成清单")
    sm.add_argument("--since", default="2026-10-20")
    sm.set_defaults(func=cmd_manifest)

    args = p.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
