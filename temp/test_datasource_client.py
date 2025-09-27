from notionary import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Wissen / Notizen")

    themes = await data_source.property_reader.get_relation_options_by_property_name("Thema")
    print("themes", themes)

    print("data_source.id", data_source.id)
    print("data_source.title", data_source.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
