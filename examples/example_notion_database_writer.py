"""
# Notion Database Writer Example
====================================

Simple example of using DatabaseWritter to create and update 
entries in Notion databases with support for relations.
"""

import asyncio
from notionary.core.database.notion_database_writer import DatabaseWritter
from notionary.core.notion_client import NotionClient
from notionary.core.database.notion_database_manager import NotionDatabaseManager


async def main():
    """Creates and updates an entry in a Notion database."""
    
    client = NotionClient()
    
    try:
        db_manager = NotionDatabaseManager(client)
        await db_manager.initialize()
        
        db_writer = DatabaseWritter(client, db_manager)
        
        database_id = "1a6389d5-7bd3-8097-aa38-e93cb052615a"
        
        print("✨ Creating new database entry...")
        
        new_page = await db_writer.create_page(
            database_id=database_id,
            properties={
                "Name": "Notionary API Example",
                "Tags": ["Python", "Notion API"],
                "Status": "Entwurf",
                "URL": "https://github.com/yourusername/notionary"
            },
            relations={
                "Projekte": ["Notionary", "Second Brain"]
            }
        )
        
        if new_page:
            page_id = new_page["id"]
            page_url = new_page["url"]
            print(f"✅ New entry created: {page_url}")
            
            print("🔄 Updating the entry...")
            
            update_result = await db_writer.update_page(
                page_id=page_id,
                properties={"Status": "Fertig"},
                relations={"Thema": ["Software / AI-Engineering"]}
            )
            
            if update_result:
                print("✅ Entry successfully updated")
            else:
                print("❌ Error updating entry")
        else:
            print("❌ Error creating entry")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())