from typing import Any

from notionary import (
    DatabaseNamespace,
    DataSourceNamespace,
    PageNamespace,
    UsersNamespace,
    WorkspaceNamespace,
)
from notionary.mcp.app import NotionaryMCP, lifespan

mcp = NotionaryMCP("Notionary MCP Server", lifespan=lifespan)


# ══════════════════════════════════════════════════════════════
# Workspace
# ══════════════════════════════════════════════════════════════


@mcp.workspace_tool(
    description="Search the entire workspace for pages and data sources by keyword."
)
async def search_workspace(query: str, workspace: WorkspaceNamespace) -> list[str]:
    """Search across all pages and data sources in the workspace."""
    results = await workspace.search(query)
    return [str(r) for r in results]


# ══════════════════════════════════════════════════════════════
# Pages
# ══════════════════════════════════════════════════════════════


@mcp.page_tool(
    description="List pages in the workspace, optionally filtered by a search query."
)
async def list_pages(pages: PageNamespace, query: str | None = None) -> list[str]:
    results = await pages.list(query=query)
    return [f"{p.title} (id={p.id})" for p in results]


@mcp.page_tool(description="Find a page by its exact title (case-insensitive).")
async def find_page(title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    return f"{page.title} (id={page.id}, url={page.url})"


@mcp.page_tool(description="Get the full markdown content of a page by title.")
async def get_page_content(title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    return await page.get_markdown()


@mcp.page_tool(description="Get all comments on a page.")
async def get_page_comments(title: str, pages: PageNamespace) -> list[str]:
    page = await pages.find(title)
    comments = await page.get_comments()
    return [str(c) for c in comments]


@mcp.page_tool(
    description=(
        "Update a page. All fields are optional. "
        "Use 'content' to replace the full body, or 'append_content' to add to the end."
    )
)
async def update_page(
    title: str,
    pages: PageNamespace,
    new_title: str | None = None,
    icon_emoji: str | None = None,
    icon_url: str | None = None,
    cover_url: str | None = None,
    content: str | None = None,
    append_content: str | None = None,
    properties: dict[str, Any] | None = None,
) -> str:
    page = await pages.find(title)
    await page.update(
        title=new_title,
        icon_emoji=icon_emoji,
        icon_url=icon_url,
        cover_url=cover_url,
        content=content,
        append_content=append_content,
        properties=properties,
    )
    return f"Updated page '{page.title}'"


@mcp.page_tool(description="Append markdown content to the end of a page.")
async def append_to_page(title: str, content: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.append(content)
    return f"Appended content to '{page.title}'"


@mcp.page_tool(
    description="Replace the entire body of a page with new markdown content."
)
async def replace_page_content(title: str, content: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.replace(content)
    return f"Replaced content of '{page.title}'"


@mcp.page_tool(description="Clear all content from a page, leaving it empty.")
async def clear_page(title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.clear()
    return f"Cleared content of '{page.title}'"


@mcp.page_tool(description="Add a comment to a page.")
async def comment_on_page(title: str, text: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.comment(text)
    return f"Added comment to '{page.title}'"


@mcp.page_tool(description="Rename a page.")
async def rename_page(title: str, new_title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.rename(new_title)
    return f"Renamed '{title}' to '{new_title}'"


@mcp.page_tool(description="Set a property on a page by name and value.")
async def set_page_property(
    title: str, property_name: str, value: Any, pages: PageNamespace
) -> str:
    page = await pages.find(title)
    await page.properties.set_property(property_name, value)
    return f"Set '{property_name}' on '{page.title}'"


@mcp.page_tool(description="Move a page to the trash.")
async def trash_page(title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.trash()
    return f"Trashed '{page.title}'"


@mcp.page_tool(description="Restore a page from the trash.")
async def restore_page(title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.restore()
    return f"Restored '{page.title}'"


@mcp.page_tool(description="Lock a page to prevent editing.")
async def lock_page(title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.lock()
    return f"Locked '{page.title}'"


@mcp.page_tool(description="Unlock a page to allow editing.")
async def unlock_page(title: str, pages: PageNamespace) -> str:
    page = await pages.find(title)
    await page.unlock()
    return f"Unlocked '{page.title}'"


# ══════════════════════════════════════════════════════════════
# Data sources
# ══════════════════════════════════════════════════════════════


@mcp.data_source_tool(
    description="List data sources in the workspace, optionally filtered by query."
)
async def list_data_sources(
    data_sources: DataSourceNamespace, query: str | None = None
) -> list[str]:
    results = await data_sources.list(query=query)
    return [f"{ds.title} (id={ds.id})" for ds in results]


@mcp.data_source_tool(
    description="Find a data source by its exact title (case-insensitive)."
)
async def find_data_source(title: str, data_sources: DataSourceNamespace) -> str:
    ds = await data_sources.find(title)
    return f"{ds.title} (id={ds.id}, url={ds.url})"


@mcp.data_source_tool(
    description="Get the property schema of a data source (column names and types)."
)
async def get_data_source_schema(
    title: str, data_sources: DataSourceNamespace
) -> dict[str, str]:
    ds = await data_sources.find(title)
    return {name: type(prop).__name__ for name, prop in ds.properties.items()}


@mcp.data_source_tool(
    description="Create a new page inside a data source. Returns the page title and id."
)
async def create_page_in_data_source(
    data_source_title: str,
    data_sources: DataSourceNamespace,
    page_title: str | None = None,
) -> str:
    ds = await data_sources.find(data_source_title)
    page = await ds.create_page(title=page_title)
    return f"Created page '{page.title}' (id={page.id}) in '{ds.title}'"


@mcp.data_source_tool(
    description=("Update a data source's metadata. All fields are optional.")
)
async def update_data_source(
    title: str,
    data_sources: DataSourceNamespace,
    new_title: str | None = None,
    icon_emoji: str | None = None,
    icon_url: str | None = None,
    cover_url: str | None = None,
) -> str:
    ds = await data_sources.find(title)
    await ds.update(
        title=new_title,
        icon_emoji=icon_emoji,
        icon_url=icon_url,
        cover_url=cover_url,
    )
    return f"Updated data source '{ds.title}'"


@mcp.data_source_tool(description="List available templates in a data source.")
async def list_data_source_templates(
    title: str, data_sources: DataSourceNamespace
) -> list[str]:
    ds = await data_sources.find(title)
    templates = await ds.list_templates()
    return [t.name for t in templates]


@mcp.data_source_tool(description="Move a data source to the trash.")
async def trash_data_source(title: str, data_sources: DataSourceNamespace) -> str:
    ds = await data_sources.find(title)
    await ds.trash()
    return f"Trashed data source '{ds.title}'"


@mcp.data_source_tool(description="Restore a data source from the trash.")
async def restore_data_source(title: str, data_sources: DataSourceNamespace) -> str:
    ds = await data_sources.find(title)
    await ds.restore()
    return f"Restored data source '{ds.title}'"


# ══════════════════════════════════════════════════════════════
# Databases
# ══════════════════════════════════════════════════════════════


@mcp.database_tool(
    description="List databases in the workspace, optionally filtered by query."
)
async def list_databases(
    databases: DatabaseNamespace, query: str | None = None
) -> list[str]:
    results = await databases.list(query=query)
    return [f"{db.title} (id={db.id})" for db in results]


@mcp.database_tool(description="Find a database by its exact title (case-insensitive).")
async def find_database(title: str, databases: DatabaseNamespace) -> str:
    db = await databases.find(title)
    return f"{db.title} (id={db.id}, url={db.url})"


@mcp.database_tool(description="Create a new database, optionally under a parent page.")
async def create_database(
    databases: DatabaseNamespace,
    title: str | None = None,
    description: str | None = None,
    parent_page_id: str | None = None,
    icon_emoji: str | None = None,
    cover_url: str | None = None,
) -> str:
    from uuid import UUID

    parent = UUID(parent_page_id) if parent_page_id else None
    db = await databases.create(
        parent_page_id=parent,
        title=title,
        description=description,
        icon_emoji=icon_emoji,
        cover_url=cover_url,
    )
    return f"Created database '{db.title}' (id={db.id})"


@mcp.database_tool(description="Update a database's metadata. All fields are optional.")
async def update_database(
    title: str,
    databases: DatabaseNamespace,
    new_title: str | None = None,
    description: str | None = None,
    icon_emoji: str | None = None,
    icon_url: str | None = None,
    cover_url: str | None = None,
    is_locked: bool | None = None,
    is_inline: bool | None = None,
) -> str:
    db = await databases.find(title)
    await db.update(
        title=new_title,
        description=description,
        icon_emoji=icon_emoji,
        icon_url=icon_url,
        cover_url=cover_url,
        is_locked=is_locked,
        is_inline=is_inline,
    )
    return f"Updated database '{db.title}'"


@mcp.database_tool(description="Move a database to the trash.")
async def trash_database(title: str, databases: DatabaseNamespace) -> str:
    db = await databases.find(title)
    await db.trash()
    return f"Trashed database '{db.title}'"


@mcp.database_tool(description="Restore a database from the trash.")
async def restore_database(title: str, databases: DatabaseNamespace) -> str:
    db = await databases.find(title)
    await db.restore()
    return f"Restored database '{db.title}'"


# ══════════════════════════════════════════════════════════════
# Users
# ══════════════════════════════════════════════════════════════


@mcp.user_tool(
    description="List workspace members. Optionally filter by 'person' or 'bot'."
)
async def list_users(users: UsersNamespace, filter: str | None = None) -> list[str]:
    results = await users.list(filter=filter)
    return [str(u) for u in results]


@mcp.user_tool(description="Search workspace members by name or email.")
async def search_users(query: str, users: UsersNamespace) -> list[str]:
    results = await users.search(query)
    return [str(u) for u in results]


@mcp.user_tool(description="Get the bot user associated with the current API token.")
async def get_me(users: UsersNamespace) -> str:
    bot = await users.me()
    return str(bot)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
