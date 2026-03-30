"""Demonstrate the three ways to create a page inside a data source."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        ds = await notion.data_sources.find("Projekte")

        print(f"Data source: {ds.title} ({ds.url})")

        # 1. Plain page — no template applied
        page = await ds.create_page(title="Bare Page")
        print(f"[no template]      {page.title} → {page.url}")

        # 2. Default template — uses whatever template the database has configured
        page = await ds.create_page(
            title="Default Template Page", use_default_template=True
        )
        print(f"[default template] {page.title} → {page.url}")

        # 3. Specific template — look up available templates first, then pick one
        templates = await ds.list_templates()
        if templates:
            first = templates[0]
            page = await ds.create_page(
                title="From Template Page", template_id=str(first.id)
            )
            print(f"[template '{first.name}'] {page.title} → {page.url}")
        else:
            print("[template]         no templates found in this data source")


if __name__ == "__main__":
    asyncio.run(main())
