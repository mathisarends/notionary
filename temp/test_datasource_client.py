from notionary import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Test Data Source")

    query_params = data_source.filter().where("TestProperty").contains("Immer").build()

    pages = await data_source.get_pages(query_params=query_params)

    for page in pages:
        print(page.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
