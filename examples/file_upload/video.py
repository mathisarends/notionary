"""
Video File Upload Example
=========================

Demonstrates how to upload a local video file to Notion.
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Upload a video file example."""
    print("🎬 Video Upload Example")
    print("=" * 30)

    try:
        # Load the page
        page = await NotionPage.from_title(PAGE_NAME)

        # Simple video upload with caption
        markdown = """
        ## Video Upload Example

        Here's a video file that will be automatically uploaded:

        [video](./examples/file_upload/res/test.mp4)(caption:Sample Video Clip)
        """

        await page.append_markdown(markdown)
        print("✅ Video uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
