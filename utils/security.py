# utils/security.py

from pathlib import Path
from config import BASE_DIR, MAX_FILE_SIZE, TEXT_EXTENSIONS


def safe_path(relative_path: str) -> Path:
    """
    Resolves a relative path inside BASE_DIR.
    Raises ValueError if path tries to escape BASE_DIR.
    This is the core security function — all tool handlers use this.
    """
    full_path = (BASE_DIR / relative_path).resolve()

    if not str(full_path).startswith(str(BASE_DIR.resolve())):
        raise ValueError(
            f"Access denied: path '{relative_path}' is outside "
            f"the allowed workspace directory"
        )
    return full_path


def validate_file_size(path: Path) -> None:
    """
    Raises ValueError if file exceeds MAX_FILE_SIZE.
    """
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        from utils.formatters import format_size
        raise ValueError(
            f"File too large: {format_size(size)} "
            f"(max allowed: {format_size(MAX_FILE_SIZE)})"
        )


def is_text_file(path: Path) -> bool:
    """Returns True if file extension is in allowed text extensions."""
    return path.suffix.lower() in TEXT_EXTENSIONS