from typing import Optional, List
from notionary import NotionPage, NotionDatabase, NotionClient
from notionary.util import LoggingMixin
from notionary.common.search_filter_builder import SearchFilterBuilder


class NotionWorkspace(LoggingMixin):
    """
    Represents a Notion workspace, providing methods to interact with databases and pages.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the workspace with a Notion client.
        """
        self.client = NotionClient(token=token)

    async def search_pages(self, query: str):
        """
        Search for pages globally across Notion workspace.
        """
        response = await self.client.search_pages(query)
        return [NotionPage.from_page_id(page.id) for page in response.results]

    async def search_databases(self, query: str, limit: int = 10):
        """
        Search for databases globally across the Notion workspace.
        """
        response = await self.client.search_databases(query=query, limit=limit)
        return [
            NotionDatabase.from_database_id(database.id)
            for database in response.results
        ]

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
        database_results = await self.client.search_databases(query="", limit=limit)
        return [
            NotionDatabase.from_database_id(database.id)
            for database in database_results.results
        ]


if __name__ == "__main__":
    import asyncio

    async def main():
        workspace = NotionWorkspace()
        databases = await workspace.list_all_databases()
        for db in databases:
            print(f"Database ID: {db.database_id}, Title: {await db.get_title()}")
            
    asyncio.run(create_database_test())
