"""
# Notionary: Upload from Bytes Demo
==================================

A demo showing how to upload file content from bytes to Notion workspace.
Perfect for uploading dynamically generated content!

SETUP: No files needed - content is generated in memory.
"""

import asyncio
import json
from datetime import datetime
from notionary import NotionFileUpload, NotionBotUser

FILENAME = "dynamic_report.json"
CONTENT_TYPE = "application/json"


async def main():
    """Demo of uploading file content from bytes."""

    print("🚀 Notionary Upload from Bytes Demo")
    print("=" * 39)

    try:
        print("🔍 Checking workspace upload limits...")
        bot_user = await NotionBotUser.from_current_integration()

        if bot_user:
            print(f"✅ Workspace: {bot_user.workspace_name}")
            if bot_user.max_file_upload_size:
                max_size_mb = bot_user.max_file_upload_size / (1024 * 1024)
                print(f"✅ Max upload size: {max_size_mb:.1f} MB")

        print("\n📊 Generating dynamic content...")

        # Create a sample JSON report
        report_data = {
            "report_id": f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "workspace_info": {
                "name": bot_user.workspace_name if bot_user else "Unknown",
                "bot_user": bot_user.name if bot_user else "Unknown",
            },
            "metrics": {
                "total_uploads": 42,
                "success_rate": 98.5,
                "avg_file_size_mb": 2.3,
            },
            "recent_activities": [
                {
                    "action": "file_upload",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                },
                {
                    "action": "page_update",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                },
                {
                    "action": "database_query",
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                },
            ],
        }

        # Convert to JSON bytes
        json_content = json.dumps(report_data, indent=2)
        file_bytes = json_content.encode("utf-8")
        file_size = len(file_bytes)
        file_size_kb = file_size / 1024

        print("\n📄 Generated Content:")
        print(f"├── Filename: {FILENAME}")
        print(f"├── Content-Type: {CONTENT_TYPE}")
        print(f"├── Size: {file_size_kb:.1f} KB ({file_size:,} bytes)")
        print(f"└── Preview: {json_content[:100]}...")

        # Upload from bytes
        print("\n🚀 Uploading content from memory...")
        file_uploader = NotionFileUpload()

        upload_result = await file_uploader.upload_from_bytes(
            file_content=file_bytes, filename=FILENAME, content_type=CONTENT_TYPE
        )

        if upload_result:
            print("\n✅ Content uploaded successfully!")
            print(f"├── File ID: {upload_result.id}")
            print(f"├── Status: {upload_result.status}")
            print(f"├── Filename: {upload_result.filename}")
            print(f"├── Content Type: {upload_result.content_type}")
            print("├── Upload Mode: From bytes (in-memory)")
            print(f"└── Expires: {upload_result.expiry_time}")

            print("\n💡 To use this file in a page:")
            print(f"   ![Report](notion://file_upload/{upload_result.id})")

            print("\n📋 File content preview:")
            print(f"   {json_content[:200]}...")

        else:
            print("❌ Upload from bytes failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your NOTION_SECRET environment variable is set")


if __name__ == "__main__":
    asyncio.run(main())
