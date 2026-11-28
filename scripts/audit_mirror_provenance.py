#!/usr/bin/env python3
"""Read-only inventory of tracked mirror Markdown files in the working tree."""

from collections import Counter
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en_us", "zh_tw", "ja_jp", "ko_kr")
CATEGORIES = ("character", "lightcone", "relic", "events")
LABEL = "本地化来源：非官方".encode("utf-8")


def main():
    raw = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "data/zh_cn", *[f"data/{l}" for l in LANGS]], cwd=ROOT
    )
    paths = [p.decode("utf-8")[len("data/"):] for p in raw.split(b"\0") if p.endswith(b".md")]
    counts = Counter()
    for path in paths:
        lang, _, rest = path.partition("/")
        if lang not in LANGS:
            continue
        # Match gen_metrics.py's marker and 8192-byte window, but only tracked paths.
        with (ROOT / "data" / path).open("rb") as f:
            labeled = LABEL in f.read(8192)
        category = rest.split("/", 1)[0]
        for group in ("all", category) if category in CATEGORIES else ("all",):
            counts[lang, group, "total"] += 1
            counts[lang, group, "labeled"] += labeled
    print("| 语言 | 类别 | 已跟踪文件 | 非官方标记 | 无此标记 |")
    print("|---|---|---:|---:|---:|")
    for lang in LANGS:
        for group in ("all", *CATEGORIES):
            total = counts[lang, group, "total"]
            labeled = counts[lang, group, "labeled"]
            print(f"| {lang} | {group} | {total} | {labeled} | {total - labeled} |")


if __name__ == "__main__":
    main()
