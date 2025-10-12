from notionary import NotionDataSource

DATASOURCE_NAME = "Udemny"


async def main() -> None:
    data_source = await NotionDataSource.from_title("Udemy")

    query_params = (
        data_source.filter()
        .where("Status")
        .equals("Abgeschlossen")
        .or_where("Dozent")
        .equals("Dr. Angela Yu")
        .order_by_created_time()
        .build()
    )

    async for page in data_source.get_pages_stream(query_params):
        print(page.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
