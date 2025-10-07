from notionary import NotionDataSource


async def main() -> None:
    data_source = await NotionDataSource.from_title("Wissen und Notizen")

    page = await data_source.create_blank_page("Neue super page")
    await page.set_emoji_icon("🚀")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
