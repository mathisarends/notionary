import asyncio
from typing import Optional

from notionary import NotionDatabase, NotionPage
from notionary.database.client import NotionDatabaseClient
from notionary.database.models import NotionQueryDatabaseResponse
from notionary.notion_client import NotionClient
from notionary.page.search_filter_builder import SearchFilterBuilder
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
        self.notion_client = NotionClient(token=token)
        self.user_manager = NotionUserManager(token=token)

    async def search_pages(
        self, query: str, sort_ascending: bool = True, limit: int = 100
    ) -> list[NotionPage]:
        """
        Searches for pages in Notion using the search endpoint.
        """
        search_filter = (
            SearchFilterBuilder()
            .with_query(query)
            .with_pages_only()
            .with_sort_direction("ascending" if sort_ascending else "descending")
            .with_page_size(limit)
        )

        result = await self.notion_client.post("search", search_filter.build())
        response = NotionQueryDatabaseResponse.model_validate(result)

        return await asyncio.gather(
            *(NotionPage.from_page_id(page.id) for page in response.results)
        )

    async def search_databases(
        self, query: str, limit: int = 100
    ) -> list[NotionDatabase]:
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

    async def list_all_databases(self, limit: int = 100) -> list[NotionDatabase]:
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
