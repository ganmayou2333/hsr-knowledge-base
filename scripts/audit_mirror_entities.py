#!/usr/bin/env python3
"""Compare tracked detail files by numeric entity ID; never infer synchronization."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("zh_cn", "en_us", "zh_tw", "ja_jp", "ko_kr")
CATEGORIES = ("character", "lightcone", "relic", "events")
ID_LINE = re.compile(r"^>[ \t]*实体ID[ \t]*[:：][ \t]*(.*?)[ \t]*$", re.MULTILINE)
PARTIAL_LINE = re.compile(r"^>[ \t]*状态[ \t]*[:：][ \t]*部分收录(?:[；;]|[ \t]*$)", re.MULTILINE)


def inventory():
    raw = subprocess.check_output(
        ["git", "ls-files", "-z", "--", *[f"data/{lang}/{cat}" for lang in LANGS for cat in CATEGORIES]],
        cwd=ROOT,
    )
    groups = {(lang, cat): defaultdict(list) for lang in LANGS for cat in CATEGORIES}
    nonnumeric = defaultdict(list)
    no_id = defaultdict(list)
    partial = set()
    for b in raw.split(b"\0"):
        if not b.endswith(b".md"):
            continue
        path = b.decode("utf-8")[len("data/"):]
        lang, category, _ = path.split("/", 2)
        text = (ROOT / "data" / path).read_text(encoding="utf-8-sig")
        if PARTIAL_LINE.search(text):
            partial.add(path)
        ids = ID_LINE.findall(text)
        if len(ids) == 1 and re.fullmatch(r"[0-9]+", ids[0]):
            groups[lang, category][ids[0]].append(path)
        elif ids:
            nonnumeric[lang, category].append({"path": path, "ids": ids})
        else:
            no_id[lang, category].append(path)
    return groups, nonnumeric, no_id, partial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit detailed comparison as JSON")
    args = parser.parse_args()
    groups, nonnumeric, no_id, partial = inventory()
    results = []
    for category in CATEGORIES:
        base = groups["zh_cn", category]
        for lang in LANGS[1:]:
            mirror = groups[lang, category]
            unique_base = {key for key, paths in base.items() if len(paths) == 1}
            unique_mirror = {key for key, paths in mirror.items() if len(paths) == 1}
            results.append({
                "category": category, "language": lang,
                "base_unique": len(unique_base),
                "matched_unique": len(unique_base & unique_mirror),
                # A shared ID is only a candidate pair, not a provenance or
                # synchronization verdict. Include both paths for human review.
                "matched_candidates": {
                    k: {"base": base[k][0], "mirror": mirror[k][0]}
                    for k in sorted(unique_base & unique_mirror)
                },
                "matched_marked_partial": {
                    k: mirror[k][0] for k in sorted(unique_base & unique_mirror)
                    if mirror[k][0] in partial
                },
                "missing": {k: base[k] for k in sorted(unique_base - set(mirror))},
                "extra": {k: mirror[k] for k in sorted(unique_mirror - set(base))},
                "base_duplicates": {k: v for k, v in base.items() if len(v) > 1},
                "mirror_duplicates": {k: v for k, v in mirror.items() if len(v) > 1},
                "base_nonnumeric": nonnumeric["zh_cn", category],
                "mirror_nonnumeric": nonnumeric[lang, category],
                "base_no_id": no_id["zh_cn", category],
                "mirror_no_id": no_id[lang, category],
            })
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("| 类别 | 语言 | 中文唯一 ID | 双方唯一匹配 | 其中标为部分收录 | 镜像缺失 ID | 镜像额外 ID | 中文/镜像重复 ID | 中文/镜像非数字 ID 文件 | 中文/镜像无 ID 文件 |")
        print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for r in results:
            print(f"| {r['category']} | {r['language']} | {r['base_unique']} | {r['matched_unique']} | {len(r['matched_marked_partial'])} | {len(r['missing'])} | {len(r['extra'])} | {len(r['base_duplicates'])}/{len(r['mirror_duplicates'])} | {len(r['base_nonnumeric'])}/{len(r['mirror_nonnumeric'])} | {len(r['base_no_id'])}/{len(r['mirror_no_id'])} |")


if __name__ == "__main__":
    main()
