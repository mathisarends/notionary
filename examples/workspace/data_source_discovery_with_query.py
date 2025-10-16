import asyncio

from notionary import NotionWorkspace

# Replace with your desired query string
YOUR_QUERY = "Poadcast"


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    print(f"Search for {YOUR_QUERY}:")
    async for data_source in workspace.get_data_sources_stream(
        lambda builder: builder.with_query(YOUR_QUERY).with_page_size(10)
    ):
        print(f"  {data_source.title}")


if __name__ == "__main__":
    asyncio.run(main())
