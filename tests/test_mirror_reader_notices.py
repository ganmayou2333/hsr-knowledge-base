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
    def test_event_unknown_sources_are_not_declared_unpublished(self):
        forbidden = {
            'ja_jp': ('日本語版は未公開', '日本語版が未公開', '日本語版の公式情報が未公開', 'にのみ掲載されており'),
            'ko_kr': ('한국어판은 미공개', '한국어판이 미공개', '한국어판 공식 정보가 미공개', '에만 게재되어 있고'),
        }
        for language, phrases in forbidden.items():
            pages = list((ROOT / language / 'events').rglob('*.md'))
            self.assertGreater(len(pages), 0)
            for path in pages:
                text = path.read_text(encoding='utf-8')
                for phrase in phrases:
                    with self.subTest(path=str(path.relative_to(ROOT)), phrase=phrase):
                        self.assertNotIn(phrase, text)

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
