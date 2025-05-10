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

        system_prompt = page.get_notion_markdown_system_prompt()
        print(f"System prompt: {system_prompt}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
