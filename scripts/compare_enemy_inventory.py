#!/usr/bin/env python3
"""Compare a dated community-Wiki search snapshot to tracked enemy filenames.

Exact names yield candidates, not verified entity matches or coverage assertions.
"""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "docs/evidence/enemy-wiki-search-2026-11-27.json"
INDEXES = {"敌人", "普通敌人", "精英敌人", "首领", "周本BOSS"}


def compare(snapshot, filenames):
    names = {Path(p).stem for p in filenames if Path(p).stem not in INDEXES}
    ids = set()
    matched, missing = [], []
    for entry in snapshot["entries"]:
        identifier = entry["wiki_id"]
        if identifier in ids:
            raise ValueError(f"duplicate wiki page ID: {identifier}")
        ids.add(identifier)
        (matched if entry["name"] in names else missing).append(entry)
    if snapshot["retrieved_unique"] != len(ids):
        raise ValueError("snapshot count does not match unique IDs")
    return {"matched": matched, "missing": missing,
            "local_without_exact_match": sorted(names - {e["name"] for e in matched})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    data = subprocess.check_output(["git", "ls-files", "-z", "--", "zh_cn/enemies"], cwd=ROOT)
    paths = [p.decode("utf-8") for p in data.split(b"\0") if p.endswith(b".md")]
    result = compare(snapshot, paths)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"快照 {snapshot['retrieved_unique']} 页；同名 {len(result['matched'])}；无同名 {len(result['missing'])}")
        print("无同名仅为候选，社区页面编号不是游戏实体 ID；需逐条确认。")
        for e in sorted(result["missing"], key=lambda x: x["wiki_id"], reverse=True):
            print(f"{e['wiki_id']}\t{e['name']}\t{', '.join(e['filters']) or '分类未取得'}")
        print("本库无同名搜索结果：", "、".join(result["local_without_exact_match"]) or "无")


if __name__ == "__main__":
    main()
