"""
PDF File Upload Example
=======================

Demonstrates how to upload a local PDF file to Notion.
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Upload a PDF file example."""
    print("📄 PDF Upload Example")
    print("=" * 30)

    try:
        # Load the page
        page = await NotionPage.from_title(PAGE_NAME)

        # Simple PDF upload with caption
        markdown = """
        ## PDF Upload Example

        Here's a PDF document that will be automatically uploaded:

        [pdf](./examples/file_upload/res/test.pdf)(caption:Sample PDF Document)
        """

        await page.append_markdown(markdown)
        print("✅ PDF uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
