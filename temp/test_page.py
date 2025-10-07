from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
    ::: columns
    ::: column
    test
    :::
    ::: column
    fest
    :::
    :::

    wird hier was appended überhaupt
    """
    content = await page.append_markdown(markdown)
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
