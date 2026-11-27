"""Regression gate for visible source notices on high-priority mirrors.

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
    def test_high_priority_pages_have_localized_header_notice(self):
        # Unmarked pages may be partial official extracts, not official translations.
        # Require a visible notice without inferring a source classification.
        for language, notice in NOTICES.items():
            for category in CATEGORIES:
                pages = list((ROOT / language / category).rglob('*.md'))
                self.assertTrue(pages, (language, category))
                for path in pages:
                    header = path.read_text(encoding='utf-8').split('\n---', 1)[0]
                    with self.subTest(path=str(path.relative_to(ROOT))):
                        self.assertIn(notice, header)

    def test_zh_tw_event_names_and_source_description(self):
        root = ROOT / 'zh_tw' / 'events' / '版本活动'
        checks = {
            '劇場版絨絨號：歡鬧廚房.md': ('模糊QR寇', '模糊二維馬'),
            '奇庫尋遺.md': ('黑塔太空站', '黑塔空間站'),
            '寰宇美學•幻樂秀場.md': ('服裝邀請函', '時裝邀請函'),
            '萬象和鳴.md': ('服裝邀請函', '時裝邀請函'),
        }
        for name, (expected, wrong) in checks.items():
            text = (root / name).read_text(encoding='utf-8')
            with self.subTest(name=name):
                self.assertIn(expected, text)
                self.assertNotIn(wrong, text)
        gifts = (root / '開場好禮先抱走.md').read_text(encoding='utf-8')
        self.assertIn('非逐字原文', gifts)
        self.assertNotIn('官方原文照錄', gifts)

    def test_event_unknown_sources_are_not_declared_unpublished(self):
        forbidden = {
            'ja_jp': ('日本語版は未公開', '日本語版が未公開', '日本語版の公式情報が未公開', 'にのみ掲載されており'),
            'ko_kr': ('한국어판은 미공개', '한국어판이 미공개', '한국어판 공식 정보가 미공개', '에만 게재되어 있고'),
            'zh_tw': ('無官方繁中版 →',),
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
