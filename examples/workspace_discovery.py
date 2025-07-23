"""
# Notionary: Workspace Discovery Demo
====================================

Simple demo showing workspace-level operations to discover databases and pages.
Perfect for exploring your entire Notion workspace!

SETUP: Make sure your NOTION_TOKEN environment variable is set.
"""

import asyncio
from notionary import NotionWorkspace

# Replace with your search term
SEARCH_QUERY = "Jarvis"


async def workspace_discovery_demo():
    """Demo of NotionWorkspace discovery features."""

    print("🚀 Notionary Workspace Demo")
    print("=" * 35)

    try:
        # Initialize workspace
        print("🔧 Initializing workspace...")
        workspace = NotionWorkspace()

        # List all databases
        print("\n🗂️  Discovering databases...")
        databases = await workspace.list_all_databases()

        print(f"\n📊 Found {len(databases)} databases:")
        print()

        for i, db in enumerate(databases):
            icon = db.emoji if db.emoji else "🗄️"
            is_last = i == len(databases) - 1

            # Tree structure for better visual hierarchy
            prefix = "└── " if is_last else "├── "
            indent = "    " if is_last else "│   "

            print(f"{prefix}{icon} {db.title}")
            print(f"{indent}├── ID: {db.id}")
            print(f"{indent}└── Visit at: {db.url}")
            print()

        # Search for pages
        print(f"🔍 Searching for pages containing '{SEARCH_QUERY}'...")
        pages = await workspace.search_pages(SEARCH_QUERY, limit=5)

        print(f"\n📄 Found {len(pages)} pages:")
        print()

        for i, page in enumerate(pages):
            icon = page.emoji_icon if page.emoji_icon else "📝"
            is_last = i == len(pages) - 1

            # Tree structure for better visual hierarchy
            prefix = "└── " if is_last else "├── "
            indent = "    " if is_last else "│   "

            print(f"{prefix}{icon} {page.title}")
            print(f"{indent}├── ID: {page.id}")
            print(f"{indent}└── Visit at: {page.url}")
            print()

        print("✅ Workspace discovery completed successfully!")

    except Exception as e:
        print(f"❌ Error during workspace discovery: {e}")
        print("💡 Make sure your NOTION_TOKEN is set and valid")


async def main():
    """Run the workspace discovery demo."""
    await workspace_discovery_demo()


if __name__ == "__main__":
    print("🎭 Starting Notionary Workspace Discovery...")
    print("📝 Make sure your NOTION_TOKEN environment variable is set!")
    print()

    asyncio.run(main())

    print("\n🎉 Thanks for trying the Notionary workspace demo!")
    print("💡 Tip: Update SEARCH_QUERY to search for your own content")
