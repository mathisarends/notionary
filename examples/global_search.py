import asyncio
import os

from notionary.search.global_search import GlobalSearch, SearchObjectType


async def demo():
    """Demonstrates the usage of GlobalSearch class."""
    search = GlobalSearch()

    try:
        print("🔍 Global Search Demo")
        print("=" * 50)

        # Example 1: Search all content
        print("\n1. Searching for 'AI' across all content...")
        results = await search.search_all("AI", limit=5)
        for result in results:
            print(f"   {result.object_type.value}: {result.title}")
            print(f"   📄 ID: {result.id}")
            print(f"   🔗 URL: {result.url}")
            print()

        # Example 2: Search only pages
        print("\n2. Searching for pages containing 'Flutter'...")
        page_results = await search.search_pages("Flutter", limit=3)
        for page, title in page_results:
            print(f"   📄 Page: {title}")
            print(f"   🆔 ID: {page.id}")
            print()

        # Example 5: Get recent items
        print("\n5. Getting recent pages...")
        recent = await search.search_recent(limit=3, object_type=SearchObjectType.PAGE)
        for result in recent:
            print(f"   📄 {result.title}")
            print(f"   🕐 Last edited: {result.last_edited_time}")
            print()

    except Exception as e:
        print(f"❌ Error during demo: {e}")

    finally:
        await search.close()


if __name__ == "__main__":
    asyncio.run(demo())
