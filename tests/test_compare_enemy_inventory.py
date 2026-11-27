import unittest
from scripts.compare_enemy_inventory import compare


class EnemyInventoryTest(unittest.TestCase):
    def test_exact_names_only_and_local_unmatched(self):
        snapshot = {"retrieved_unique": 2, "entries": [
            {"wiki_id": 1, "name": "灯塔"}, {"wiki_id": 2, "name": "重子"}]}
        result = compare(snapshot, ["zh_cn/enemies/敌人.md", "zh_cn/enemies/精英敌人/灯塔.md", "zh_cn/enemies/首领/其他.md"])
        self.assertEqual([x["name"] for x in result["matched"]], ["灯塔"])
        self.assertEqual([x["name"] for x in result["missing"]], ["重子"])
        self.assertEqual(result["local_without_exact_match"], ["其他"])

    def test_similar_punctuation_is_only_a_review_candidate(self):
        snapshot = {"retrieved_unique": 2, "entries": [
            {"wiki_id": 1, "name": "金血忆灵 · 犬形"},
            {"wiki_id": 2, "name": "敌人（错误）"}]}
        result = compare(snapshot, ["zh_cn/enemies/普通敌人/金血忆灵•犬形.md",
                                    "zh_cn/enemies/精英敌人/金血忆灵·犬形.md",
                                    "zh_cn/enemies/精英敌人/敌人.md"])
        self.assertEqual(len(result["matched"]), 0)
        self.assertEqual(len(result["missing"]), 2)
        self.assertEqual(result["possible_aliases"], [{
            "wiki_id": 1, "name": "金血忆灵 · 犬形",
            "local_names": ["金血忆灵·犬形", "金血忆灵•犬形"]}])

    def test_bad_snapshot_fails_closed(self):
        for snapshot in ({"retrieved_unique": 1, "entries": []},
                         {"retrieved_unique": 2, "entries": [{"wiki_id": 1, "name": "甲"}, {"wiki_id": 1, "name": "乙"}]}):
            with self.subTest(snapshot=snapshot), self.assertRaises(ValueError):
                compare(snapshot, [])


if __name__ == "__main__":
    unittest.main()
