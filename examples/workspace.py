"""
# Notionary: Workspace Management Example
========================================

This example demonstrates how to use NotionWorkspace as the top-level instance
for global searches across your entire Notion workspace, then work with
specific databases and pages found through these searches.

IMPORTANT: Set your NOTION_TOKEN environment variable or pass it directly.
"""

import asyncio
import traceback
from notionary import NotionWorkspace

YOUR_SEARCH_QUERY = "Jarvis"

async def main():
    """Demonstrate workspace-level operations with Notionary."""
    print("")
    print("🌐 Notionary Workspace Example")
    print("==============================")

    try:
        workspace = NotionWorkspace()
        
        print("🔍 Searching for databases globally...")
        databases = await workspace.list_all_databases()
        print(f"Found {len(databases)} databases:")
        
        for db in databases:
            print(f" {db.emoji} {db.title} (ID: {db.database_id} ({db.url}))")
        
    except Exception as e:
        print(f"❌ Error: {traceback.format_exc(e)}")
        
async def search_pages_in_workspace():
    """Search for pages globally across the Notion workspace."""
    try:
        workspace = NotionWorkspace()
        
        print("\n🔍 Searching for pages globally...")
        pages = await workspace.search_pages(YOUR_SEARCH_QUERY)
        print(f"Found {len(pages)} pages:")
        
        for page in pages:
            title = await page.get_title()
            url = await page.get_url()
            icon = await page.get_icon()
            print(f" 📄 {title} - {url} {icon}")
        
    except Exception as e:
        print(f"❌ Error: {traceback.format_exc(e)}")   


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(search_pages_in_workspace())
    print("\n" + "="*50)
    print("✅ Example completed!")