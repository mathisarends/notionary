from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
    ### Content-Plan für Social Media

    ::: columns
    ::: column 0.7
    Main
    :::
    ::: column 0.3
    Sidebar
    :::
    :::

    """
    content = await page.append_markdown(markdown)
    print("content", content)

    content = await page.get_markdown_content()
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
