# tools/write_tools.py

import shutil
from pathlib import Path
from mcp import types
from config import BASE_DIR
from utils import safe_path, format_size, format_time


async def write_file(arguments: dict) -> list[types.TextContent]:
    """Create or overwrite a file in the workspace."""
    path    = safe_path(arguments["filename"])
    content = arguments["content"]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return [types.TextContent(
        type="text",
        text=f"✅ File saved!\n"
             f"Path : {path.relative_to(BASE_DIR)}\n"
             f"Size : {format_size(len(content.encode()))}"
    )]


async def append_file(arguments: dict) -> list[types.TextContent]:
    """Append content to an existing file."""
    path    = safe_path(arguments["filename"])
    content = arguments["content"]

    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"❌ File not found: {arguments['filename']}"
        )]

    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

    return [types.TextContent(
        type="text",
        text=f"✅ Content appended to {path.name}\n"
             f"New size: {format_size(path.stat().st_size)}"
    )]


async def create_folder(arguments: dict) -> list[types.TextContent]:
    """Create a new folder inside the workspace."""
    path = safe_path(arguments["folder_name"])
    path.mkdir(parents=True, exist_ok=True)

    return [types.TextContent(
        type="text",
        text=f"✅ Folder created: {path.relative_to(BASE_DIR)}"
    )]


async def delete_file(arguments: dict) -> list[types.TextContent]:
    """Delete a file from the workspace."""
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

    path.unlink()
    return [types.TextContent(
        type="text",
        text=f"🗑️ File deleted: {arguments['filename']}"
    )]


async def delete_folder(arguments: dict) -> list[types.TextContent]:
    """Delete a folder and all its contents."""
    path = safe_path(arguments["folder_name"])

    if not path.exists():
        return [types.TextContent(
            type="text",
            text=f"❌ Folder not found: {arguments['folder_name']}"
        )]

    if not path.is_dir():
        return [types.TextContent(
            type="text",
            text=f"❌ Not a folder: {arguments['folder_name']}"
        )]

    shutil.rmtree(path)
    return [types.TextContent(
        type="text",
        text=f"🗑️ Folder deleted: {arguments['folder_name']}"
    )]


async def rename(arguments: dict) -> list[types.TextContent]:
    """Rename a file or folder inside the workspace."""
    old_path = safe_path(arguments["old_name"])
    new_path = old_path.parent / arguments["new_name"]

    # Validate new path is still inside workspace
    safe_path(str(new_path.relative_to(BASE_DIR)))

    if not old_path.exists():
        return [types.TextContent(
            type="text",
            text=f"❌ Not found: {arguments['old_name']}"
        )]

    if new_path.exists():
        return [types.TextContent(
            type="text",
            text=f"❌ Already exists: {arguments['new_name']}"
        )]

    old_path.rename(new_path)
    return [types.TextContent(
        type="text",
        text=f"✅ Renamed!\n"
             f"From : {arguments['old_name']}\n"
             f"To   : {arguments['new_name']}"
    )]