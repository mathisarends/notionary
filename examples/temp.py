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
        page = await NotionPage.from_page_name("Paradoxe Intention")

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )
        print(f"Page found: {page.id}")
        print(f"{icon} → {title} → {url}")
        
        status = await page.set_property_value_by_name("Status", "Fertig")
        print(f"Status: {status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())