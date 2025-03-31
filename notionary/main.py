"""
Example usage of the NotionClient.
"""

import asyncio
from notionary.core.notion_client import NotionClient


async def main():
    # If needed, set your token in environment variable
    # os.environ["NOTION_SECRET"] = "your_notion_integration_token"
    
    # Enable debug mode for verbose logging
    async with NotionClient(debug=True) as client:
        try:
            # List all accessible databases
            print("\n--- Listing databases ---")
            databases = await client.list_databases()
            print(f"Found {len(databases.get('results', []))} databases")
            
            if databases.get('results'):
                database_id = databases['results'][0]['id']
                print(f"\n--- Getting database details for {database_id} ---")
                database = await client.retrieve_database(database_id)
                print(f"Database title: {database.get('title', [{}])[0].get('text', {}).get('content', 'Untitled')}")
                
                # Query the database
                print(f"\n--- Querying database {database_id} ---")
                query_results = await client.query_database(
                    database_id,
                    page_size=5  # Limit to 5 results
                )
                print(f"Found {len(query_results.get('results', []))} items")
                
                # Get details of the first page
                if query_results.get('results'):
                    page_id = query_results['results'][0]['id']
                    print(f"\n--- Getting page details for {page_id} ---")
                    page = await client.retrieve_page(page_id)
                    print(f"Page URL: {page.get('url', 'Unknown')}")
                    
                    # Get blocks of the page
                    print(f"\n--- Getting blocks for page {page_id} ---")
                    blocks = await client.retrieve_block_children(page_id)
                    print(f"Found {len(blocks.get('results', []))} blocks")
            
            # Search for content
            print("\n--- Searching for content ---")
            search_results = await client.search(
                query="Meeting",  # Search for pages containing "Meeting"
                filter={"property": "object", "value": "page"},  # Only find pages, not databases
                page_size=5  # Limit to 5 results
            )
            print(f"Found {len(search_results.get('results', []))} matching pages")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())