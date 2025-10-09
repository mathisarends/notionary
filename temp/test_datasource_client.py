from notionary.data_source.query.service import DataSourceFilterBuilder

from notionary import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Test Data Source")

    builder = DataSourceFilterBuilder()
    filters = builder.where("TestProperty").contains("Immer").build()

    pages = await data_source.get_pages(filters=filters)

    for page in pages:
        print(page.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
