import asyncio
from typing import Optional, List
from notionary import NotionPage, NotionDatabase
from notionary.database.client import NotionDatabaseClient
from notionary.page.client import NotionPageClient
from notionary.user import NotionUser, NotionUserManager
from notionary.util import LoggingMixin


class NotionWorkspace(LoggingMixin):
    """
    Represents a Notion workspace, providing methods to interact with databases, pages, and limited user operations.

    Note: Due to Notion API limitations, bulk user operations (listing all users) are not supported.
    Only individual user queries and bot user information are available.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the workspace with Notion clients.
        """
        self.database_client = NotionDatabaseClient(token=token)
        self.page_client = NotionPageClient(token=token)
        self.user_manager = NotionUserManager(token=token)

    async def search_pages(self, query: str, limit=100) -> List[NotionPage]:
        """
        Search for pages globally across Notion workspace.
        """
        response = await self.page_client.search_pages(query, limit=limit)
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

    # User-related methods (limited due to API constraints)
    async def get_current_bot_user(self) -> Optional[NotionUser]:
        """
        Get the current bot user from the API token.

        Returns:
            Optional[NotionUser]: Current bot user or None if failed
        """
        return await self.user_manager.get_current_bot_user()

    async def get_user_by_id(self, user_id: str) -> Optional[NotionUser]:
        """
        Get a specific user by their ID.

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            Optional[NotionUser]: The user or None if not found/failed
        """
        return await self.user_manager.get_user_by_id(user_id)

    async def get_workspace_info(self) -> Optional[dict]:
        """
        Get available workspace information including bot details.

        Returns:
            Optional[dict]: Workspace information or None if failed to get bot user
        """
        return await self.user_manager.get_workspace_info()

    # TODO: Create database would be nice here
