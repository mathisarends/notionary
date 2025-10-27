import asyncio

from notionary import NotionWorkspace, NotionWorkspaceQueryConfigBuilder


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    query_config_builder = NotionWorkspaceQueryConfigBuilder().with_total_results_limit(
        10
    )
    query_config = query_config_builder.build()

    async for page in workspace.get_pages_stream(query_config=query_config):
        print(f"Data Source: {page.title} (URL: {page.url})")


if __name__ == "__main__":
    asyncio.run(main())
