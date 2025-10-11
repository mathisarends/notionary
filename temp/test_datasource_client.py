from notionary import NotionDataSource

DATASOURCE_NAME = "Udemny"


async def main() -> None:
    data_source = await NotionDataSource.from_title("Udemy")

    query_params = data_source.filter().where("Status").equals("Abgeschlossen").order_by_created_time().build()

    pages = await data_source.get_pages(query_params=query_params)

    for page in pages:
        print(page.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
