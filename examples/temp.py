import logging
import asyncio
import traceback
from notionary import NotionPageFactory, NotionPage


async def main():
    """Tests batch processing by appending many blocks to a Notion page."""

    logger = logging.getLogger("notionary")
    logger.setLevel(logging.DEBUG)

    try:
        print("Searching for page by name...")
        page = await NotionPage.create_from_page_name("Paradoxe Intention")

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )

        print(f'✅ Found: "{title}" {icon} → {url}')

        """ await page.add_relations_by_name(relation_property_name="Projekte", page_titles=["Thesis", "Vizro"])
        print("✅ Relations added successfully.") """

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
