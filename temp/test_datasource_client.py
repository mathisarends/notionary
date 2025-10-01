from notionary import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Wissen und Notizen")

    await data_source.create_blank_page(title="Neue leere Seite")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
