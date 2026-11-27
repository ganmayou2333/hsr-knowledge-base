"""Extract an untrusted Wiki ZIP into a fresh directory, without executing it.

This only protects the publishing filesystem. Extracted HTML and JavaScript
remain untrusted and must not be served from the production origin or allowed
to control a trusted preview banner. This module does not publish previews.
"""
import os
import re
import shutil
import stat
import struct
import tempfile
import unicodedata
import zipfile
from pathlib import Path


MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
MAX_FILES = 50000
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_PATH_BYTES = 1024
MAX_DIRECTORY_BYTES = 16 * 1024 * 1024
WINDOWS_DEVICE = re.compile(r"^(?:con|prn|aux|nul|conin\$|conout\$|com[1-9¹²³]|lpt[1-9¹²³])(?: *\..*)?$", re.I)


class InvalidPreviewArtifact(ValueError):
    """An archive cannot be safely used as a preview artifact."""


def check_zip_directory(handle, size):
    """Bound central-directory parsing before ZipFile allocates per-entry objects."""
    handle.seek(max(0, size - 65557))
    tail = handle.read()
    position = tail.rfind(b"PK\x05\x06")
    if position < 0 or len(tail) - position < 22:
        raise InvalidPreviewArtifact("ZIP end record is missing")
    _, disk, directory_disk, disk_entries, entries, directory_size, directory_offset, comment_size = struct.unpack_from(
        "<4s4H2LH", tail, position
    )
    end_offset = size - len(tail) + position
    if (position + 22 + comment_size != len(tail) or disk or directory_disk or disk_entries != entries
            or entries == 0xffff or directory_size == 0xffffffff or directory_offset == 0xffffffff
            or entries > MAX_FILES or directory_size > MAX_DIRECTORY_BYTES
            or directory_offset + directory_size != end_offset):
        raise InvalidPreviewArtifact("Unsupported or oversized ZIP directory")
    handle.seek(directory_offset)
    directory = handle.read(directory_size)
    offset = count = 0
    while offset < len(directory):
        if len(directory) - offset < 46 or directory[offset:offset + 4] != b"PK\x01\x02":
            raise InvalidPreviewArtifact("Invalid ZIP directory entry")
        filename_size, extra_size, entry_comment_size = struct.unpack_from("<3H", directory, offset + 28)
        offset += 46 + filename_size + extra_size + entry_comment_size
        count += 1
        if offset > len(directory) or count > MAX_FILES:
            raise InvalidPreviewArtifact("Invalid or oversized ZIP directory")
    if count != entries:
        raise InvalidPreviewArtifact("ZIP directory count does not match")
    handle.seek(0)


def archive_path(name):
    """Return validated components usable on both Windows and Linux."""
    if not isinstance(name, str) or not name or len(name.encode("utf-8")) > MAX_PATH_BYTES:
        raise InvalidPreviewArtifact("Invalid archive path")
    if name.startswith("/") or name.endswith("//") or "\\" in name or ":" in name:
        raise InvalidPreviewArtifact(f"Unsafe archive path: {name!r}")
    parts = name.rstrip("/").split("/")
    if any(
        part in ("", ".", "..") or part.endswith((".", " "))
        or len(part.encode("utf-8")) > 255
        or any(ord(char) < 32 or ord(char) == 127 or char in '<>"|?*' for char in part)
        or WINDOWS_DEVICE.fullmatch(part)
        for part in parts
    ):
        raise InvalidPreviewArtifact(f"Unsafe archive path: {name!r}")
    return parts


def extract_preview_zip(source, destination):
    """Validate and extract into a new directory; leave no partial result on failure."""
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise InvalidPreviewArtifact("Destination already exists")
    if source.stat().st_size > MAX_ARCHIVE_BYTES:
        raise InvalidPreviewArtifact("Archive exceeds size limit")
    parent = destination.parent
    if not parent.is_dir():
        raise InvalidPreviewArtifact("Destination parent must already exist")
    stage = Path(tempfile.mkdtemp(prefix=".preview-stage-", dir=parent))
    try:
        with source.open("rb") as handle:
            size = os.fstat(handle.fileno()).st_size
            if size > MAX_ARCHIVE_BYTES:
                raise InvalidPreviewArtifact("Archive exceeds size limit")
            check_zip_directory(handle, size)
            archive = zipfile.ZipFile(handle)
            with archive:
                _extract_entries(archive, stage)
        if destination.exists() or destination.is_symlink():
            raise InvalidPreviewArtifact("Destination already exists")
        os.rename(stage, destination)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _extract_entries(archive, stage):
    """Validate every entry before extracting any file to the staging directory."""
    entries = archive.infolist()
    if len(entries) > MAX_FILES:
        raise InvalidPreviewArtifact("Too many archive entries")
    seen = {}
    prefixes = {}
    total = 0
    files = []
    for info in entries:
        if info.orig_filename != info.filename:
            raise InvalidPreviewArtifact("Archive path contains a null byte")
        parts = archive_path(info.filename)
        key = tuple(unicodedata.normalize("NFC", part).casefold() for part in parts)
        for length in range(1, len(key) + 1):
            canonical, spelling = key[:length], tuple(parts[:length])
            if canonical in prefixes and prefixes[canonical] != spelling:
                raise InvalidPreviewArtifact("Ambiguous archive path spelling")
            prefixes[canonical] = spelling
        if key in seen:
            raise InvalidPreviewArtifact("Duplicate or ambiguous archive path")
        seen[key] = "directory" if info.is_dir() else "file"
        mode = info.external_attr >> 16
        file_type = stat.S_IFMT(mode)
        if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise InvalidPreviewArtifact("Links and special files are not allowed")
        if (file_type == stat.S_IFDIR) != info.is_dir() and file_type != 0:
            raise InvalidPreviewArtifact("Inconsistent archive entry type")
        if info.flag_bits & 1:
            raise InvalidPreviewArtifact("Encrypted entries are not supported")
        if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raise InvalidPreviewArtifact("Unsupported archive compression")
        if not info.is_dir():
            if info.file_size > MAX_FILE_BYTES:
                raise InvalidPreviewArtifact("Archive entry exceeds size limit")
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                raise InvalidPreviewArtifact("Unpacked archive exceeds size limit")
            files.append((info, parts))
    for key in seen:
        if any(seen.get(key[:i]) == "file" for i in range(1, len(key))):
            raise InvalidPreviewArtifact("Archive file is also a parent directory")
    if not any(info.filename == "index.html" for info, _ in files):
        raise InvalidPreviewArtifact("Preview index.html is missing")
    for info, parts in files:
        target = stage.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as src, target.open("xb") as dst:
            shutil.copyfileobj(src, dst, length=65536)
