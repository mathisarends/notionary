import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        pages = await notion.pages.list()
        for page in pages:
            print(f"{page.title} ({page.url})")


if __name__ == "__main__":
    asyncio.run(main())
