from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    content = await page.get_markdown_content()
    print("content", content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
