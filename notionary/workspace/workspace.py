import asyncio
from typing import Optional, List
from notionary import NotionPage, NotionDatabase
from notionary.database.client import NotionDatabaseClient
from notionary.page.notion_page_client import NotionPageClient
from notionary.util import LoggingMixin


class NotionWorkspace(LoggingMixin):
    """
    Represents a Notion workspace, providing methods to interact with databases and pages.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the workspace with a Notion database_client.
        """
        self.database_client = NotionDatabaseClient(token=token)
        self.page_client = NotionPageClient(token=token)

    async def search_pages(self, query: str, limit = 100) -> List[NotionPage]:
        """
        Search for pages globally across Notion workspace.
        """
        response = await self.page_client.search_pages(query, limit=limit)
        # Parallelisiere die Erzeugung der NotionPage-Instanzen
        return await asyncio.gather(
            *(NotionPage.from_page_id(page.id) for page in response.results)
        )

    async def search_databases(
        self, query: str, limit: int = 100
    ) -> List[NotionDatabase]:
        """
        Search for databases globally across the Notion workspace.
        """
        response = await self.database_client.search_databases(query=query, limit=limit)
        return await asyncio.gather(
            *(
                NotionDatabase.from_database_id(database.id)
                for database in response.results
            )
        )

    async def get_database_by_name(
        self, database_name: str
    ) -> Optional[NotionDatabase]:
        """
        Get a Notion database by its name.
        Uses Notion's search API and returns the first matching database.
        """
        databases = await self.search_databases(query=database_name, limit=1)

        return databases[0] if databases else None

    async def list_all_databases(self, limit: int = 100) -> List[NotionDatabase]:
        """
        List all databases in the workspace.
        Returns a list of NotionDatabase instances.
        """
        database_results = await self.database_client.search_databases(
            query="", limit=limit
        )
        return [
            await NotionDatabase.from_database_id(database.id)
            for database in database_results.results
        ]

    # TODO: Create database would be nice here
