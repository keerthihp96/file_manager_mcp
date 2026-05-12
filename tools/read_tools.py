# tools/read_tools.py

from pathlib import Path
from mcp import types
from config import BASE_DIR, MAX_RESULTS
from utils import safe_path, validate_file_size, is_text_file
from utils import format_size, format_time, format_separator


async def list_directory(arguments: dict) -> list[types.TextContent]:
    """List files and folders inside the workspace."""
    subfolder = arguments.get("subfolder", "")
    path      = safe_path(subfolder) if subfolder else BASE_DIR

    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"❌ Folder not found: {subfolder}"
        )]

    if not path.is_dir():
        return [types.TextContent(
            type="text",
            text=f"❌ Not a directory: {subfolder}"
        )]

    items   = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    items   = [i for i in items if not i.name.startswith(".")]
    folders = [i for i in items if i.is_dir()]
    files   = [i for i in items if i.is_file()]

    rel     = path.relative_to(BASE_DIR) if path != BASE_DIR else "root"
    lines   = [
        f"📁 Workspace: {rel}",
        f"({len(folders)} folders, {len(files)} files)\n"
    ]

    if folders:
        lines.append("📂 Folders:")
        for f in folders:
            lines.append(f"  📂 {f.name}/")

    if files:
        lines.append("\n📄 Files:")
        for f in files:
            size     = format_size(f.stat().st_size)
            modified = format_time(f.stat().st_mtime)
            lines.append(f"  📄 {f.name} ({size}) — {modified}")

    if not folders and not files:
        lines.append("📭 Empty folder")

    return [types.TextContent(type="text", text="\n".join(lines))]


async def read_file(arguments: dict) -> list[types.TextContent]:
    """Read the full contents of a text file."""
    path = safe_path(arguments["filename"])

    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"❌ File not found: {arguments['filename']}"
        )]

    if not path.is_file():
        return [types.TextContent(
            type="text",
            text=f"❌ Not a file: {arguments['filename']}"
        )]

    if not is_text_file(path):
        return [types.TextContent(
            type="text",
            text=f"❌ Cannot read binary file: {path.name}\n"
                 f"Only text files are supported."
        )]

    validate_file_size(path)

    try:
        content  = path.read_text(encoding="utf-8")
        size     = format_size(path.stat().st_size)
        lines    = content.count("\n") + 1
        modified = format_time(path.stat().st_mtime)

        return [types.TextContent(
            type="text",
            text=f"📄 {path.name} ({size}, {lines} lines)\n"
                 f"Last modified: {modified}\n"
                 f"{format_separator()}\n"
                 f"{content}"
        )]
    except UnicodeDecodeError:
        return [types.TextContent(
            type="text",
            text=f"❌ Cannot decode file: {path.name} — not valid UTF-8"
        )]


async def search_files(arguments: dict) -> list[types.TextContent]:
    """Search for files by name keyword or extension."""
    keyword   = arguments.get("keyword", "").lower()
    extension = arguments.get("extension", "").lower()

    if not keyword and not extension:
        return [types.TextContent(
            type="text",
            text="❌ Please provide a keyword or extension to search"
        )]

    results = []
    for item in BASE_DIR.rglob("*"):
        if item.name.startswith("."):
            continue
        name_match = keyword in item.name.lower() if keyword else True
        ext_match  = item.suffix.lower() == extension if extension else True
        if name_match and ext_match:
            results.append(item)

    if not results:
        return [types.TextContent(
            type="text",
            text="🔍 No files found matching your search"
        )]

    lines = [f"🔍 Found {len(results)} item(s):\n"]
    for item in results[:MAX_RESULTS]:
        icon     = "📂" if item.is_dir() else "📄"
        rel_path = item.relative_to(BASE_DIR)
        size     = f"({format_size(item.stat().st_size)})" if item.is_file() else ""
        lines.append(f"  {icon} {rel_path} {size}")

    if len(results) > MAX_RESULTS:
        lines.append(f"\n... and {len(results) - MAX_RESULTS} more items")

    return [types.TextContent(type="text", text="\n".join(lines))]


async def get_file_info(arguments: dict) -> list[types.TextContent]:
    """Get detailed info about a file or folder."""
    path = safe_path(arguments["filename"])

    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"❌ Not found: {arguments['filename']}"
        )]

    stat      = path.stat()
    file_type = "📂 Folder" if path.is_dir() else "📄 File"

    info = (
        f"{file_type}: {path.name}\n"
        f"{format_separator()}\n"
        f"Relative path : {path.relative_to(BASE_DIR)}\n"
        f"Size          : {format_size(stat.st_size)}\n"
        f"Created       : {format_time(stat.st_ctime)}\n"
        f"Modified      : {format_time(stat.st_mtime)}\n"
        f"Extension     : {path.suffix or 'none'}\n"
        f"Is text file  : {'✅ Yes' if is_text_file(path) else '❌ No'}\n"
    )

    if path.is_dir():
        items  = list(path.iterdir())
        info  += f"Contents      : {len(items)} items\n"

    return [types.TextContent(type="text", text=info)]


async def get_workspace_info(arguments: dict) -> list[types.TextContent]:
    """Get full overview of the workspace."""
    all_items  = list(BASE_DIR.rglob("*"))
    files      = [f for f in all_items if f.is_file()]
    folders    = [f for f in all_items if f.is_dir()]
    total_size = sum(f.stat().st_size for f in files)

    ext_counts = {}
    for f in files:
        ext = f.suffix.lower() or "no extension"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    top_exts = sorted(
        ext_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    lines = [
        f"📊 Workspace Overview",
        f"{'═' * 40}",
        f"📁 Location  : {BASE_DIR}",
        f"📂 Folders   : {len(folders)}",
        f"📄 Files     : {len(files)}",
        f"💾 Total size: {format_size(total_size)}",
        f"\n📊 Top file types:"
    ]
    for ext, count in top_exts:
        lines.append(f"  {ext}: {count} file(s)")

    return [types.TextContent(type="text", text="\n".join(lines))]