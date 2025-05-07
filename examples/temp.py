import logging
import asyncio
import textwrap
import traceback
from notionary import NotionPage


async def main():
    """Tests batch processing by appending many blocks to a Notion page."""

    logger = logging.getLogger("notionary")
    logger.setLevel(logging.DEBUG)

    try:
        print("Searching for page by name...")
        page = await NotionPage.from_page_name("#936 - Alex Hutchinson - How To Rewire Your Brain To Take More Risks")
        
        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )
        print(f'✅ Found: "{title}" {icon} → {url}')
        
        text_content = await page.get_text_content()
        print(f"✅ Text content retrieved: {text_content}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
