import asyncio
import time

from notionary import NotionPage

PAGE_NAME = "Henningway Bridge"


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_title(PAGE_NAME)

        # Erste Request
        start_time = time.time()
        themes = await page.property_reader.get_values_of_relation_property("Thema")
        erste_request_time = time.time() - start_time
        print(f"erste request hat gedauert {erste_request_time:.4f} sekunden")
        print(f"🗂️  Themes: {themes}")

        # Zweite Request (sollte aus Cache kommen)
        start_time = time.time()
        themes = await page.property_reader.get_values_of_relation_property("Thema")
        zweite_request_time = time.time() - start_time
        print(f"zweite request hat gedauert {zweite_request_time:.4f} sekunden")
        print(f"🗂️  Themes: {themes}")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
