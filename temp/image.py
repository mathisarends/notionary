"""
# Notionary: Image Gallery Test
# ==============================

A dedicated script to append only images with captions to a Notion page.
"""

import asyncio
from notionary import NotionPage

# Name of the Notion Page to update
PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Append an image gallery with captions to the specified Notion page."""
    print(f"🚀 Loading page: '{PAGE_NAME}'")
    page = await NotionPage.from_page_name(PAGE_NAME)

    print("🧹 Cleared existing content.")

    markdown = """
# 📸 Image Gallery

[image](https://raw.githubusercontent.com/github/explore/main/topics/python/python.png)(caption:Random Seeded Photo 100)
"""

    print("📝 Appending image gallery...")
    await page.append_markdown(markdown)

    print("✅ Images with captions added successfully!")
    content = await page.get_text_content()
    print(f"📄 Content length: {len(content)} characters")
    print(f"🌐 Visit your Notion page '{PAGE_NAME}' to view the gallery.")


if __name__ == "__main__":
    asyncio.run(main())
