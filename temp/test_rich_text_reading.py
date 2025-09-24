import asyncio

from notionary import NotionDatabase

PAGE_NAME = "Wissen & Notizen"


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        db = await NotionDatabase.from_database_name(PAGE_NAME)

        await db.set_title("Neuer Titel")

        await db.set_emoji_icon("🚀")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
