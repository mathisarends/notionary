"""List all pages in the workspace."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.from_title("Weekly Sync Notes")
        comments = await page.get_comments()
        for comment in comments:
            print(f"{comment.author_name}: {comment.content}")

        await page.comment("This is a new comment added via Notionary!")


if __name__ == "__main__":
    asyncio.run(main())
