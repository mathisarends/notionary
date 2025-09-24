import asyncio

from notionary import NotionPage

PAGE_NAME = "Ruff Linter"


async def main():
    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_title(PAGE_NAME)
        await page.property_writer.set_relation_property_by_page_titles("Thema", ["Smart Home", "Lernen"])

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
