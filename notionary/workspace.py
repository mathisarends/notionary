import asyncio
from typing import Optional

from notionary import NotionDatabase, NotionPage
from notionary.database.database_client import NotionDatabaseClient
from notionary.database.database_models import NotionQueryDatabaseResponse
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
        search_query = self._truncate_query_if_needed(query)

        search_filter = (
            SearchFilterBuilder()
            .with_query(search_query)
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
        search_query = self._truncate_query_if_needed(query)

        response = await self.database_client.search_databases(
            query=search_query, limit=limit
        )
        return await asyncio.gather(
            *(
                NotionDatabase.from_database_id(database.id)
                for database in response.results
            )
        )

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
        """
        return await self.user_manager.get_current_bot_user()

    async def get_user_by_id(self, user_id: str) -> Optional[NotionUser]:
        """
        Get a specific user by their ID.
        """
        return await self.user_manager.get_user_by_id(user_id)

    async def get_workspace_info(self) -> Optional[dict]:
        """
        Get available workspace information including bot details.

        Returns:
            Optional[dict]: Workspace information or None if failed to get bot user
        """
        return await self.user_manager.get_workspace_info()

    def _truncate_query_if_needed(self, query: str) -> str:
        """
        Truncates search queries to first 4 words to avoid Notion API issues with long queries.
        """
        MAX_WORDS = 4

        words = query.split()

        if len(words) > MAX_WORDS:
            truncated = " ".join(words[:MAX_WORDS])
            self.logger.debug(f"Query truncated from '{query}' to '{truncated}'")
            return truncated

        return query
