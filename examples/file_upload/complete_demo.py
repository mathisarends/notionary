"""
Complete File Upload Demo
========================

Demonstrates all file upload types in one example.
Shows how easy it is to upload different media types to Notion.
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Complete file upload demonstration."""
    print("🚀 Complete File Upload Demo")
    print("=" * 40)

    try:
        page = await NotionPage.from_page_name(PAGE_NAME)

        markdown = """
        # File Upload Demo 🚀

        This demonstrates how easy it is to upload different file types to Notion:

        ## 📄 PDF Document
        [pdf](./examples/file_upload/res/test.pdf)(caption:PDF Document - Automatically uploaded)

        ## 🎵 Audio File
        [audio](./examples/file_upload/res/test.mp3)(caption:Audio Track - Local MP3 file)

        ## 🎬 Video File
        [video](./examples/file_upload/res/test.mp4)(caption:Video Clip - Local video upload)

        ## 🖼️ Image File
        [image](./examples/file_upload/res/test.png)(caption:Image - Local image upload)

        ## 📁 General File
        [file](./examples/file_upload/res/test.pdf)(caption:Generic File - Any file type)

        ---
        All files are automatically detected as local and uploaded to Notion!
        """

        await page.append_markdown(markdown)
        print("✅ All files uploaded successfully!")
        print("📄 Check your Notion page to see the results!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
