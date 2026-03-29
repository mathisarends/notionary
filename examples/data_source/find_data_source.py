"""Find a data source by title and inspect its properties."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        ds = await notion.data_sources.from_title("Projekte")

        print(f"Title: {ds.title}")
        print(f"URL:   {ds.url}")

        templates = await ds.list_templates()
        for template in templates:
            print(f"Template: {template.name} (ID: {template.id})")


if __name__ == "__main__":
    asyncio.run(main())
