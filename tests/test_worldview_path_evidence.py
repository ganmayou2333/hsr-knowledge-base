"""Guard against previously identified identity and character-path mixups.

These checks do not establish that the rest of the worldview is correct.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WorldviewPathEvidenceTests(unittest.TestCase):
    def test_unsynchronized_worldview_mirrors_warn_readers(self):
        labels = {'en_us': '> Reader warning:', 'zh_tw': '> 閱讀警告：',
                  'ja_jp': '> 閲覧上の注意：', 'ko_kr': '> 열람 주의:'}
        for lang, label in labels.items():
            for name in ('星神与命途.md', '术语词典.md'):
                with self.subTest(language=lang, name=name):
                    text = (ROOT / 'data' / lang / 'worldview' / name).read_text(encoding='utf-8')
                    self.assertIn(label, '\n'.join(text.splitlines()[:8]))
                    self.assertIn('本地化来源：非官方', text)

    def test_previous_confident_identity_mixups_are_not_reintroduced(self):
        for name in ('星神与命途.md', '术语词典.md'):
            text = (ROOT / 'data/zh_cn/worldview' / name).read_text(encoding='utf-8')
            with self.subTest(name=name):
                self.assertNotIn('同谐星神伊德莉拉', text)
                self.assertNotIn('虚无奥博洛斯', text)
        text = (ROOT / 'data/zh_cn/worldview/星神与命途.md').read_text(encoding='utf-8')
        self.assertNotIn('岚（巡猎之星神 / 帝弓七天将）', text)
        self.assertIn('其余内容尚未逐条核验', text)

    def test_character_examples_match_the_fields_checked(self):
        text = (ROOT / 'data/zh_cn/worldview/星神与命途.md').read_text(encoding='utf-8')
        def section(start, end):
            return text.split(start, 1)[1].split(end, 1)[0]
        self.assertNotIn('阿格莱雅', section('### 6. 丰饶', '### 7. 巡猎'))
        self.assertNotIn('黄泉', section('### 7. 巡猎', '### 8. 记忆'))
        self.assertNotIn('大黑塔', section('### 8. 记忆', '### 9. 欢愉'))
        self.assertIn('阿格莱雅', section('### 8. 记忆', '### 9. 欢愉'))


if __name__ == '__main__':
    unittest.main()
