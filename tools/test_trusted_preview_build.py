import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.preview_artifact import InvalidPreviewArtifact
from tools.trusted_preview_build import build


class TrustedPreviewBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trusted = self.root / 'trusted'
        self.input = self.root / 'input'
        (self.trusted / 'wiki' / 'assets').mkdir(parents=True)
        (self.input / 'zh_cn').mkdir(parents=True)
        (self.input / 'wiki').mkdir()
        (self.input / 'zh_cn' / 'page.md').write_text('# Untrusted content', encoding='utf8')
        (self.input / 'zh_cn' / 'poison.py').write_text('raise RuntimeError("PR code executed")', encoding='utf8')
        (self.input / 'wiki' / 'build_wiki.py').write_text('raise RuntimeError("PR builder executed")', encoding='utf8')
        (self.trusted / 'wiki' / 'index.html').write_text('trusted shell', encoding='utf8')
        (self.trusted / 'wiki' / 'assets' / 'app.js').write_text('trusted asset', encoding='utf8')
        (self.trusted / 'wiki' / 'build_wiki.py').write_text("""from pathlib import Path
import os
assert not os.environ.get('GH_TOKEN')
root = Path(__file__).resolve().parent.parent
assert not (root / 'zh_cn' / 'poison.py').exists()
for name in ('pages', 'data'):
 (root / 'wiki' / name).mkdir()
(root / 'wiki' / 'pages' / 'page.html').write_text((root / 'zh_cn' / 'page.md').read_text(encoding='utf8'), encoding='utf8')
(root / 'wiki' / 'data' / 'index.json').write_text('{}', encoding='utf8')
""", encoding='utf8')

    def test_build_uses_trusted_code_and_only_pr_markdown(self):
        out = self.root / 'preview.zip'
        with patch.dict(os.environ, {'GH_TOKEN': 'do-not-pass'}):
            build(self.input, self.trusted, out)
        with zipfile.ZipFile(out) as z:
            self.assertIn(b'Untrusted content', z.read('pages/page.html'))
            self.assertEqual(z.read('assets/app.js'), b'trusted asset')
            self.assertNotIn('poison.py', ' '.join(z.namelist()))

    def test_isolated_cli_with_real_trusted_checkout(self):
        import subprocess
        import sys
        script = Path(__file__).resolve().parent / 'trusted_preview_build.py'
        out = self.root / 'cli.zip'
        result = subprocess.run([sys.executable, '-I', str(script), str(self.input), str(out)],
                                capture_output=True, text=True, encoding='utf8', errors='replace')
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(out) as z:
            self.assertIn('pages/page.html', z.namelist())

    def test_refuses_existing_output_and_nested_checkouts(self):
        out = self.root / 'out.zip'
        out.write_bytes(b'existing')
        with self.assertRaises(InvalidPreviewArtifact):
            build(self.input, self.trusted, out)
        self.assertEqual(out.read_bytes(), b'existing')
        with self.assertRaises(InvalidPreviewArtifact):
            build(self.input, self.trusted, self.input / 'out.zip')
        with self.assertRaises(InvalidPreviewArtifact):
            build(self.input, self.input, self.root / 'other.zip')

    def test_size_limit_applies_even_in_skipped_directory(self):
        skipped = self.input / 'zh_cn' / 'temp'
        skipped.mkdir()
        (skipped / 'oversized.md').write_text('x' * 33, encoding='utf8')
        out = self.root / 'out.zip'
        with patch('tools.trusted_preview_build.MAX_MARKDOWN_FILE', 32):
            with self.assertRaises(InvalidPreviewArtifact):
                build(self.input, self.trusted, out)
        self.assertFalse(out.exists())

    def test_failed_builder_leaves_no_artifact(self):
        (self.trusted / 'wiki' / 'build_wiki.py').write_text('raise RuntimeError("failure")', encoding='utf8')
        out = self.root / 'out.zip'
        import subprocess
        with self.assertRaises(subprocess.CalledProcessError):
            build(self.input, self.trusted, out)
        self.assertFalse(out.exists())

    def test_rejects_symlinked_markdown(self):
        try:
            (self.input / 'zh_cn' / 'link.md').symlink_to(self.input / 'zh_cn' / 'page.md')
        except OSError as error:
            self.skipTest(str(error))
        with self.assertRaises(ValueError):
            build(self.input, self.trusted, self.root / 'out.zip')
        self.assertFalse((self.root / 'out.zip').exists())


if __name__ == '__main__':
    unittest.main()
