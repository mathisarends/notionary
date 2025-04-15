"""
# NotionPageFactory - Simple Example
Demonstrates how easily you can find Notion pages by their name.
"""

import asyncio
from notionary import NotionPageFactory


async def main():
    """Demonstrates various ways to find a Notion page."""

    # 1. Find a page by its name (most convenient method)
    print("Searching for page by name...")
    page = await NotionPageFactory.from_page_name("My Notes")
    print(f"Found: {page.title}")

    # 2. Alternative: Find a page by ID (if known)
    # page = await NotionPageFactory.from_page_id("1cd389d5-7bd3-81e5-8be9-d35ce24adf3d")

    # 3. Alternative: Find a page by URL
    # page = await NotionPageFactory.from_url("https://www.notion.so/My-Notes-1cd389d57bd381e58be9d35ce24adf3d")

    # Perform simple actions with the found page
    icon = await page.get_icon()
    print(f"Page icon: {icon}")

    await page.append_markdown("## Found via NotionPageFactory")
    print("Markdown added!")

    return page


if __name__ == "__main__":
    found_page = asyncio.run(main())
    print("Done! Page was found by name and updated.")
