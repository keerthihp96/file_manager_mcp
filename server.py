# server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from config import BASE_DIR
from tools import (
    list_directory,
    read_file,
    search_files,
    get_file_info,
    get_workspace_info,
    write_file,
    append_file,
    create_folder,
    delete_file,
    delete_folder,
    rename
)

# ── Initialize MCP Server ─────────────────────────────────────────────────────
server = Server("file-manager-mcp")


# ── Tool Definitions ──────────────────────────────────────────────────────────
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [

        # ── Read Tools ────────────────────────────────────────────────────────
        types.Tool(
            name="list_directory",
            description=f"List files and folders in the workspace. "
                        f"Base directory: {BASE_DIR}",
            inputSchema={
                "type": "object",
                "properties": {
                    "subfolder": {
                        "type": "string",
                        "description": "Subfolder to list (leave empty for root workspace)"
                    }
                }
            }
        ),

        types.Tool(
            name="read_file",
            description="Read the contents of a text file in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File path relative to workspace e.g. notes/todo.txt"
                    }
                },
                "required": ["filename"]
            }
        ),

        types.Tool(
            name="search_files",
            description="Search for files by name or extension in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search in filenames"
                    },
                    "extension": {
                        "type": "string",
                        "description": "File extension e.g. .txt .py .pdf"
                    }
                }
            }
        ),

        types.Tool(
            name="get_file_info",
            description="Get size, dates, and details of a file or folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File or folder path relative to workspace"
                    }
                },
                "required": ["filename"]
            }
        ),

        types.Tool(
            name="get_workspace_info",
            description="Get full overview of workspace — total files, sizes, file types",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        # ── Write Tools ───────────────────────────────────────────────────────
        types.Tool(
            name="write_file",
            description="Create or overwrite a file in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File path relative to workspace e.g. reports/summary.txt"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["filename", "content"]
            }
        ),

        types.Tool(
            name="append_file",
            description="Append content to an existing file without overwriting",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File path relative to workspace"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to append"
                    }
                },
                "required": ["filename", "content"]
            }
        ),

        types.Tool(
            name="create_folder",
            description="Create a new folder inside the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {
                        "type": "string",
                        "description": "Folder path relative to workspace e.g. projects/ai"
                    }
                },
                "required": ["folder_name"]
            }
        ),

        types.Tool(
            name="delete_file",
            description="Delete a file from the workspace permanently",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File path relative to workspace"
                    }
                },
                "required": ["filename"]
            }
        ),

        types.Tool(
            name="delete_folder",
            description="Delete a folder and all its contents permanently",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {
                        "type": "string",
                        "description": "Folder path relative to workspace"
                    }
                },
                "required": ["folder_name"]
            }
        ),

        types.Tool(
            name="rename",
            description="Rename a file or folder inside the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "old_name": {
                        "type": "string",
                        "description": "Current path relative to workspace"
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New name only — not full path"
                    }
                },
                "required": ["old_name", "new_name"]
            }
        ),
    ]


# ── Tool Router ───────────────────────────────────────────────────────────────
@server.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:

    # Map tool names to handler functions
    handlers = {
        # Read tools
        "list_directory"   : list_directory,
        "read_file"        : read_file,
        "search_files"     : search_files,
        "get_file_info"    : get_file_info,
        "get_workspace_info": get_workspace_info,
        # Write tools
        "write_file"       : write_file,
        "append_file"      : append_file,
        "create_folder"    : create_folder,
        "delete_file"      : delete_file,
        "delete_folder"    : delete_folder,
        "rename"           : rename,
    }

    handler = handlers.get(name)

    if handler:
        try:
            return await handler(arguments)
        except ValueError as e:
            return [types.TextContent(
                type="text",
                text=f"🔒 Security: {str(e)}"
            )]
        except PermissionError:
            return [types.TextContent(
                type="text",
                text="❌ Permission denied — cannot access this path"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]

    return [types.TextContent(
        type="text",
        text=f"❌ Unknown tool: {name}"
    )]


# ── Run Server ────────────────────────────────────────────────────────────────
def main():
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()