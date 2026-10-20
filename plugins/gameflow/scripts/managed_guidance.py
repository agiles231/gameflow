"""Byte-preserving managed guidance shared by initialization and migration."""
import os
from pathlib import Path
import stat
import tempfile

START = b"<!-- gameflow:start -->"
END = b"<!-- gameflow:end -->"


def render(existing: bytes, block: bytes) -> bytes:
    """Replace exactly one well-formed block, preserving all outside bytes."""
    starts, ends = existing.count(START), existing.count(END)
    if (starts, ends) not in ((0, 0), (1, 1)):
        raise ValueError("duplicate or unmatched GameFlow markers")
    newline = b"\r\n" if b"\r\n" in existing else b"\n"
    block = block.replace(b"\r\n", b"\n").strip().replace(b"\n", newline)
    if starts:
        start, end = existing.index(START), existing.index(END)
        if start >= end:
            raise ValueError("reversed GameFlow markers")
        return existing[:start] + block + existing[end + len(END):]
    separator = b"" if not existing else (newline if existing.endswith(b"\n") else newline * 2)
    return existing + separator + block + newline


def replace_checked(path: Path, expected: bytes | None, content: bytes | None) -> None:
    """Check source identity immediately before atomic replacement (or removal)."""
    if path.is_symlink():
        raise ValueError(f"refusing symlink: {path}")
    current = path.read_bytes() if path.exists() else None
    if current != expected:
        raise ValueError(f"source changed since inspection: {path}")
    if content is None:
        path.unlink()
        return
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=".gameflow-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        if (path.read_bytes() if path.exists() else None) != expected:
            raise ValueError(f"source changed since inspection: {path}")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
