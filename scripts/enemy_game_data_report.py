#!/usr/bin/env python3
"""Cross-check the local enemy detail pages against a local third-party game-data dump.

The dump is a StarRailData mirror (`turnbasedgamedata/`) whose package carries no
version file, so this report never asserts a data version; it only states which
records were read and what they say. Third-party data is not an official source.

Recomputed here (nothing is copied from another report):

* name normalisation (NFKC, middle-dot unification, whitespace removal),
* MonsterTemplateConfig `Rank` -> local category mapping,
* base template ID selection (records whose MonsterID == MonsterTemplateID),
* comparison with the git-tracked (`--tracked`, default) or worktree detail pages.

Read-only: the script never writes into the data directory and refuses to run
when it is missing, so a 2.7 GB dump is never needed inside the repository.
"""
import argparse
import collections
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_ROOT = "turnbasedgamedata"
CATEGORIES = ("普通敌人", "精英敌人", "首领", "周本BOSS")
INDEX_NAMES = frozenset(("敌人",) + CATEGORIES)
RANK_TO_TYPE = {
    "Minion": "普通敌人",
    "MinionLv2": "普通敌人",
    "Elite": "精英敌人",
    "LittleBoss": "首领",
    "BigBoss": "周本BOSS",
}
WEAKNESS_CN = {
    "Physical": "物理",
    "Fire": "火",
    "Ice": "冰",
    "Thunder": "雷",
    "Wind": "风",
    "Quantum": "量子",
    "Imaginary": "虚数",
}
VARIANT_MARKERS = ("（完整）", "（幻象）", "（污染）", "（错误）")
# The parser used by the build script and by tools/test_enemy_index.py.
NUMERIC_ID_RE = re.compile(r"^>\s*实体ID[：:]\s*([0-9]+)\s*$", re.M)
ENTITY_LINE_RE = re.compile(r"^>\s*实体ID[：:].*$", re.M)
WEAKNESS_ROW_RE = re.compile(r"^\|\s*弱点属性\s*\|", re.M)


def normalize(name):
    """Normalise spacing and every middle-dot variant to one review key.

    This is a comparison key, not an identity claim: two names sharing it may
    still be different entities in game.
    """
    name = unicodedata.normalize("NFKC", name)
    return "".join("·" if char in "·•‧∙" else char for char in name if not char.isspace())


def _hash_text(textmap, node):
    if not isinstance(node, dict):
        return None
    return textmap.get(str(node.get("Hash")))


def load_textmap(data_root):
    path = data_root / "TextMap" / "TextMapCHS.json"
    if not path.is_file():
        raise SystemExit(f"[error] 找不到 TextMap：{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_excel(data_root, filename):
    path = data_root / "ExcelOutput" / filename
    if not path.is_file():
        raise SystemExit(f"[error] 找不到 ExcelOutput 文件：{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_game_data(data_root):
    textmap = load_textmap(data_root)
    monsters = load_excel(data_root, "MonsterConfig.json")
    templates = load_excel(data_root, "MonsterTemplateConfig.json")
    return textmap, monsters, templates


def build_name_index(textmap, monsters, templates):
    """name key -> {'display': str, 'records': [...], 'ranks': set, 'base_ids': [...]}."""
    rank_by_template = {t["MonsterTemplateID"]: t.get("Rank") for t in templates}
    index = {}
    unresolved = []
    for record in monsters:
        display = _hash_text(textmap, record.get("MonsterName"))
        if not display:
            unresolved.append({"monster_id": record.get("MonsterID"),
                               "monster_template_id": record.get("MonsterTemplateID")})
            continue
        key = normalize(display)
        entry = index.setdefault(key, {"display": display, "records": [], "ranks": set(),
                                       "base_ids": [], "raw_names": set()})
        entry["records"].append(record)
        entry["raw_names"].add(display)
        rank = rank_by_template.get(record.get("MonsterTemplateID"))
        if rank in RANK_TO_TYPE:
            entry["ranks"].add(RANK_TO_TYPE[rank])
        if record.get("MonsterID") == record.get("MonsterTemplateID"):
            entry["base_ids"].append(record["MonsterID"])
    for entry in index.values():
        entry["base_ids"] = sorted(set(entry["base_ids"]))
        entry["ranks"] = sorted(entry["ranks"])
    return index, unresolved, rank_by_template


def tracked_detail_paths():
    """Detail .md paths as recorded in the git index (read-only git call)."""
    try:
        data = subprocess.check_output(
            ["git", "-c", "core.quotepath=false", "ls-files", "-z", "--", "zh_cn/enemies"],
            cwd=ROOT)
    except (OSError, subprocess.CalledProcessError) as exc:  # pragma: no cover - environment
        raise SystemExit(f"[error] 读取 git 跟踪文件失败：{exc}")
    return sorted(p for p in (x.decode("utf-8") for x in data.split(b"\0")) if p.endswith(".md"))


def worktree_detail_paths():
    """Detail .md paths on disk, including files not yet tracked."""
    return sorted(str(p.relative_to(ROOT)).replace("\\", "/")
                  for p in (ROOT / "data" / "zh_cn" / "enemies").rglob("*.md"))


def parse_local_weakness(path):
    """Read the local `| 弱点属性 |` cell and return the Chinese attribute names found."""
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == "弱点属性":
            value = re.split(r"[（(]", cells[1], maxsplit=1)[0]
            tokens = [t for t in re.split(r"[/、,，\s]+", value) if t]
            return {t for t in tokens if t in set(WEAKNESS_CN.values())}
    return set()


def collect_details(paths):
    """Parse the tracked/worktree enemy .md files into per-category detail records.

    Paths recorded in the git index but no longer present on disk (a rename that
    has not been committed yet) are skipped.
    """
    details = []
    for rel in paths:
        path = ROOT / rel
        parts = rel.split("/")
        if len(parts) < 4:  # zh_cn/enemies/<category>/<name>.md
            continue
        if not path.is_file():
            continue
        stem = path.stem
        if stem in INDEX_NAMES:
            continue
        category = parts[2]
        if category not in CATEGORIES:
            continue
        text = path.read_text(encoding="utf-8")
        id_match = NUMERIC_ID_RE.search(text)
        details.append({
            "path": rel,
            "category": category,
            "name": stem,
            "key": normalize(stem),
            "numeric_id": int(id_match.group(1)) if id_match else None,
            "has_entity_line": bool(ENTITY_LINE_RE.search(text)),
            "has_weakness_row": bool(WEAKNESS_ROW_RE.search(text)),
        })
    return details


def analyse(game_index, unresolved, monsters, templates, details, source_label):
    rank_by_template = {t["MonsterTemplateID"]: t.get("Rank") for t in templates}
    rank_counts = collections.Counter()
    variant_counts = collections.Counter()
    uncovered = collections.defaultdict(list)
    covered_names = set()
    exact_matches = 0
    normalisation_only = []

    for detail in details:
        entry = game_index.get(detail["key"])
        if not entry:
            continue
        detail["game_ranks"] = entry["ranks"]
        detail["base_ids"] = entry["base_ids"]
        detail["game_names"] = sorted(entry["raw_names"])
        if detail["name"] in entry["raw_names"]:
            exact_matches += 1
        else:
            normalisation_only.append({"local": detail["name"],
                                       "game": sorted(entry["raw_names"]),
                                       "category": detail["category"]})

    local_by_category = collections.Counter(d["category"] for d in details)
    local_keys_by_category = {c: set() for c in CATEGORIES}
    for detail in details:
        if "game_ranks" in detail:
            for rank in detail["game_ranks"]:
                local_keys_by_category[rank].add(detail["key"])

    for key in sorted(game_index):
        entry = game_index[key]
        is_variant = any(marker in entry["display"] for marker in VARIANT_MARKERS)
        for rank in entry["ranks"]:
            rank_counts[rank] += 1
            if is_variant:
                variant_counts[rank] += 1
            if key not in local_keys_by_category.get(rank, set()):
                uncovered[rank].append(entry["display"])

    conflicts = [{"category": d["category"], "name": d["name"],
                  "game_ranks": d["game_ranks"]}
                 for d in details if "game_ranks" in d and d["game_ranks"] != [d["category"]]]

    coverage = {}
    for rank in CATEGORIES:
        total = sum(1 for k in game_index if rank in game_index[k]["ranks"])
        matched = len(local_keys_by_category[rank])
        coverage[rank] = {"local_names_matched": matched, "game_unique_names": total,
                          "missing": total - matched}

    weakness_mismatches = []
    for detail in details:
        entry = game_index.get(detail["key"])
        if not entry or not detail["has_weakness_row"]:
            continue
        expected = {WEAKNESS_CN[w] for r in entry["records"]
                    for w in r.get("StanceWeakList") or [] if w in WEAKNESS_CN}
        actual = parse_local_weakness(ROOT / detail["path"])
        if expected and actual and expected != actual:
            weakness_mismatches.append({"category": detail["category"], "name": detail["name"],
                                        "local": sorted(actual), "game": sorted(expected)})

    id_missing, id_eligible, id_blocked = [], [], []
    for detail in details:
        if detail["numeric_id"] is not None:
            continue
        detail["game_entry"] = game_index.get(detail["key"])
        id_missing.append(detail)
        entry = detail.get("game_entry")
        reasons = []
        if not entry:
            reasons.append("游戏数据中无同名记录")
        else:
            if len(entry["base_ids"]) != 1:
                reasons.append("基础记录（MonsterID==MonsterTemplateID）数量为 %d，不是 1：%s"
                               % (len(entry["base_ids"]), entry["base_ids"]))
            if entry["ranks"] != [detail["category"]]:
                reasons.append("游戏 Rank 映射为 %s，与所在目录「%s」不一致"
                               % (entry["ranks"] or ["未知"], detail["category"]))
        if reasons:
            id_blocked.append({"category": detail["category"], "name": detail["name"],
                               "reasons": reasons,
                               "base_ids": entry["base_ids"] if entry else [],
                               "game_ranks": entry["ranks"] if entry else [],
                               "weaknesses": sorted({w for r in entry["records"]
                                                     for w in r.get("StanceWeakList") or []})
                               if entry else []})
        else:
            id_eligible.append({"category": detail["category"], "name": detail["name"],
                               "base_id": entry["base_ids"][0],
                               "game_ranks": entry["ranks"],
                               "weaknesses": sorted({w for r in entry["records"]
                                                     for w in r.get("StanceWeakList") or []})})

    missing_weakness = [{"category": d["category"], "name": d["name"],
                         "weaknesses_en": sorted({w for r in game_index[d["key"]]["records"]
                                                  for w in r.get("StanceWeakList") or []})
                         if d["key"] in game_index else []}
                        for d in details if not d["has_weakness_row"]]

    return {
        "local": {
            "source": source_label,
            "detail_files": len(details),
            "by_category": {c: local_by_category.get(c, 0) for c in CATEGORIES},
            "normalised_matches": sum(1 for d in details if "game_ranks" in d),
            "exact_name_matches": exact_matches,
            "normalisation_only": normalisation_only,
            "type_conflicts": conflicts,
            "pages_missing_weakness": missing_weakness,
            "weakness_mismatches": weakness_mismatches,
        },
        "coverage": coverage,
        "game": {
            "monster_config_records": len(monsters),
            "monster_templates": len(templates),
            "rank_counts_of_templates": dict(sorted(
                collections.Counter(t.get("Rank") for t in templates).items())),
            "unique_names": len(game_index),
            "name_rank_pairs": sum(len(e["ranks"]) for e in game_index.values()),
            "rank_counts_by_name": dict(rank_counts),
            "variant_names": {k: v for k, v in variant_counts.items()},
            "unresolved_name_records": unresolved,
            "names_with_multiple_ranks": sorted(
                ({"name": e["display"], "ranks": e["ranks"]} for e in game_index.values()
                 if len(e["ranks"]) > 1), key=lambda x: x["name"]),
            "names_with_multiple_base_ids": sorted(
                ({"name": e["display"], "base_ids": e["base_ids"]} for e in game_index.values()
                 if len(e["base_ids"]) > 1), key=lambda x: x["name"]),
            "uncovered_names_by_type": {k: sorted(v) for k, v in uncovered.items()},
        },
        "entity_ids": {
            "pages_with_numeric_id": sum(1 for d in details if d["numeric_id"] is not None),
            "pages_without_numeric_id": len(id_missing),
            "eligible": id_eligible,
            "ineligible": id_blocked,
        },
        "data_root_version_note": (
            "第三方 StarRailData 转储：包内没有版本文件，只能称「含 4.7 内容的第三方转储，"
            "版本号未标注」；非官方来源，字段准确性未与游戏内逐条比对。"),
    }


def human_summary(report):
    game = report["game"]
    local = report["local"]
    print("== 本地第三方游戏数据转储交叉核验（非官方来源；版本号未标注）==")
    print("MonsterConfig 记录 %d；MonsterTemplateConfig 模板 %d；唯一名称（归一化后）%d；"
          "名称-类型对 %d"
          % (game["monster_config_records"], game["monster_templates"],
             game["unique_names"], game["name_rank_pairs"]))
    print("模板 Rank 分布：", "，".join(f"{k}={v}" for k, v in game["rank_counts_of_templates"].items()))
    print("名称口径分类（名称可属多个类型，故合计可大于唯一名称数）：",
          "，".join(f"{k} {v}" for k, v in game["rank_counts_by_name"].items()))
    print("变体名称（含（完整）（幻象）（污染）（错误））：",
          "，".join(f"{k} {v}" for k, v in game["variant_names"].items()) or "无")
    print("未解析名称的记录：%d；多类型名称：%d；多基础 ID 名称：%d"
          % (len(game["unresolved_name_records"]), len(game["names_with_multiple_ranks"]),
             len(game["names_with_multiple_base_ids"])))
    print()
    print("本地详情（%s）：%d 篇（%s）" % (local["source"], local["detail_files"],
          "，".join(f"{k} {v}" for k, v in local["by_category"].items())))
    print("归一化后同名 %d（其中名称逐字相同 %d，仅写法/分隔符不同 %d）"
          % (local["normalised_matches"], local["exact_name_matches"],
             len(local["normalisation_only"])))
    print("覆盖（本库唯一名 / 游戏唯一名）：", "，".join(
        f"{k} {v['local_names_matched']}/{v['game_unique_names']}"
        for k, v in report["coverage"].items()))
    print()
    print("分类冲突：%d" % len(local["type_conflicts"]))
    for conflict in local["type_conflicts"]:
        print("  ! %s/%s → 游戏 Rank 映射 %s" % (conflict["category"], conflict["name"],
                                                conflict["game_ranks"]))
    print("缺弱点行页面：%d（%s）" % (len(local["pages_missing_weakness"]),
          "、".join(x["name"] for x in local["pages_missing_weakness"]) or "无"))
    ids = report["entity_ids"]
    print("数字实体ID：已有 %d 篇；缺 %d 篇（满足补 ID 条件 %d，不满足 %d）"
          % (ids["pages_with_numeric_id"], ids["pages_without_numeric_id"],
             len(ids["eligible"]), len(ids["ineligible"])))
    for item in ids["ineligible"]:
        print("  - %s/%s：%s" % (item["category"], item["name"], "；".join(item["reasons"])))
    print()
    print("未覆盖名称数（按类型，含变体名）：", "，".join(
        f"{k} {len(v)}" for k, v in game["uncovered_names_by_type"].items()))
    print("口径提示：%s" % report["data_root_version_note"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-root", default=DEFAULT_DATA_ROOT,
                        help="第三方游戏数据转储根目录（默认 %(default)s，相对仓库根）")
    parser.add_argument("--json", action="store_true", help="只向标准输出打印 JSON")
    parser.add_argument("--json-out", metavar="PATH", help="把 JSON 报告写入该文件")
    parser.add_argument("--include-untracked", action="store_true",
                        help="改用工作区扫描（含尚未入库的详情），默认为 git 跟踪口径")
    args = parser.parse_args(argv)

    data_root = Path(args.data_root)
    if not data_root.is_absolute():
        data_root = (ROOT / data_root)
    if not data_root.is_dir():
        raise SystemExit(f"[error] 数据目录不存在：{data_root}\n"
                         "本脚本不下载数据；请把第三方转储放在该路径或传 --data-root。")
    for required in ("TextMap/TextMapCHS.json", "ExcelOutput/MonsterConfig.json",
                     "ExcelOutput/MonsterTemplateConfig.json"):
        if not (data_root / required).is_file():
            raise SystemExit(f"[error] 数据目录缺少 {required}：{data_root}")

    textmap, monsters, templates = load_game_data(data_root)
    game_index, unresolved, _ = build_name_index(textmap, monsters, templates)

    if args.include_untracked:
        paths, source_label = worktree_detail_paths(), "工作区扫描（含未入库文件）"
    else:
        paths, source_label = tracked_detail_paths(), "git 跟踪文件"
    details = collect_details(paths)
    report = {
        "generated_for": "2026-11-28",
        "data_root": str(data_root),
        "local": {},
        "coverage": {},
        "game": {},
        "entity_ids": {},
        "data_root_version_note": "",
    }
    report.update(analyse(game_index, unresolved, monsters, templates, details, source_label))
    report["game"]["textmap_entries"] = len(textmap)

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"JSON 报告已写入 {out}", file=sys.stderr)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        human_summary(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
