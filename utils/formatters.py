# utils/formatters.py

from datetime import datetime


def format_size(size_bytes: int) -> str:
    """Convert bytes to human readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.1f} GB"


def format_time(timestamp: float) -> str:
    """Convert Unix timestamp to readable datetime."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def format_separator(length: int = 40) -> str:
    """Returns a separator line."""
    return "─" * length