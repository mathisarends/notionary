from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    themes = await page.property_reader.get_values_of_multiselect_property("Thema")

    print("Themes", themes)

    """ await page.property_writer.set_relation_property_by_page_titles("Thema", ["Smart Home"])
 """


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
