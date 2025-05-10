import logging
import asyncio
import traceback
from notionary import NotionPage


async def main():
    """Tests batch processing by appending many blocks to a Notion page."""

    logger = logging.getLogger("notionary")
    logger.setLevel(logging.DEBUG)

    try:
        print("Searching for page by name...")
        page = await NotionPage.from_page_name("Inside Devin: The world’s first autonomous AI engineer that's set to write 50% of its company’s code by end of year | Scott Wu (CEO and co-founder of Cognition)")

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )
        print(f"Page found: {page.id}")
        print(f"Icon: {icon}")
        print(f"Title: {title}")
        print(f"URL: {url}")
        
        status = await page.set_property_value_by_name("Status", "Überarbeiten")
        print(f"Status: {status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
