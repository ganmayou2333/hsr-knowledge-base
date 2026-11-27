"""Prevent planned update dates from diverging between timeline sections and table."""
from pathlib import Path
import re
import unittest

TIMELINE = Path(__file__).resolve().parents[1] / "zh_cn/worldview/剧情时间线.md"


class TimelineDatesTests(unittest.TestCase):
    def test_verified_planned_dates_match_overview(self):
        text = TIMELINE.read_text(encoding="utf-8")
        for version in ("4.2", "4.3", "4.4", "4.5", "4.6", "4.7"):
            with self.subTest(version=version):
                heading = re.escape(version)
                section = re.search(rf"(?ms)^### {heading}「[^\n]+\n(.*?)(?=^### |^## |\Z)", text)
                self.assertIsNotNone(section)
                date = re.search(r"\*\*公告计划更新日期\*\*：([0-9]{4}-[0-9]{2}-[0-9]{2})", section.group(1))
                self.assertIsNotNone(date)
                rows = re.findall(rf"(?m)^\| {heading} \|[^\n]+$", text)
                self.assertEqual(len(rows), 1)
                self.assertIn(f"| {date.group(1)}（计划更新日期） |", rows[0])


if __name__ == "__main__":
    unittest.main()
