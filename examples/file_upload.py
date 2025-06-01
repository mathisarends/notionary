"""
# Notionary: File Upload Test
============================

Simple test for file upload functionality with Pydantic validation.
"""

import asyncio
import os
import traceback

from notionary import NotionClient


async def main():
    """Test file upload functionality."""
    print("📁 File Upload Test")
    print("==================")

    client = None
    try:
        client = NotionClient()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "res", "picture.jpg")

        print(f"📤 Uploading: {os.path.basename(file_path)}...")
        
        upload_result = await client.upload_file(file_path=file_path)

        if upload_result:
            filename = upload_result.filename or os.path.basename(file_path)
            
            print(f"✅ Upload ID: {upload_result.id}")
            print(f"📁 File: {filename} • Status: {upload_result.status}")
        else:
            print("❌ Upload failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
    finally:
        if client:
            await client.close()


if __name__ == "__main__":
    print("🚀 Starting upload test...")
    asyncio.run(main())
    print("✅ Test completed!")