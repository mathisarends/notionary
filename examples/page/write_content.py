"""Write and update page content using markdown."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.from_title("Old Draft")

        await page.append("## Action Items\n\n- Follow up with design team")

        await page.replace("# Fresh Start\n\nThis replaces all previous content.")

        await page.clear()


if __name__ == "__main__":
    asyncio.run(main())
