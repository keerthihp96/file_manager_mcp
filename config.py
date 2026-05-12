# config.py

from pathlib import Path

# ── Safe Workspace — Claude can ONLY access this folder ───────────────────────
BASE_DIR = Path.home() / "Desktop" / "ClaudeFiles"
BASE_DIR.mkdir(exist_ok=True)

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE    = MAX_FILE_SIZE_MB * 1024 * 1024   # 10MB in bytes
MAX_RESULTS      = 50                                # max search results

# ── Allowed text file extensions ──────────────────────────────────────────────
TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".ts", ".html", ".css",
    ".json", ".yaml", ".yml", ".csv", ".sql", ".sh", ".env",
    ".toml", ".xml", ".log", ".ini", ".cfg", ".rst"
}