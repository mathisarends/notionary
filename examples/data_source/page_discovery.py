import asyncio

from notionary import NotionDataSource

DATA_SOURCE_TITLE = "Inbox"


async def main() -> None:
    data_source = await NotionDataSource.from_title(DATA_SOURCE_TITLE)
    print(f"Found datasource: {data_source.title} (URL: {data_source.url})")

    query = data_source.get_query_builder().order_by_last_edited_time_descending().total_results_limit(5).build()
    print("query", query)

    async for page in data_source.iter_pages(query_params=query):
        print(f"- {page.title} (URL: {page.url})")


if __name__ == "__main__":
    asyncio.run(main())
