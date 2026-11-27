"""The regular quality gate must not interpret untrusted report text as success."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import check_quality


class QualityGateTests(unittest.TestCase):
    def test_only_one_machine_count_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'tools').mkdir()
            (root / 'tools' / 'quality_baseline.json').write_text(
                json.dumps({'dead_links': []}), encoding='utf-8')
            for output, code, expected in (
                ('0\n', 0, 0), ('1\n', 0, 1), ('', 0, 1),
                ('0\n1\n', 0, 1), ('异常合计: 0\n1\n', 0, 1), ('0\n', 1, 1),
            ):
                with self.subTest(output=output, code=code), \
                     patch.object(check_quality, 'ROOT', root), \
                     patch.object(check_quality.verify_links, 'scan', return_value={'dead_data_details': []}), \
                     patch.object(check_quality.subprocess, 'run',
                                  return_value=subprocess.CompletedProcess([], code, output, '')) as run:
                    self.assertEqual(check_quality.main(), expected)
                    self.assertIn('--quality-count', run.call_args_list[0].args[0])
                    self.assertEqual(run.call_count, 1 if expected == 0 else 2)


if __name__ == '__main__':
    unittest.main()
