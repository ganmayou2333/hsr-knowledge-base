#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量抓取米游社「崩坏星穹铁道」官方号文章（API 方式，不渲染页面）。

用途：4.7 入库需要的「活动跃迁 / 遗器部位名与套装效果 / 关卡说明」只在米游社官方号公告里，
      官方站内容 API 不含这些条目。本脚本走米游社 bbs API 批量取，避免逐页浏览。

用法：
  python scripts/fetch_miyoushe_batch.py probe                     # 探测可用列表端点
  python scripts/fetch_miyoushe_batch.py list --uid 288909600      # 抓官方号文章列表（分页）
  python scripts/fetch_miyoushe_batch.py full --since 2026-10-25   # 按列表抓正文（断点续抓）
  python scripts/fetch_miyoushe_batch.py manifest                  # 生成清单 md

缓存：.tmp_build/miyoushe/（gitignore）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) hsr-knowledge-base/1.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".tmp_build", "miyoushe")
MANIFEST = os.path.join(ROOT, "docs", "pipeline", "4.7_米游社公告批量清单.md")
UID = "288909600"  # 「崩坏星穹铁道」官方号
HOSTS = ["https://bbs-api.miyoushe.com", "https://bbs-api-s.miyoushe.com"]
LIST_PATHS = [
    "/post/wapi/getUserPostList?uid={uid}&size={size}&offset={offset}",
    "/post/wapi/userPost?uid={uid}&size={size}&offset={offset}",
    "/post/wapi/getUserArticleList?uid={uid}&size={size}&offset={offset}",
    "/post/wapi/getUserPost?uid={uid}&size={size}&offset={offset}",
]
TAG_RE = re.compile(r"<[^>]+>")


def _get(url: str, retries: int = 3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.miyoushe.com/"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    return {"_error": str(last)}


def cmd_probe(args) -> int:
    for host in HOSTS:
        for tpl in LIST_PATHS:
            url = host + tpl.format(uid=args.uid, size=5, offset=0)
            d = _get(url)
            rc, msg = d.get("retcode"), d.get("message")
            n = len(((d.get("data") or {}).get("list")) or [])
            print(f"{url}\n    retcode={rc} msg={msg} list={n}")
            time.sleep(1.2)
    print("\n单篇对照：")
    for host in HOSTS:
        url = f"{host}/post/wapi/getPostFull?post_id=79450027"
        d = _get(url)
        data = d.get("data") or {}
        post = (data.get("post") or {}).get("post") or {}
        print(f"{url}\n    retcode={d.get('retcode')} title={post.get('subject')}")
        time.sleep(1.2)
    return 0


def _list_url(offset: int, size: int, uid: str) -> str:
    # 实测（2026-11-14）：仅 /post/wapi/userPost 返回 retcode=0，其余端点返回空壳
    return HOSTS[0] + "/post/wapi/userPost?uid={uid}&size={size}&offset={offset}".format(
        uid=uid, size=size, offset=offset
    )


def cmd_list(args) -> int:
    os.makedirs(CACHE, exist_ok=True)
    all_posts, offset, size = [], 0, 20
    while offset is not None and len(all_posts) < args.max_items:
        d = _get(_list_url(offset, size, args.uid))
        if d.get("retcode") != 0:
            print(f"[FAIL] offset={offset} retcode={d.get('retcode')} msg={d.get('message')}")
            break
        data = d.get("data") or {}
        batch = data.get("list") or []
        for it in batch:
            p = it.get("post") or it
            all_posts.append(
                {
                    "post_id": str(p.get("post_id")),
                    "subject": p.get("subject"),
                    "created_at": p.get("created_at"),
                    "view_type": p.get("view_type"),
                }
            )
        # 实测：offset=0 即返回 is_last=true，必须按 next_offset 推进
        nxt = data.get("next_offset")
        offset = int(nxt) if nxt not in (None, "", 0, "0") else (None if data.get("is_last") else offset + size)
        if not batch:
            break
        time.sleep(1.2)
    path = os.path.join(CACHE, "list.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=1)
    print(f"[OK] 列表 {len(all_posts)} 条 -> {path}")
    for p in all_posts[:20]:
        print(f"  {p['post_id']} {time.strftime('%Y-%m-%d', time.localtime(p['created_at'] or 0))} {p['subject']}")
    return 0


def cmd_full(args) -> int:
    lp = os.path.join(CACHE, "list.json")
    if not os.path.exists(lp):
        print("[FAIL] 先跑 list")
        return 2
    with open(lp, encoding="utf-8") as f:
        posts = json.load(f)
    os.makedirs(os.path.join(CACHE, "posts"), exist_ok=True)
    got = skipped = 0
    for p in posts:
        created = time.strftime("%Y-%m-%d", time.localtime(p.get("created_at") or 0))
        if created < args.since:
            skipped += 1
            continue
        out = os.path.join(CACHE, "posts", f"{p['post_id']}.json")
        if os.path.exists(out):
            skipped += 1
            continue
        d = _get(f"{HOSTS[0]}/post/wapi/getPostFull?post_id={p['post_id']}")
        for attempt in range(4):
            if d.get("retcode") == 0:
                break
            # 1034 = 频控；退避后重试
            time.sleep(6 * (attempt + 1))
            d = _get(f"{HOSTS[0]}/post/wapi/getPostFull?post_id={p['post_id']}")
        if d.get("retcode") != 0:
            print(f"  [WARN] {p['post_id']} retcode={d.get('retcode')}")
            continue
        with open(out, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        got += 1
        print(f"  + {p['post_id']} {created} {p['subject']}")
        time.sleep(1.4)
    print(f"[OK] 新抓 {got} 篇，跳过 {skipped} 篇 -> {CACHE}/posts")
    return 0


def cmd_manifest(args) -> int:
    pdir = os.path.join(CACHE, "posts")
    if not os.path.isdir(pdir):
        print("[FAIL] 无正文缓存")
        return 2
    # getPostFull 的 post 对象不含 created_at，用列表缓存补日期
    dates = {}
    lp = os.path.join(CACHE, "list.json")
    if os.path.exists(lp):
        with open(lp, encoding="utf-8") as f:
            for it in json.load(f):
                dates[str(it.get("post_id"))] = it.get("created_at")

    rows = []
    for name in os.listdir(pdir):
        with open(os.path.join(pdir, name), encoding="utf-8") as f:
            d = json.load(f)
        post = ((d.get("data") or {}).get("post") or {})
        post = post.get("post") or {}
        content = ((d.get("data") or {}).get("post") or {}).get("post", {}).get("content") or ""
        text = TAG_RE.sub("", content)
        rows.append(
            {
                "id": str(post.get("post_id")),
                "title": post.get("subject") or "",
                "created": time.strftime("%Y-%m-%d", time.localtime(post.get("created_at") or dates.get(str(post.get("post_id"))) or 0)),
                "len": len(text),
                "url": f"https://www.miyoushe.com/sr/article/{post.get('post_id')}",
                "text": text,
            }
        )
    rows.sort(key=lambda r: r["created"], reverse=True)
    lines = [
        "# 米游社官方号 4.7 公告清单（脚本生成）",
        "",
        f"> 生成：`python scripts/fetch_miyoushe_batch.py manifest`｜缓存 `.tmp_build/miyoushe/posts/`（gitignore）",
        f"> 来源：米游社「崩坏星穹铁道」官方号 uid `{UID}` 的 bbs API",
        f"> 共 **{len(rows)}** 篇；官方站内容 API 不含的活动跃迁/遗器部位名等以本清单为准。",
        "",
        "| post_id | 日期 | 标题 | 正文字数 | 官方 URL |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['id']} | {r['created']} | {r['title'].replace('|','\\|')} | {r['len']} | {r['url']} |")
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    # 正文旁挂，便于 grep
    textdir = os.path.join(CACHE, "text")
    os.makedirs(textdir, exist_ok=True)
    for r in rows:
        with open(os.path.join(textdir, f"{r['id']}.txt"), "w", encoding="utf-8") as f:
            f.write(f"# {r['title']}\n# {r['url']}\n# {r['created']}\n\n{r['text']}\n")
    print(f"[OK] 清单 -> {MANIFEST}（{len(rows)} 篇）；正文 -> {textdir}")
    for r in rows[:25]:
        print(f"  {r['id']} {r['created']} {r['title'][:42]}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="米游社官方号公告批量抓取")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("probe")
    sp.add_argument("--uid", default=UID)
    sp.set_defaults(func=cmd_probe)
    sl = sub.add_parser("list")
    sl.add_argument("--uid", default=UID)
    sl.add_argument("--max-items", type=int, default=200)
    sl.set_defaults(func=cmd_list)
    sf = sub.add_parser("full")
    sf.add_argument("--since", default="2026-10-25")
    sf.set_defaults(func=cmd_full)
    sm = sub.add_parser("manifest")
    sm.set_defaults(func=cmd_manifest)
    args = p.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

