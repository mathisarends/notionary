"""
File Upload Example
===================

Demonstrates how to upload any local file to Notion.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Upload a general file example."""
    print("📁 File Upload Example")
    print("=" * 30)

    try:
        # Load the page
        page = await NotionPage.from_page_name(PAGE_NAME)

        # Simple file upload with caption
        markdown = """
        ## File Upload Example

        Here's a file that will be automatically uploaded:

        [file](./examples/file_upload/res/test.pdf)(caption:Sample Document File)
        """

        await page.append_markdown(markdown)
        print("✅ File uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
