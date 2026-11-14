#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DeepSeek 网页搜索 / 抓取 批量工具（走官方 tools API，不逐页渲染）。

官方文档：https://api-docs.deepseek.com/zh-cn/guides/search
  Search: POST https://api.deepseek.com/v1/tools/search   （query/count/need_content，QPS 100）
  Fetch : POST https://api.deepseek.com/v1/tools/fetch    （url -> Markdown，QPS 25 / 按域名另有限制）

用法：
  python scripts/dsk_batch.py search --query "崩坏星穹铁道 4.7 版本更新" --count 10
  python scripts/dsk_batch.py search-batch --queries-file .tmp_build/queries.txt
  python scripts/dsk_batch.py fetch --url https://www.miyoushe.com/sr/article/79450027
  python scripts/dsk_batch.py fetch-many --urls-file .tmp_build/urls.txt --workers 6
  python scripts/dsk_batch.py manifest --out docs/pipeline/4.7_DeepSeek抓取清单.md

缓存：.tmp_build/dsk/（gitignore，可复跑；命中即跳过）
鉴权：环境变量 DEEPSEEK_API_KEY，缺失时读 ~/.dsh/.credentials.yaml 的 DEEPSEEK_API_KEY
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://api.deepseek.com/v1/tools"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".tmp_build", "dsk")
RETRY_CODES = {408, 429, 500, 502, 503, 504}


def api_key() -> str:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    cred = os.path.join(os.path.expanduser("~"), ".dsh", ".credentials.yaml")
    if os.path.exists(cred):
        with open(cred, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^\s*DEEPSEEK_API_KEY\s*:\s*(\S+)\s*$", line)
                if m:
                    return m.group(1).strip().strip('"\'')
    raise SystemExit("[FAIL] 未找到 DEEPSEEK_API_KEY（环境变量或 ~/.dsh/.credentials.yaml）")


KEY = None


def post(path: str, payload: dict, retries: int = 4) -> dict:
    global KEY
    if KEY is None:
        KEY = api_key()
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last = ""
    for i in range(retries):
        req = urllib.request.Request(
            f"{API}/{path}",
            data=body,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last = f"HTTP {e.code}: {detail}"
            if e.code in RETRY_CODES:
                time.sleep(2 * (i + 1))
                continue
            raise SystemExit(f"[FAIL] {path} {last}")
        except Exception as e:  # noqa: BLE001
            last = str(e)
            time.sleep(2 * (i + 1))
    raise SystemExit(f"[FAIL] {path} 重试耗尽: {last}")


def slug(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def save(kind: str, name: str, obj) -> str:
    d = os.path.join(CACHE, kind)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    return path


def do_search(query: str, count: int, need_content: bool, ori: str | None = None) -> dict:
    payload = {"query": query, "count": count, "need_content": need_content}
    if ori:
        payload["ori_question"] = ori
    return post("search", payload)


def do_fetch(url: str) -> dict:
    return post("fetch", {"url": url})


def cmd_search(args) -> int:
    r = do_search(args.query, args.count, args.need_content, args.ori)
    name = hashlib.sha1(args.query.encode()).hexdigest()[:10]
    save("search", name, {"query": args.query, "response": r})
    res = r.get("results") or []
    print(f"[OK] query={args.query!r} results={len(res)}")
    for it in res:
        body = it.get("content") or it.get("summary") or ""
        print(f"  [{it.get('rerank_score')}] {it.get('title')}\n     {it.get('url')}  ({len(body)} 字正文)")
    return 0


def cmd_search_batch(args) -> int:
    with open(args.queries_file, encoding="utf-8") as f:
        queries = [q.strip() for q in f if q.strip() and not q.startswith("#")]
    hit = 0
    for q in queries:
        r = do_search(q, args.count, True)
        res = r.get("results") or []
        hit += len(res)
        save("search", hashlib.sha1(q.encode()).hexdigest()[:10], {"query": q, "response": r})
        print(f"  {len(res):>2} 条  {q}")
        time.sleep(0.6)
    print(f"[OK] {len(queries)} 个 query，命中 {hit} 条结果 -> {CACHE}/search")
    return 0


def fetch_one(url: str, force: bool = False) -> dict:
    path = os.path.join(CACHE, "fetch", f"{slug(url)}.json")
    if os.path.exists(path) and not force:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return {"url": url, "cached": True, **d}
    try:
        r = do_fetch(url)
    except SystemExit as e:
        return {"url": url, "error": str(e)}
    out = {"url": url, "title": r.get("title", ""), "content": r.get("content", "")}
    save("fetch", slug(url), out)
    return {"url": url, "cached": False, "error": None, **out}


def cmd_fetch(args) -> int:
    r = fetch_one(args.url, args.force)
    if r.get("error"):
        print(f"[FAIL] {r['error']}")
        return 2
    print(f"[OK] {r['title']}  {len(r['content'])} 字  ({'cache' if r['cached'] else 'live'})")
    print(r["content"][:600])
    return 0


def cmd_fetch_many(args) -> int:
    with open(args.urls_file, encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip() and not u.startswith("#")]
    ok = err = 0
    results = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, u, args.force): u for u in urls}
        for fut in cf.as_completed(futs):
            r = fut.result()
            if r.get("error"):
                err += 1
                print(f"  [ERR] {r['url']}  {r['error'][:110]}")
            else:
                ok += 1
                print(f"  [OK ] {len(r['content']):>6} 字  {r['url']}")
            results.append(r)
    print(f"[OK] 成功 {ok} / 失败 {err} -> {CACHE}/fetch")
    return 0 if err == 0 else 1


def cmd_manifest(args) -> int:
    lines = [
        "# 4.7 取证清单（DeepSeek Search / Fetch API 生成）",
        "",
        "> 口径：`POST /v1/tools/search`（`need_content=true`）与 `POST /v1/tools/fetch` 批量取证，",
        "> 文档 <https://api-docs.deepseek.com/zh-cn/guides/search>｜缓存 `.tmp_build/dsk/`（gitignore）",
        "",
        "## 抓取（Fetch）",
        "",
        "| 状态 | 字数 | 标题 | URL |",
        "|---|---|---|---|",
    ]
    fdir = os.path.join(CACHE, "fetch")
    if os.path.isdir(fdir):
        rows = []
        for name in os.listdir(fdir):
            with open(os.path.join(fdir, name), encoding="utf-8") as f:
                d = json.load(f)
            rows.append(d)
        rows.sort(key=lambda d: -len(d.get("content") or ""))
        for d in rows:
            t = (d.get("title") or "").replace("|", "\\|")[:60]
            lines.append(f"| ok | {len(d.get('content') or '')} | {t} | {d.get('url')} |")
    lines += ["", "## 搜索（Search）", "", "| query | 命中 | 高分结果 |", "|---|---|---|"]
    sdir = os.path.join(CACHE, "search")
    if os.path.isdir(sdir):
        for name in os.listdir(sdir):
            with open(os.path.join(sdir, name), encoding="utf-8") as f:
                d = json.load(f)
            res = (d.get("response") or {}).get("results") or []
            top = "；".join(
                f"[{(it.get('rerank_score') or 0):.1f}]{it.get('title')}" for it in res[:3]
            ).replace("|", "\\|")
            lines.append(f"| {d.get('query')} | {len(res)} | {top} |")
    out = args.out or os.path.join("docs", "pipeline", "4.7_DeepSeek抓取清单.md")
    out = out if os.path.isabs(out) else os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] 清单 -> {out}")
    return 0


def cmd_export_urls(args) -> int:
    """从 search 缓存里挑出高价值 URL，写成 fetch-many 的输入清单。"""
    sdir = os.path.join(CACHE, "search")
    allow = [d for d in (args.allow or "").split(",") if d]
    best: dict[str, dict] = {}
    if os.path.isdir(sdir):
        for name in os.listdir(sdir):
            with open(os.path.join(sdir, name), encoding="utf-8") as f:
                d = json.load(f)
            for it in (d.get("response") or {}).get("results") or []:
                url, score = it.get("url") or "", it.get("rerank_score") or 0
                if not url or score < args.min_score:
                    continue
                if allow and not any(a in url for a in allow):
                    continue
                if url not in best or score > best[url]["score"]:
                    best[url] = {"score": score, "title": it.get("title") or "", "query": d.get("query")}
    rows = sorted(best.values(), key=lambda r: -r["score"])
    out = args.out or os.path.join(ROOT, ".tmp_build", "urls_47.txt")
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            for url, v in best.items():
                if v is r:
                    f.write(url + "\n")
    print(f"[OK] {len(rows)} 个 URL -> {out}")
    for r in rows[:40]:
        print(f"  {r['score']:.2f}  {r['title'][:52]}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="DeepSeek Search/Fetch 批量取证")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    s.add_argument("--query", required=True)
    s.add_argument("--count", type=int, default=10)
    s.add_argument("--need-content", action="store_true")
    s.add_argument("--ori")
    s.set_defaults(func=cmd_search)

    sb = sub.add_parser("search-batch")
    sb.add_argument("--queries-file", required=True)
    sb.add_argument("--count", type=int, default=10)
    sb.set_defaults(func=cmd_search_batch)

    f = sub.add_parser("fetch")
    f.add_argument("--url", required=True)
    f.add_argument("--force", action="store_true")
    f.set_defaults(func=cmd_fetch)

    fm = sub.add_parser("fetch-many")
    fm.add_argument("--urls-file", required=True)
    fm.add_argument("--workers", type=int, default=6)
    fm.add_argument("--force", action="store_true")
    fm.set_defaults(func=cmd_fetch_many)

    eu = sub.add_parser("export-urls")
    eu.add_argument("--min-score", type=float, default=1.5)
    eu.add_argument("--allow", default="")
    eu.add_argument("--out")
    eu.set_defaults(func=cmd_export_urls)

    m = sub.add_parser("manifest")
    m.add_argument("--out")
    m.set_defaults(func=cmd_manifest)

    args = p.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

