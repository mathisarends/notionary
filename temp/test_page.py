from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
    ### Content-Plan für Social Media

    +++ ## Überschrift
    test von der welt
    +++

    +++ normales toggle
    super lit
    +++

    normaler text

    """
    content = await page.append_markdown(markdown)
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
