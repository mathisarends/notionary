from notionary import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Wissen und Notizen")

    theme_options = await data_source.get_relation_options_by_property_name("Thema")
    print(theme_options)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
