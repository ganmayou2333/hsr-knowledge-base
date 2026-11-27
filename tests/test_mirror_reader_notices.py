"""Regression gate for visible source notices on high-priority mirrors.

This checks presentation, not translation quality, source authenticity or synchronization.
"""
from pathlib import Path
import re
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
    def test_missing_local_provenance_paths_are_explicitly_qualified(self):
        # Historical paths are evidence, not a guarantee that the current
        # baseline was the original input. Do not silently rewrite them.
        pattern = re.compile(r'^> 本地化来源：非官方（.*?来源：(zh_cn/[^；）]+)', re.M)
        notice = {'en_us': 'Historical source path:', 'zh_tw': '來源路徑提示',
                  'ja_jp': '過去の参照パス:', 'ko_kr': '과거 출처 경로:'}
        for language in NOTICES:
            for category in (*CATEGORIES, 'events'):
                for path in (ROOT / language / category).rglob('*.md'):
                    text = path.read_text(encoding='utf-8')
                    match = pattern.search(text)
                    if not match or (ROOT / match.group(1)).is_file():
                        continue
                    with self.subTest(path=str(path.relative_to(ROOT))):
                        self.assertIn(notice[language], text)
                        if language == 'zh_tw':
                            self.assertIn('當時實際輸入尚待核實', text)
                            self.assertIn('不能據此認定歷史輸入或逐欄同步', text)

    def test_zh_tw_47_historical_source_paths_are_qualified(self):
        pairs = {
            '劇場版絨絨號：歡鬧廚房': '剧场版绒绒号：欢闹厨房',
            '奇庫尋遺': '奇库寻遗', '開場好禮先抱走': '开场好礼先抱走',
            '寰宇美學•幻樂秀場': '寰宇美学•幻乐秀场',
            '星際和平盛典：成名之路': '星际和平盛典：成名之路',
            '萬象和鳴': '万象和鸣',
        }
        for translated, baseline in pairs.items():
            with self.subTest(page=translated):
                text = (ROOT / 'zh_tw/events/版本活动' / (translated + '.md')).read_text(encoding='utf-8')
                self.assertIn('> 本地化来源：非官方', text)
                self.assertIn('當時實際輸入尚待核實', text)
                self.assertIn(f'[[zh_cn/events/版本活动/{baseline}|{baseline}]]', text)
                self.assertTrue((ROOT / 'zh_cn/events/版本活动' / (baseline + '.md')).is_file())

    def test_event_id_does_not_claim_official_nonpublication(self):
        # A missing ID in our sources does not establish that no official ID exists.
        for language in ('zh_cn', *NOTICES):
            for path in (ROOT / language / 'events').rglob('*.md'):
                text = path.read_text(encoding='utf-8')
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertNotRegex(text, r'实体ID[：:]\s*(?:无（官方未公开）|無（官方未公開）)')

    def test_event_pages_have_localized_header_notice(self):
        notices = {'en_us': '> Reading note:', 'zh_tw': '> 閱讀提示：',
                   'ja_jp': '> 閲覧上の注意：', 'ko_kr': '> 열람 안내:'}
        for language, notice in notices.items():
            pages = list((ROOT / language / 'events').rglob('*.md'))
            self.assertTrue(pages, language)
            for path in pages:
                header = path.read_text(encoding='utf-8').split('\n---', 1)[0]
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertIn(notice, header)

    def test_zh_tw_event_index_tracks_baseline_targets(self):
        # This checks the list, not the translation or each event's facts.
        relative = Path('events/版本活动/版本活动.md')
        pattern = r'\[\[zh_cn/events/版本活动/([^|\\]+)\\?\|'
        baseline = (ROOT / 'zh_cn' / relative).read_text(encoding='utf-8')
        mirror = (ROOT / 'zh_tw' / relative).read_text(encoding='utf-8')
        expected = re.findall(pattern, baseline)
        actual = re.findall(pattern, mirror)
        self.assertTrue(expected)
        self.assertEqual(expected, actual)

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

    def test_zh_tw_46_event_announcement_scope(self):
        root = ROOT / 'zh_tw' / 'events' / '版本活动'
        pet = (root / '星际幻宠乐园.md').read_text(encoding='utf-8')
        self.assertIn('更新說明的樂園條目未列', pet)
        self.assertIn('隨身寵物小屋', pet)
        self.assertNotIn('隨寵小屋', pet)
        show = (root / '星际和平盛典_一镜到底.md').read_text(encoding='utf-8')
        self.assertIn('2026/10/21 12:00（伺服器時間）', show)
        story = (root / '爱，幽灵与机器人.md').read_text(encoding='utf-8')
        self.assertIn('愛、幽靈與機器人', story)

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
