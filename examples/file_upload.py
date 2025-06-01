"""
# Notionary: File Upload Test
============================

Simple test for file upload functionality.
"""

import asyncio
import json
import os
from notionary import NotionClient


async def main():
    """Test file upload functionality."""
    print("📁 File Upload Test")
    print("==================")

    client = None
    try:
        client = NotionClient()

        # Korrekte Pfad-Erstellung
        file_path = os.path.join(os.getcwd(), "examples", "res", "picture.jpg")

        # Prüfen ob Datei existiert
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            print("💡 Create a 'res' folder and add 'picture.jpg' or adjust the path")
            return

        print(f"📤 Uploading file: {file_path}")

        # File Upload
        upload_result = await client.upload_file(file_path=file_path)

        if upload_result:
            print("✅ File uploaded successfully!")
            print("upload_result:", json.dumps(upload_result, indent=2))
            print(f"🔗 Upload ID: {upload_result.get('id', 'Unknown')}")
            print(f"📊 Result: {upload_result}")
        else:
            print("❌ File upload failed")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Client schließen
        if client:
            await client.close()


if __name__ == "__main__":
    print("🚀 Starting file upload test...")
    asyncio.run(main())
    print("✅ File upload test completed!")
