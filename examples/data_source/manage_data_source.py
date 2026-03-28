"""Create a new page inside a data source and customize its appearance."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        ds = await notion.data_sources.from_title("Projects")

        page = await ds.create_page(title="New Project")
        print(f"Created: {page.title} ({page.url})")

        await ds.set_icon_emoji("📁")
        await ds.set_title("Projects (updated)")


if __name__ == "__main__":
    asyncio.run(main())
