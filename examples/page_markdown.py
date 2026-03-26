import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.from_title("Eleven Labs")

        markdown = await page.get_markdown()
        print("Markdown content of the page:")
        print(markdown)
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
