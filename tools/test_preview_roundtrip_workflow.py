"""Exercise the actual workflow's ZIP comparison and verification shell step."""
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PreviewRoundtripWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bash = shutil.which("bash")
        if not cls.bash and os.name == "nt":
            git = shutil.which("git")
            if git:
                candidate = Path(git).resolve().parent.parent / "bin" / "bash.exe"
                if candidate.exists():
                    cls.bash = str(candidate)
        if not cls.bash:
            raise unittest.SkipTest("bash is unavailable")
        workflow = (ROOT / ".github/workflows/wiki-quality.yml").read_text(encoding="utf-8")
        block = workflow.split("      - name: Verify downloaded preview input\n", 1)[1]
        block = block.split("        run: |\n", 1)[1].split("      - name:", 1)[0]
        cls.script = "\n".join(line[10:] for line in block.splitlines()) + "\n"

    def check_case(self, kind):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            downloaded = root / "preview-roundtrip"
            downloaded.mkdir()
            original = root / "wiki-preview.zip"
            with zipfile.ZipFile(original, "w") as archive:
                for name in ("index.html", "assets/app.js", "data/titles.js", "pages/a.html", "assets/icons/a.png"):
                    archive.writestr(name, "ok")
            if kind != "missing":
                shutil.copyfile(original, downloaded / original.name)
            if kind == "tampered":
                with (downloaded / original.name).open("ab") as handle:
                    handle.write(b"tampered")
            if kind == "incomplete":
                with zipfile.ZipFile(original, "w") as archive:
                    archive.writestr("index.html", "ok")
                shutil.copyfile(original, downloaded / original.name)
            env = dict(os.environ, RUNNER_TEMP=tmp)
            if os.name == "nt":
                env["RUNNER_TEMP"] = subprocess.check_output(
                    [self.bash, "-c", 'cygpath -u "$1"', "_", tmp], text=True
                ).strip()
            env["PYTHONIOENCODING"] = "utf-8"
            return subprocess.run([self.bash, "-e", "-c", self.script], cwd=ROOT, env=env,
                                  capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_valid_archive_passes(self):
        result = self.check_case("valid")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: preview archive round-trip", result.stdout)

    def test_missing_tampered_and_incomplete_archives_fail(self):
        for kind, expected in (("missing", "No such file"),
                               ("tampered", "cmp:"),
                               ("incomplete", "Preview is missing required files")):
            with self.subTest(kind=kind):
                result = self.check_case(kind)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
