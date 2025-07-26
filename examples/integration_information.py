"""
# Notionary: Integration Bot Demo
=================================

A quick demo showing how to access your Notion integration's bot information.
Perfect for understanding your integration's capabilities and workspace details!

SETUP: Just run this with your Notion API token configured - no additional setup needed.
"""

import asyncio
import traceback
from notionary import NotionIntegrationBot


async def main():
    """Simple demo of NotionIntegrationBot basic operations."""

    print("🤖 Notionary Integration Bot Demo")
    print("=" * 33)

    try:
        print("🔍 Loading integration bot...")
        bot = await NotionIntegrationBot.from_integration()

        # Display basic bot information
        print("\n🤖 Bot Information:")
        print(f"├── Name: {bot.name or 'Unnamed Bot'}")
        print(f"├── ID: {bot.id}")
        print(f"└── Workspace: {bot.workspace_name}")

        # Show integration type
        print("\n🏢 Integration Type:")
        if bot.is_workspace_integration:
            print("└── 🌐 Workspace Integration (team-wide access)")
        else:
            print("└── 👤 User Integration (personal access)")

        # Show file upload limits
        print("\n📁 Upload Limits:")
        print(f"├── Max Size: {bot.max_file_upload_size:.1f} MB")

        print("\n✅ Bot loaded successfully!")
        print("💡 Your integration can now access Notion content")

    except Exception as e:
        print("❌ Error: {}".format(e))
        print("🔍 Full traceback:\n{}".format(traceback.format_exc()))
        print("💡 Make sure your NOTION_API_TOKEN is configured correctly")


if __name__ == "__main__":
    asyncio.run(main())