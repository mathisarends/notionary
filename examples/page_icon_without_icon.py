import traceback
from notionary import NotionPageFactory

YOUR_PAGE_NAME = "Singleton Metaclass"


async def main():
    """Demonstrates various ways to find a Notion page."""

    try:
        print("Searching for page by name...")
        page = await NotionPageFactory.from_page_name(YOUR_PAGE_NAME)
        icon = await page.get_icon()
        print(f"✅ Found: {icon}")

    except Exception as e:
        print("Error: ", traceback.format_exc(e))
        return


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
