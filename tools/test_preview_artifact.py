"""Verify that extracting PR-produced ZIPs cannot escape the staging directory."""
import stat
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.preview_artifact import InvalidPreviewArtifact, archive_path, extract_preview_zip


class PreviewArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.zip = self.root / "site.zip"
        self.dest = self.root / "site"

    def make_zip(self, entries):
        with zipfile.ZipFile(self.zip, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries:
                archive.writestr(name, data)

    def reject(self, entries):
        self.make_zip(entries)
        with self.assertRaises((InvalidPreviewArtifact, zipfile.BadZipFile)):
            extract_preview_zip(self.zip, self.dest)
        self.assertFalse(self.dest.exists())
        self.assertFalse(list(self.root.glob('.preview-stage-*')))

    def test_extracts_static_files_and_preserves_bytes(self):
        self.make_zip([("index.html", "<!doctype html>"), ("pages/页面.html", "正文"), ("assets/a.js", "1+1")])
        extract_preview_zip(self.zip, self.dest)
        self.assertEqual((self.dest / "pages" / "页面.html").read_text(encoding="utf-8"), "正文")
        self.assertEqual((self.dest / "assets" / "a.js").read_text(encoding="utf-8"), "1+1")

    def test_rejects_paths_that_escape_or_are_ambiguous(self):
        with self.assertRaises(InvalidPreviewArtifact):
            archive_path("a\\outside")
        for path in ["../outside", "/outside", "C:/outside", "a/../outside",
                     "a//outside", "a/NUL.txt", "a/CON .txt", "a/LPT¹.log", "a/CONIN$",
                     "a/space. ", "a/\x01bad", "a/<bad>", "a/file?.js", "a/" + "x" * 256]:
            with self.subTest(path=path):
                self.reject([("index.html", "home"), (path, "bad")])
                self.assertFalse((self.root / "outside").exists())

        # ZipFile.writestr normalizes native Windows separators in a string
        # filename, so construct the malicious central-directory name directly.
        backslash = zipfile.ZipInfo("placeholder")
        backslash.filename = "a\\outside"
        self.reject([("index.html", "home"), (backslash, "bad")])

    def test_rejects_aliases_conflicts_and_missing_index(self):
        for entries in [
            [("index.html", "a"), ("INDEX.HTML", "b")],
            [("index.html", "a"), ("A/x", "b"), ("a/y", "c")],
            [("index.html", "a"), ("page", "b"), ("page/x", "c")],
            [("INDEX.HTML", "a")],
        ]:
            with self.subTest(entries=entries):
                self.reject(entries)

    def test_rejects_symlinks_and_oversized_files(self):
        link = zipfile.ZipInfo("link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.reject([("index.html", "home"), (link, "../../outside")])
        self.make_zip([("index.html", "longer than allowed")])
        with patch("tools.preview_artifact.MAX_FILE_BYTES", 5):
            with self.assertRaises(InvalidPreviewArtifact):
                extract_preview_zip(self.zip, self.dest)
        self.assertFalse(self.dest.exists())

    def test_rejects_aggregate_size_and_entry_count(self):
        entries = [("index.html", "home"), ("assets/a.js", "script")]
        self.make_zip(entries)
        for name, limit in [("MAX_ARCHIVE_BYTES", 1), ("MAX_TOTAL_BYTES", 5), ("MAX_FILES", 1)]:
            with self.subTest(limit=name), patch("tools.preview_artifact." + name, limit):
                with self.assertRaises(InvalidPreviewArtifact):
                    extract_preview_zip(self.zip, self.dest)
                self.assertFalse(self.dest.exists())
                self.assertFalse(list(self.root.glob('.preview-stage-*')))

    def test_rejects_unsupported_compression_before_extracting(self):
        for method in (zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA):
            with self.subTest(method=method):
                with zipfile.ZipFile(self.zip, 'w', compression=method) as archive:
                    archive.writestr('index.html', 'home')
                with self.assertRaises(InvalidPreviewArtifact):
                    extract_preview_zip(self.zip, self.dest)
                self.assertFalse(self.dest.exists())
                self.assertFalse(list(self.root.glob('.preview-stage-*')))

    def test_rejects_forged_central_directory_count(self):
        self.make_zip([("index.html", "home"), ("a.js", "script")])
        data = bytearray(self.zip.read_bytes())
        end = data.rfind(b"PK\x05\x06")
        self.assertGreaterEqual(end, 0)
        struct.pack_into("<HH", data, end + 8, 1, 1)
        self.zip.write_bytes(data)
        with self.assertRaises(InvalidPreviewArtifact):
            extract_preview_zip(self.zip, self.dest)
        self.assertFalse(self.dest.exists())

    def test_does_not_replace_existing_destination(self):
        self.dest.mkdir()
        (self.dest / "keep").write_text("existing", encoding="utf-8")
        self.make_zip([("index.html", "home")])
        with self.assertRaises(InvalidPreviewArtifact):
            extract_preview_zip(self.zip, self.dest)
        self.assertEqual((self.dest / "keep").read_text(encoding="utf-8"), "existing")


if __name__ == "__main__":
    unittest.main()
