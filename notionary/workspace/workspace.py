from typing import Optional, List
from notionary import NotionPage, NotionDatabase, NotionClient
from notionary.util import LoggingMixin


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

    async def crate_database(self, title: str, properties: dict) -> NotionDatabase:
        """
        Create a new database in the Notion workspace.

        Args:
            title: The title of the new database.
            properties: A dictionary defining the properties of the database.

        Returns:
            The created NotionDatabase instance.
        """

    async def list_all_databases(self, page_size: int = 100) -> List[NotionDatabase]:
        """
        List all databases in the workspace.
        Returns a list of NotionDatabase instances.
        """
        databases = []
        start_cursor = None
        while True:
            body = {
                "filter": {"value": "database", "property": "object"},
                "page_size": page_size,
            }
            if start_cursor:
                body["start_cursor"] = start_cursor
            result = await self.client.post("search", data=body)
            if not result or "results" not in result:
                break
            for database in result["results"]:
                db_id = database.get("id")
                if db_id:
                    databases.append(NotionDatabase.from_database_id(db_id))
            if not result.get("has_more") or not result.get("next_cursor"):
                break
            start_cursor = result["next_cursor"]
        return databases
