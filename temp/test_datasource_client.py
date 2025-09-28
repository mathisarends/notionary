from notionary.database.database import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Wissen / Notizen")

    print("data_source", data_source.title)

    themes = await data_source.property_reader.get_relation_options_by_property_name("Thema")
    print(themes)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
