from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    markdown = """
    # Das ist ein Überschrift 1
    das ist alles was zu tun ist
    """
    await page.append_markdown(markdown)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
