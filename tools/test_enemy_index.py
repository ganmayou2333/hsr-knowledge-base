"""Verify the generated enemy indexes link to every tracked detail page."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "zh_cn" / "enemies"
PAGES = ROOT / "wiki" / "pages" / "enemies"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.active = [dict(attrs).get("href", ""), ""]

    def handle_data(self, data):
        if self.active is not None:
            self.active[1] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.active is not None:
            self.links.append(self.active)
            self.active = None


class EnemyIndexTests(unittest.TestCase):
    def assert_page_links_to(self, page, label, destination):
        parser = Links()
        parser.feed(page.read_text(encoding="utf-8"))
        actual = [
            (page.parent / unquote(urlsplit(href).path)).resolve()
            for href, text in parser.links if text.strip() == label
        ]
        self.assertIn(destination.resolve(), actual, (page, label, actual))
        self.assertTrue(destination.is_file(), destination)

    def test_indexes_link_to_each_detail_by_name_and_numeric_id(self):
        main = PAGES / "敌人.html"
        self.assertTrue(main.is_file(), "Run python wiki/build_wiki.py first")
        details = 0
        for category in ("普通敌人", "精英敌人", "首领", "周本BOSS"):
            category_page = PAGES / category / (category + ".html")
            self.assert_page_links_to(main, category + "索引", category_page)
            for source in (SOURCE / category).glob("*.md"):
                if source.stem == category:
                    continue
                text = source.read_text(encoding="utf-8")
                match = re.search(r"^>\s*实体ID[：:]\s*([0-9]+)\s*$", text, re.M)
                target = PAGES / category / ((match.group(1) if match else source.stem) + ".html")
                for page in (main, category_page):
                    with self.subTest(page=page, source=source):
                        self.assert_page_links_to(page, source.stem, target)
                details += 1
        self.assertGreater(details, 0, "No enemy detail pages were tested")


if __name__ == "__main__":
    unittest.main()
