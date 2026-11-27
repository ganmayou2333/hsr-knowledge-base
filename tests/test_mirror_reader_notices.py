"""Regression gate for visible source notices on marked, high-priority mirrors.

This checks presentation, not translation quality, source authenticity or synchronization.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("character", "lightcone", "relic")
NOTICES = {
    "en_us": "> Reader note:",
    "zh_tw": "> 閱讀提示：",
    "ja_jp": "> 閲覧上の注意：",
    "ko_kr": "> 읽기 안내:",
}


class MirrorReaderNoticeTests(unittest.TestCase):
    def test_nonofficial_high_priority_pages_have_notice_in_header(self):
        for language, notice in NOTICES.items():
            for category in CATEGORIES:
                directory = ROOT / language / category
                self.assertTrue(directory.is_dir(), str(directory))
                marked = 0
                for path in directory.rglob("*.md"):
                    text = path.read_text(encoding="utf-8")
                    # Only the opening metadata block is a conspicuous reader entry.
                    header = text.split("\n---", 1)[0]
                    if "> 本地化来源：非官方" not in text[:8192]:
                        continue
                    marked += 1
                    with self.subTest(path=str(path.relative_to(ROOT))):
                        self.assertIn("> 本地化来源：非官方", header)
                        self.assertIn(notice, header)
                self.assertGreater(marked, 0, str(directory))


if __name__ == "__main__":
    unittest.main()
