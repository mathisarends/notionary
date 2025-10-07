from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
    +++ ## heading 2
    some text ending here.
    +++
    """
    content = await page.append_markdown(markdown)
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
