"""
Finds a Notion data source (e.g., database or collection) by its title adds a new meme page to it ("Never gonna give you up")
"""

import asyncio

from notionary import NotionDataSource

# Replace with your datasource/database title
DATA_SOURCE_TITLE = "Inbox"


async def main() -> None:
    data_source = await NotionDataSource.from_title(DATA_SOURCE_TITLE)
    print(f"Found datasource: {data_source.title} (URL: {data_source.url})")

    page = await data_source.create_blank_page(title="New Page from Notionary")

    await page.set_emoji_icon("🆕")
    await page.set_random_gradient_cover()
    await page.append_markdown(
        """
        # New Page from Notionary

        - [x] Install Notionary
        - [x] Set up authentication
        - [ ] Create your first page
        - [ ] Explore advanced features

        See other examples for more and complex markdown formats!
        """
    )

    print("Created new page at ", page.url)


if __name__ == "__main__":
    asyncio.run(main())
