import traceback
import asyncio
from notionary import NotionDatabase


async def main():
    """Demonstrate workspace-level operations with Notionary."""
    print("")
    print("🌐 Notionary Workspace Example")
    print("==============================")

    try:
        db = await NotionDatabase.from_database_name("Wissen/Notizen")

        await db.set_emoji("📚")

        url = await db.set_random_gradient_cover()
        print(f"Cover set to: {url}")

        properties = db.get_options_by_property_name("Tags")
        print("Properties for 'Tags':", properties)

    except Exception as e:
        print(f"❌ Error: {traceback.format_exc(e)}")


if __name__ == "__main__":

    asyncio.run(main())
