from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from notionary import NotionClient, NotionPageFactory, NotionDatabaseFactory

from notionary.util import LoggingMixin, singleton

if TYPE_CHECKING:
    from notionary import NotionPage, NotionDatabase


@singleton
class GlobalSearchService(LoggingMixin):
    """
    Service for performing global searches across Notion pages and databases.

    Simplified – no context manager needed since NotionClient is a singleton.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the search service with a Notion client.
        """
        self.client = NotionClient(token=token)

    async def search_pages(self, query: str) -> List[NotionPage]:
        """Search for pages globally across Notion workspace."""

        response = await self.client.search_pages(query)
        return [NotionPageFactory.from_page_id(page.id) for page in response.results]

    async def search_databases(self, query: str) -> List[NotionDatabase]:
        """
        Search for databases globally across the Notion workspace.
        """

        response = await self.client.search_databases(query)
        return [
            NotionDatabaseFactory.from_database_id(database.id)
            for database in response.results
        ]


search_service = GlobalSearchService()


# Example usage
async def main():
    response = await search_service.search_pages("React")

    for page in response:
        print(f"Found page: {await page.get_title()} (ID: {page.id})")


async def main2():
    response = await search_service.search_databases("Wissen")
    print("Database search response:", response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
