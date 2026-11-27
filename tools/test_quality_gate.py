"""Exercise the CI gate's treatment of existing and new data problems."""
import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tools import check_quality


class QualityGateTests(unittest.TestCase):
    def run_gate(self, links, field_output="0\n"):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "tools").mkdir()
            (root / "tools" / "quality_baseline.json").write_text(
                json.dumps({"dead_links": [["zh_cn/a.md", "missing"]]}), encoding="utf-8"
            )
            result = SimpleNamespace(returncode=0, stdout=field_output, stderr="")
            with patch.object(check_quality, "ROOT", root), \
                 patch.object(check_quality.verify_links, "scan", return_value={"dead_data_details": links}), \
                 patch.object(check_quality.subprocess, "run", return_value=result), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return check_quality.main()

    def test_existing_link_is_allowed_but_new_link_fails(self):
        existing = [("zh_cn/a.md", "missing")]
        self.assertEqual(self.run_gate(existing), 0)
        self.assertEqual(self.run_gate(existing + [("zh_cn/b.md", "other")]), 1)

    def test_field_errors_and_unrecognized_output_fail(self):
        self.assertEqual(self.run_gate([], "1\n"), 1)
        self.assertEqual(self.run_gate([], "unexpected output\n"), 1)
        self.assertEqual(self.run_gate([], "异常合计: 0\n1\n"), 1)

    def test_link_checker_reports_a_data_link_failure(self):
        script = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "verify_links.py"
        with tempfile.TemporaryDirectory() as tmp:
            data = pathlib.Path(tmp) / "zh_cn"
            data.mkdir()
            (data / "entry.md").write_text("[[missing]]", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script)], cwd=tmp, capture_output=True,
                text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("RESULT: FAIL", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
