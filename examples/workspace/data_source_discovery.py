import asyncio

from notionary import NotionWorkspace


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    async for data_source in workspace.get_data_sources_stream():
        print(f"Data Source: {data_source.title} (URL: {data_source.url})")


if __name__ == "__main__":
    asyncio.run(main())
