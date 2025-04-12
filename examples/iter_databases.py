from notionary.core.database.notion_database_manager import NotionDatabaseManager
from notionary.core.database.notion_database_manager_factory import NotionDatabaseFactory
from datetime import datetime, timedelta

from notionary.core.page.notion_page_manager import NotionPageManager


async def main():
    database_name = "WISSEN_NOTIZEN"
    db_manager: NotionDatabaseManager = await NotionDatabaseFactory.from_database_name(database_name)

    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    
    filter_conditions = {
        "and": [
            {
                "timestamp": "created_time",
                "created_time": {"after": twenty_four_hours_ago.isoformat()}
            },
            {
                "property": "Status",
                "status": {
                    "does_not_equal": "Fertig"
                }
            }
        ]
    }
    
    async for page_manager in db_manager.iter_pages(filter_conditions=filter_conditions):
        print(f"- {page_manager.title} ({page_manager.url})")
        
        status = await page_manager.get_status()
        
        text = await page_manager.get_text()
        print(f"text: {text}")
        
        
async def test_complex_conversion():
    """
    Test the complex conversion of Markdown to Notion blocks and back.
    """
    page_id = "1a3389d5-7bd3-80d7-a507-e67d1b25822c"
    content_manager = NotionPageManager(page_id=page_id)
    
    text = await content_manager.get_text()
    print("Original text:", text)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_complex_conversion())
    # asyncio.run(test_complex_conversion())