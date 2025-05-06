import logging
import asyncio
import traceback
from notionary import NotionPage, NotionDatabase


async def main():
    """Tests batch processing by appending many blocks to a Notion page."""

    logger = logging.getLogger("notionary")
    logger.setLevel(logging.DEBUG)

    try:
        print("Searching for page by name...")
        page = await NotionPage.from_page_name("#936 - Alex Hutchinson - How To Rewire Your Brain To Take More Risks")
        
        database = await NotionDatabase.from_database_name("Wissen & Notizen")
        last_edit = await database.get_last_edited_time()
        print(f"Last edited time: {last_edit}")

        """ icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )
        print(f'✅ Found: "{title}" {icon} → {url}')

        result = await page.get_cover_url()
        print(f"✅ Icon: {result}") """

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
