"""
Audio File Upload Example
=========================

Demonstrates how to upload a local audio file to Notion.
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Upload an audio file example."""
    print("🎵 Audio Upload Example")
    print("=" * 30)

    try:
        page = await NotionPage.from_title(PAGE_NAME)

        # Simple audio upload with caption
        markdown = """
        ## Audio Upload Example

        Here's an audio file that will be automatically uploaded:

        [audio](./examples/file_upload/res/test.mp3)(caption:Sample Audio Track)
        """

        await page.append_markdown(markdown)
        print("✅ Audio uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
