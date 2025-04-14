from typing import Dict, Optional, Any
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class PageDatabaseRelation(LoggingMixin):
    """
    Manages the relationship between a Notion page and its parent database.
    Provides methods to access database schema and property options.
    """

    def __init__(self, page_id: str, client: NotionClient):
        """
        Initialize the page-database relationship handler.

        Args:
            page_id: ID of the Notion page
            client: Instance of NotionClient
        """
        self._page_id = page_id
        self._client = client
        self._parent_database_id = None
        self._database_schema = None
        self._page_data = None

    async def _get_page_data(self, force_refresh=False) -> Dict[str, Any]:
        """
        Gets the page data and caches it for future use.

        Args:
            force_refresh: Whether to force a refresh of the page data

        Returns:
            Dict[str, Any]: The page data
        """
        if self._page_data is None or force_refresh:
            self._page_data = await self._client.get_page(self._page_id)
        return self._page_data

    async def get_parent_database_id(self) -> Optional[str]:
        """
        Gets the ID of the database this page belongs to, if any.

        Returns:
            Optional[str]: The database ID or None if the page doesn't belong to a database
        """
        if self._parent_database_id is not None:
            return self._parent_database_id

        page_data = await self._get_page_data()

        if not page_data or "parent" not in page_data:
            return None

        parent = page_data.get("parent", {})
        if parent.get("type") == "database_id":
            self._parent_database_id = parent.get("database_id")
            return self._parent_database_id

        return None

    async def is_database_page(self) -> bool:
        """
        Checks if this page belongs to a database.

        Returns:
            bool: True if the page belongs to a database, False otherwise
        """
        database_id = await self.get_parent_database_id()
        return database_id is not None
