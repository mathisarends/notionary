import asyncio

from notionary import NotionWorkspace
from notionary.workspace.query.builder import NotionWorkspaceQueryConfigBuilder


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    builder = NotionWorkspaceQueryConfigBuilder()
    query_config = builder.with_total_results_limit(10).build()

    async for page in workspace.iter_pages(query_config):
        print(f"Page: {page.title} (URL: {page.url})")


if __name__ == "__main__":
    asyncio.run(main())
