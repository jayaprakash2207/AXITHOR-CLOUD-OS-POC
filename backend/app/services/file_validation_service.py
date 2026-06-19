from __future__ import annotations

import mimetypes
import pathlib

ALLOWED_EXTENSIONS = {
    ".html", ".htm", ".css", ".js", ".mjs", ".cjs",
    ".json", ".xml", ".txt", ".md",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".avif",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp4", ".webm", ".ogg", ".mp3",
    ".pdf",
    ".map",
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB per file
MAX_TOTAL_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB total


class FileValidationError(Exception):
    pass


def validate_file_extension(filename: str) -> bool:
    ext = pathlib.Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def get_mime_type(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def validate_zip_contents(file_list: list[str]) -> None:
    """Raise FileValidationError if the zip doesn't contain index.html or has invalid files."""
    normalised = [p.lstrip("/").replace("\\", "/") for p in file_list]
    top_level_index = any(
        p == "index.html" or (p.count("/") == 1 and p.endswith("/index.html"))
        for p in normalised
    )
    if not top_level_index:
        raise FileValidationError(
            "ZIP must contain an index.html at the root (or one directory level deep)."
        )

    for path in normalised:
        if not validate_file_extension(path):
            ext = pathlib.Path(path).suffix.lower()
            raise FileValidationError(
                f"Unsupported file type '{ext}' in '{path}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )


def strip_single_root_dir(paths: list[str]) -> tuple[str | None, list[str]]:
    """If all paths share a single root directory, strip it and return (root, stripped_paths)."""
    parts = [p.lstrip("/").replace("\\", "/") for p in paths]
    roots = {p.split("/")[0] for p in parts if "/" in p}
    non_rooted = [p for p in parts if "/" not in p]
    if non_rooted:
        return None, parts
    if len(roots) == 1:
        root = next(iter(roots))
        stripped = [p[len(root) + 1 :] for p in parts]
        return root, stripped
    return None, parts
