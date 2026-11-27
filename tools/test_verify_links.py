import random
import re
import unittest

from scripts.verify_links import iter_wikilinks


class LinkScannerTests(unittest.TestCase):
    def test_matches_original_regex_on_adversarial_inputs(self):
        rng = random.Random(41)
        examples = ['[[a[[b]]', '[[a]bad[[b]]', '[[]]', '[[[[]]', '[[a]] [[b]]']
        examples += [''.join(rng.choices('[]abc|', k=rng.randrange(100))) for _ in range(5000)]
        for text in examples:
            self.assertEqual(list(iter_wikilinks(text)), re.findall(r'\[\[([^\]]+)\]\]', text), repr(text))

    def test_many_unclosed_openers_do_not_trigger_quadratic_backtracking(self):
        self.assertEqual(list(iter_wikilinks('[[' * 2_000_000)), [])


if __name__ == '__main__':
    unittest.main()
