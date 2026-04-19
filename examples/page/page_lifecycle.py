import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.find("Old Draft")

        await page.lock()
        print(f"Page locked: {page.title}")

        await page.unlock()

        await page.trash()
        print(f"In trash: {page.in_trash}")

        await page.restore()
        print(f"Restored: {page.in_trash}")


if __name__ == "__main__":
    asyncio.run(main())
