from notionary import NotionPage

PAGE = "Ruff Linter"


async def main() -> None:
    page = await NotionPage.from_title(PAGE)

    user = await page.get_markdown_content()
    print(user)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
