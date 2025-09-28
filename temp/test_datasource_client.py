from notionary import NotionPage


async def main() -> None:
    page = await NotionPage.from_title("Ruff Linter")

    comments = await page.get_comments()

    for comment in comments:
        print(f"{comment.author_name}: {comment.content}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
