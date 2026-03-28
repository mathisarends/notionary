"""Search across the entire workspace for pages and data sources."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        results = await notion.workspace.search("Design")
        for item in results:
            print(f"[{type(item).__name__}] {item.title} ({item.url})")


if __name__ == "__main__":
    asyncio.run(main())
