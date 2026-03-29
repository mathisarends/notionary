"""Customize a page's icon, cover, and title."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.from_title("Old Draft")

        await page.set_icon("📝")
        await page.random_cover()
        await page.rename("Weekly Sync Notes")

        await page.comment("Updated the title and added a cover image.")


if __name__ == "__main__":
    asyncio.run(main())
