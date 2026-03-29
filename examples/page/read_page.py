"""Read a page's content as markdown."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.find("Old draft")

        markdown = await page.get_markdown()
        print(markdown)


if __name__ == "__main__":
    asyncio.run(main())
