"""
# Notionary: Small File Upload Demo
==================================

A demo showing how to upload small files (< 20MB) to Notion workspace.
Perfect for demonstrating single-part file upload!

SETUP: Create a small test file or use any existing file < 20MB.
"""

import asyncio
from pathlib import Path
from notionary import NotionFileUpload, NotionBotUser

TEST_FILE_PATH = Path(__file__).parent / "my_document.pdf"


async def main():
    """Demo of small file upload to Notion workspace."""

    print("🚀 Notionary Small File Upload Demo")
    print("=" * 38)

    try:
        # Check workspace limits first
        print("🔍 Checking workspace upload limits...")
        bot_user = await NotionBotUser.from_current_integration()

        if bot_user and bot_user.max_file_upload_size:
            max_size_mb = bot_user.max_file_upload_size / (1024 * 1024)
            print(f"✅ Max upload size: {max_size_mb:.1f} MB")
        else:
            print("⚠️  Could not determine upload limits")

        file_size = TEST_FILE_PATH.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print("\n📄 File Information:")
        print(f"├── Name: {TEST_FILE_PATH.name}")
        print(f"├── Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
        print(f"└── Path: {TEST_FILE_PATH}")

        # Upload the file
        print("\n🚀 Uploading file...")
        file_uploader = NotionFileUpload()
        upload_result = await file_uploader.upload_file(TEST_FILE_PATH)

        if upload_result:
            print("\n✅ File uploaded successfully!")
            print(f"├── File ID: {upload_result.id}")
            print(f"├── Status: {upload_result.status}")
            print(f"├── Filename: {upload_result.filename}")
            print("├── Upload Mode: Single-part (< 20MB)")
            print(f"└── Expires: {upload_result.expiry_time}")

            print("\n💡 To use this file in a page:")
            print(f"   ![My File](notion://file_upload/{upload_result.id})")

        else:
            print("❌ File upload failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your NOTION_SECRET environment variable is set")


if __name__ == "__main__":
    asyncio.run(main())
