from notionary import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Wissen und Notizen")

    options = data_source.get_multi_select_options_by_property_name("Tags")
    print("options:", options)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
