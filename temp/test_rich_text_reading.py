import asyncio

from notionary import NotionDatabase

PAGE_NAME = "Wissen & Notizen"


async def main():
    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        db = await NotionDatabase.from_title(PAGE_NAME)
        await db.set_description("Neue Beschreibung der Datenbank")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
