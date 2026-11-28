#!/usr/bin/env python3
"""Read-only coverage of provenance labels and reader notices on the mirrors.

Counts tracked Markdown files under the four mirror languages for the four
entity categories, and reports how many of them carry the machine-localization
label, a header reader notice and the partial-coverage status. Presence of a
label or notice does not establish source authenticity, completeness or
synchronization with the Chinese baseline.
"""

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en_us", "zh_tw", "ja_jp", "ko_kr")
CATEGORIES = ("character", "lightcone", "relic", "events")
LABEL = "本地化来源：非官方".encode("utf-8")

# Accepted header notices. Event pages use a different English/Korean wording
# from the character/lightcone/relic pages; tests/test_mirror_reader_notices.py
# checks both sets.
NOTICES = {
    "en_us": {"default": "> Reader note:", "events": "> Reading note:"},
    "zh_tw": {"default": "> 閱讀提示：", "events": "> 閱讀提示："},
    "ja_jp": {"default": "> 閲覧上の注意：", "events": "> 閲覧上の注意："},
    "ko_kr": {"default": "> 읽기 안내:", "events": "> 열람 안내:"},
}

ID_LINE = re.compile(r"^>[ \t]*实体ID[ \t]*[:：]", re.MULTILINE)
PARTIAL_LINE = re.compile(r"^>[ \t]*状态[ \t]*[:：][ \t]*部分收录", re.MULTILINE)


def tracked_paths():
    raw = subprocess.check_output(
        ["git", "ls-files", "-z", "--", *[f"data/{lang}/{cat}" for lang in LANGS for cat in CATEGORIES]],
        cwd=ROOT,
    )
    return [b.decode("utf-8")[len("data/"):] for b in raw.split(b"\0") if b.endswith(b".md")]


def notice_for(language, category):
    return NOTICES[language]["events" if category == "events" else "default"]


def main():
    counts = {
        (lang, group, key): 0
        for lang in LANGS
        for group in (*CATEGORIES, "all")
        for key in ("total", "detail", "labeled", "notice", "partial", "labeled_no_notice")
    }
    for path in tracked_paths():
        language, category, _ = path.split("/", 2)
        if language not in LANGS or category not in CATEGORIES:
            continue
        text = (ROOT / "data" / path).read_text(encoding="utf-8-sig")
        with (ROOT / "data" / path).open("rb") as f:
            labeled = LABEL in f.read(8192)
        header = text.split("\n---", 1)[0]
        notice = notice_for(language, category) in header
        detail = bool(ID_LINE.search(text))
        partial = bool(PARTIAL_LINE.search(text))
        for group in (category, "all"):
            counts[language, group, "total"] += 1
            counts[language, group, "detail"] += detail
            counts[language, group, "labeled"] += labeled
            counts[language, group, "notice"] += notice
            counts[language, group, "partial"] += partial
            counts[language, group, "labeled_no_notice"] += labeled and not notice

    print("| 语言 | 类别 | 已跟踪文件 | 含实体ID行 | 非官方标记 | 页首阅读提示 | 部分收录 | 非官方标记但无页首提示 |")
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    for language in LANGS:
        for group in (*CATEGORIES, "all"):
            label = "四类合计" if group == "all" else group
            print(
                f"| {language} | {label} | "
                + " | ".join(
                    str(counts[language, group, key])
                    for key in ("total", "detail", "labeled", "notice", "partial", "labeled_no_notice")
                )
                + " |"
            )


if __name__ == "__main__":
    main()
