import asyncio

from notionary import NotionWorkspace

YOUR_QUERY = ""


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    print(f"Search for {YOUR_QUERY}:")
    async for page in workspace.get_pages_stream(
        filter_fn=lambda builder: builder.with_query(
            YOUR_QUERY
        ).with_total_results_limit(10)
    ):
        print(f"  {page.title}")


if __name__ == "__main__":
    asyncio.run(main())
