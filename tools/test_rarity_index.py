"""Check the displayed counts of linked character and Light Cone rarity indexes."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'\[\[(data/zh_cn/(?:character|lightcone)/[^|\]]+)\|[^\]]+\]\]（(\d+)）')
ENTRY = re.compile(r'^- ★+ \[\[', re.MULTILINE)


class RarityIndexTests(unittest.TestCase):
    def test_parent_link_counts_match_rarity_index_entries(self):
        checked = 0
        for category in ('character', 'lightcone'):
            for index in (ROOT / 'data' / 'zh_cn' / category).glob('*/*.md'):
                if index.stem != index.parent.name:
                    continue
                for target, count in LINK.findall(index.read_text(encoding='utf-8')):
                    path = ROOT / (target + '.md')
                    with self.subTest(index=index, target=target):
                        self.assertTrue(path.is_file(), path)
                        entries = ENTRY.findall(path.read_text(encoding='utf-8'))
                        self.assertEqual(int(count), len(entries))
                    checked += 1
        self.assertGreaterEqual(checked, 18, 'Rarity indexes were not discovered')


if __name__ == '__main__':
    unittest.main()
