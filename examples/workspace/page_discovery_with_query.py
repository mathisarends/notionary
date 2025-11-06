import asyncio

from notionary import NotionWorkspace
from notionary.workspace.query.builder import NotionWorkspaceQueryConfigBuilder

YOUR_QUERY = ""


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    print(f"Search for {YOUR_QUERY}:")
    builder = NotionWorkspaceQueryConfigBuilder()
    config = builder.with_query(YOUR_QUERY).with_total_results_limit(10).build()

    async for page in workspace.iter_pages(config):
        print(f"  {page.title}")


if __name__ == "__main__":
    asyncio.run(main())
