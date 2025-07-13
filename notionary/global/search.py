from typing import Optional
from notionary import NotionClient
from notionary.models.notion_database_response import NotionQueryDatabaseResponse
from notionary.util.logging_mixin import LoggingMixin


class GlobalSearchService(LoggingMixin):
    """
    Service for performing global searches across Notion pages and databases.
    
    Vereinfacht - kein Context Manager nötig da NotionClient ein Singleton ist.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the search service with a Notion client.
        
        Da NotionClient ein Singleton ist, wird immer dieselbe Instanz verwendet.
        """
        self.client = NotionClient(token=token)

    async def search_pages(self, query: str) -> NotionQueryDatabaseResponse:
        """Search for pages globally across Notion workspace."""
        self.logger.info(f"🔍 Searching pages with query: '{query}'")
        
        response = await self.client.search_pages_global(query)
        
        self.logger.info(f"✅ Found {len(response.results) if hasattr(response, 'results') else 0} pages")
        
        return response

    async def search_databases(self, query: str) -> NotionQueryDatabaseResponse:
        """Search for databases globally across Notion workspace."""
        self.logger.info(f"🔍 Searching databases with query: '{query}'")
        
        response = await self.client.search_databases_global(query)
        
        self.logger.info("✅ Found databases")
        return response

    def format_page_results(self, response: NotionQueryDatabaseResponse) -> str:
        """Format page search results for display."""
        if not hasattr(response, 'results') or not response.results:
            return "No pages found."
        
        result_lines = []
        for page in response.results:
            result_lines.append(f"📄 Page: {page.id}")
            result_lines.append(f"   Last Edited: {page.last_edited_time}")
            result_lines.append(f"   URL: {page.url}")
            
            if hasattr(page, 'properties') and page.properties:
                result_lines.append("   Properties:")
                for prop, value in page.properties.items():
                    result_lines.append(f"     {prop}: {value}")
            
            result_lines.append("-" * 50)
        
        return "\n".join(result_lines)
    
    
search_service = GlobalSearchService()


# Example usage
async def main():
    response = await search_service.search_pages("React")
        
    formatted_results = search_service.format_page_results(response)
    print(formatted_results)


async def main2():
    response = await search_service.search_databases("Wissen")
    print("Database search response:", response)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
