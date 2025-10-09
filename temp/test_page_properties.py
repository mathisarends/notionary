from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    options = await page.properties.get_multi_select_options_by_property_name("Tags")
    print(f"Options for 'Tags': {options}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
