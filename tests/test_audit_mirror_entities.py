import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_mirror_entities as audit


class EntityAuditTest(unittest.TestCase):
    def test_missing_duplicate_and_non_numeric_ids_are_separate(self):
        files = {
            "zh_cn/character/a.md": "> 实体ID：1\n",
            "zh_cn/character/b.md": "> 实体ID：2\n",
            "zh_cn/character/c.md": "> 实体ID：3\n",
            "zh_cn/character/index.md": "# index\n",
            "en_us/character/a.md": "> 实体ID：1\n",
            "en_us/character/duplicate.md": "> 实体ID：1\n",
            "en_us/character/placeholder.md": "> 实体ID：无（官方未公开）\n",
            "en_us/character/partial.md": "> 实体ID：3\n> 状态：部分收录；内容待核验\n",
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path, content in files.items():
                target = root / "data" / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            raw = b"\0".join(("data/" + path).encode("utf-8") for path in files) + b"\0"
            output = io.StringIO()
            with patch.object(audit, "ROOT", root), patch.object(audit.subprocess, "check_output", return_value=raw), patch("sys.argv", ["audit", "--json"]), contextlib.redirect_stdout(output):
                audit.main()
        result = next(row for row in json.loads(output.getvalue()) if row["category"] == "character" and row["language"] == "en_us")
        self.assertEqual(result["matched_unique"], 1)
        self.assertEqual(result["matched_candidates"], {
            "3": {"base": "zh_cn/character/c.md", "mirror": "en_us/character/partial.md"}
        })
        self.assertEqual(result["matched_marked_partial"], {"3": "en_us/character/partial.md"})
        self.assertEqual(set(result["missing"]), {"2"})
        self.assertEqual(set(result["mirror_duplicates"]), {"1"})
        self.assertEqual(len(result["mirror_nonnumeric"]), 1)
        self.assertEqual(result["base_no_id"], ["zh_cn/character/index.md"])


if __name__ == "__main__":
    unittest.main()
