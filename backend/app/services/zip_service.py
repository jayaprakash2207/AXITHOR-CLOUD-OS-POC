from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass

from app.services.file_validation_service import (
    FileValidationError,
    strip_single_root_dir,
    validate_zip_contents,
)


@dataclass
class ExtractedFile:
    path: str
    content: bytes
    checksum: str
    size: int


def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_zip(zip_bytes: bytes) -> list[ExtractedFile]:
    """Extract a ZIP archive and return validated file list."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as exc:
        raise FileValidationError("Uploaded file is not a valid ZIP archive.") from exc

    names = [
        info.filename
        for info in zf.infolist()
        if not info.is_dir() and not info.filename.startswith("__MACOSX")
    ]

    validate_zip_contents(names)
    _, stripped_names = strip_single_root_dir(names)
    name_map = dict(zip(stripped_names, names))

    files: list[ExtractedFile] = []
    for stripped, original in name_map.items():
        data = zf.read(original)
        files.append(
            ExtractedFile(
                path=stripped,
                content=data,
                checksum=_compute_sha256(data),
                size=len(data),
            )
        )
    return files
