"""回归正文摘要与无脚本目录，运行：python -m unittest tools.test_wiki_search。"""
import unittest
from html.parser import HTMLParser

from wiki.build_wiki import character_panel_html, convert_inline, md_to_html, page_toc, parse_meta, search_summary


class WikiSearchTests(unittest.TestCase):
    def test_community_wiki_is_metadata_not_official_source(self):
        metadata, body = parse_meta('# Sample\n> 米游社社区图鉴：https://bbs.mihoyo.com/sr/wiki/content/584/detail\nBody')
        self.assertIn('米游社社区图鉴', metadata)
        self.assertNotIn('官方Wiki', metadata)
        self.assertNotIn('米游社社区图鉴', body)

    def test_summary_uses_readable_body_not_metadata_or_code(self):
        body = "# 标题\n> 数据来源：示例\n## 故事\n```\n秘密代码\n```\n这是一段[[zh_cn/items/星核|星核]]记录。"
        self.assertEqual(search_summary(body), "这是一段星核记录。")

    def test_summary_is_bounded(self):
        self.assertEqual(len(search_summary("星" * 500)), 240)

    def test_summary_reads_existing_character_references(self):
        self.assertEqual(search_summary('调整&nbsp;-&nbsp;∞<unbreak>11</unbreak> &gt;'),
                         '调整\u00a0-\u00a0∞11 >')

    def test_toc_uses_rendered_heading_ids_and_escapes_labels(self):
        rendered = md_to_html("## 第一章\n正文\n## 第一章\n正文\n## **角色** & 光锥", 1)
        toc = page_toc(rendered)
        self.assertIn('href="#第一章"', toc)
        self.assertIn('href="#第一章-2"', toc)
        self.assertNotIn("<strong>", toc)
        self.assertIn("角色 &amp; 光锥", toc)

    def test_untrusted_text_cannot_create_html_attributes(self):
        class AttributeCollector(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tags = []

            def handle_starttag(self, tag, attrs):
                self.tags.append((tag, dict(attrs)))

        payload = 'x" onmouseover="alert(1)'
        panel = {'paths': [payload], 'elements': [payload], 'items': [{
            'path': payload, 'element': payload, 'h1': payload, 'name': payload,
            'star': 5, 'rarity': '五星', 'url': 'character/test.html',
            'icon': 'assets/icons/avatar/1.png', 'hasIcon': True,
        }]}
        parser = AttributeCollector()
        parser.feed(convert_inline('[link](https://example.test/" onmouseover="alert)', 0))
        parser.feed(character_panel_html(panel, ''))
        self.assertFalse(any('onmouseover' in attrs for _, attrs in parser.tags))
        self.assertTrue(any(tag == 'a' and '" onmouseover="' in attrs.get('href', '')
                            for tag, attrs in parser.tags))
        self.assertTrue(any(tag == 'li' and attrs.get('data-path') == payload
                            for tag, attrs in parser.tags))

    def test_plain_markdown_cannot_emit_raw_html(self):
        class Tags(HTMLParser):
            def __init__(self):
                super().__init__()
                self.names = []

            def handle_starttag(self, tag, attrs):
                self.names.append(tag)

        rendered = md_to_html('<script>alert(1)</script> <img src=x onerror=alert(1)> '
                              '&lt;script&gt; **粗体** <br> `代码`', 1)
        parser = Tags()
        parser.feed(rendered)
        self.assertNotIn('script', parser.names)
        self.assertNotIn('img', parser.names)
        self.assertIn('strong', parser.names)
        self.assertIn('br', parser.names)
        self.assertIn('code', parser.names)
        self.assertIn('&lt;script&gt;', rendered)

    def test_existing_character_references_and_game_markup_render_as_text(self):
        rendered = convert_inline('调整&nbsp;-&nbsp;我选择 &gt;&gt; ∞<unbreak>11</unbreak>便利店 `&gt;`', 0)
        self.assertIn('调整\u00a0-\u00a0我选择 &gt;&gt; ∞11便利店', rendered)
        self.assertIn('<code>&amp;gt;</code>', rendered)
        self.assertNotIn('<unbreak>', rendered)
        link = convert_inline('[A&nbsp;&lt;B&gt;](https://example.test/)', 0)
        self.assertIn('>A\u00a0&lt;B&gt;</a>', link)

    def test_inline_formatting_preserves_ampersands_and_links(self):
        rendered = convert_inline('文字 & **粗体** [链接](https://example.test/?a=1&b=2) `a<b`', 0)
        self.assertIn('文字 &amp; <strong>粗体</strong>', rendered)
        self.assertIn('href="https://example.test/?a=1&amp;b=2"', rendered)
        self.assertIn('<code>a&lt;b</code>', rendered)
        self.assertNotIn('&amp;amp;', rendered)

    def test_toc_omitted_for_short_page(self):
        self.assertEqual(page_toc(md_to_html("## 唯一章节\n正文", 1)), "")


if __name__ == "__main__":
    unittest.main()
