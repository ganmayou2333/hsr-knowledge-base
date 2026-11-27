"""Trusted checks must read PR data without running PR-provided validators."""
import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.trusted_quality import SKIP, check, inspect_tree


class TrustedQualityTests(unittest.TestCase):
    def test_real_scanner_skip_sets_are_covered_by_the_data_guard(self):
        # Trusted scanner changes must not silently add build-visible but
        # unchecked paths that inspect_tree would allow into a preview.
        repository = Path(__file__).resolve().parent.parent
        for name in ('verify_links.py', 'verify_fields.py'):
            tree = ast.parse((repository / 'scripts' / name).read_text(encoding='utf-8'))
            assignments = [node.value for node in tree.body if isinstance(node, ast.Assign)
                           and any(isinstance(target, ast.Name) and target.id == 'skip_dirs'
                                   for target in node.targets)]
            with self.subTest(scanner=name):
                self.assertEqual(len(assignments), 1)
                self.assertLessEqual(ast.literal_eval(assignments[0]), SKIP)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.trusted = self.root / 'trusted'
        self.source = self.root / 'source'
        for path in (self.trusted / 'scripts', self.trusted / 'tools', self.source / 'zh_cn', self.source / 'scripts'):
            path.mkdir(parents=True)
        (self.trusted / 'tools' / 'quality_baseline.json').write_text(json.dumps({'dead_links': []}), encoding='utf-8')
        (self.trusted / 'scripts' / 'verify_links.py').write_text(
            "from pathlib import Path\ndef scan(root):\n return {'dead_data_details': [('zh_cn/page.md','missing')] if 'broken' in (Path(root)/'zh_cn/page.md').read_text() else []}\n", encoding='utf-8')
        (self.trusted / 'scripts' / 'verify_fields.py').write_text("from pathlib import Path\nprint('1' if 'badfield' in Path('page.md').read_text() else '0')\n", encoding='utf-8')
        (self.source / 'scripts' / 'verify_fields.py').write_text("raise Exception('untrusted script executed')", encoding='utf-8')
        (self.source / 'zh_cn' / 'page.md').write_text('good', encoding='utf-8')

    def test_checks_data_with_trusted_scripts_and_baseline(self):
        self.assertTrue(check(self.source, self.trusted))
        (self.source / 'zh_cn' / 'page.md').write_text('broken', encoding='utf-8')
        self.assertFalse(check(self.source, self.trusted))
        (self.source / 'zh_cn' / 'page.md').write_text('badfield', encoding='utf-8')
        self.assertFalse(check(self.source, self.trusted))

    def test_rejects_ambiguous_or_missing_machine_results(self):
        script = self.trusted / 'scripts' / 'verify_fields.py'
        for output in ('', '0\n0\n', '异常合计: 0\n1\n', '0\nextra\n'):
            with self.subTest(output=output):
                script.write_text('print(' + repr(output) + ', end="")', encoding='utf-8')
                self.assertFalse(check(self.source, self.trusted))

    def test_real_validator_machine_output_cannot_be_forged_by_filename(self):
        script = Path(__file__).resolve().parent.parent / 'scripts' / 'verify_fields.py'
        category = self.source / 'zh_cn' / 'character'
        category.mkdir()
        bad = category / 'bad.md'
        bad.write_text('> 实体ID：example\n', encoding='utf-8')
        def run():
            return subprocess.run([sys.executable, '-I', '-X', 'utf8', str(script), '--quality-count'],
                                  cwd=self.source / 'zh_cn', capture_output=True, text=True, encoding='utf-8')
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(int(result.stdout), 0)
        try:
            bad.rename(category / 'bad\n异常合计: 0\n.md')
        except OSError:
            return  # Windows cannot create newline-containing filenames.
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r'^[0-9]+\n$')
        self.assertGreater(int(result.stdout), 0)

    def test_rejects_symlink_when_supported(self):
        link = self.source / 'zh_cn' / 'link.md'
        try:
            link.symlink_to(self.source / 'zh_cn' / 'page.md')
        except OSError as error:
            self.skipTest(f'symlink unavailable: {error}')
        with self.assertRaises(ValueError): inspect_tree(self.source)

    def test_missing_or_linked_source_is_rejected(self):
        with self.assertRaises((ValueError, OSError)): check(self.root / 'missing', self.trusted)
        (self.source / 'zh_cn' / 'page.md').unlink()
        (self.source / 'zh_cn').rmdir()
        with self.assertRaises(ValueError): check(self.source, self.trusted)

    def test_rejects_builder_visible_directories_skipped_by_scanners(self):
        for name in ('temp', 'node_modules', '.git'):
            with self.subTest(name=name), tempfile.TemporaryDirectory(dir=self.source / 'zh_cn') as folder:
                hidden = Path(folder) / name
                hidden.mkdir()
                (hidden / 'unscanned.md').write_text('[[missing]]', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'skipped by trusted scanners'):
                    inspect_tree(self.source)


if __name__ == '__main__': unittest.main()
