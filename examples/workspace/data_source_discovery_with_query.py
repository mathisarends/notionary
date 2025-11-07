import asyncio

from notionary import NotionWorkspace
from notionary.workspace.query.builder import NotionWorkspaceQueryConfigBuilder

# Replace with your desired query string
YOUR_QUERY = ""


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    print(f"Search for {YOUR_QUERY}:")
    builder = NotionWorkspaceQueryConfigBuilder()
    config = builder.with_query(YOUR_QUERY).with_page_size(10).build()

    async for data_source in workspace.iter_data_sources(config):
        print(f"  {data_source.title}")


if __name__ == "__main__":
    asyncio.run(main())
