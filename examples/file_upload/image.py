"""
Image File Upload Example
=========================

Demonstrates how to upload a local image file to Notion.
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Upload an image file example."""
    print("🖼️ Image Upload Example")
    print("=" * 30)

    try:
        # Load the page
        page = await NotionPage.from_title(PAGE_NAME)

        # Simple image upload with caption
        markdown = """
        ## Image Upload Example

        Here's an image file that will be automatically uploaded:

        [image](./examples/file_upload/res/test.png)(caption:Sample Image)
        """

        await page.append_markdown(markdown)
        print("✅ Image uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
