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
        page = await NotionPage.from_page_name("Smoke Test Page")

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )
        prompt_content = page.get_notion_markdown_syntax_prompt()
        print("promt_content", prompt_content)

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
