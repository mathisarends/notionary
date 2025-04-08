from typing import Any, AsyncGenerator, Dict, List, Optional
from notionary.core.database.notion_database_schema import NotionDatabaseSchema
from notionary.core.page.notion_page_manager import NotionPageManager


class DatabaseQueryService:
    """Service für Datenbankabfragen und Iterations"""

    def __init__(self, schema: NotionDatabaseSchema):
        self._schema = schema

    async def get_pages(
        self,
        database_id: str,
        limit: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
    ) -> List[NotionPageManager]:
        """
        Get all pages from the database.

        Args:
            database_id: The database ID to query
            limit: Maximum number of pages to retrieve
            filter_conditions: Optional filter to apply to the database query
            sorts: Optional sort instructions for the database query

        Returns:
            List of NotionPageManager instances for each page
        """
        pages: List[NotionPageManager] = []
        count = 0

        async for page in self.iter_pages(
            database_id,
            page_size=min(limit, 100),
            filter_conditions=filter_conditions,
            sorts=sorts,
        ):
            pages.append(page)
            count += 1

            if count >= limit:
                break

        return pages

    async def iter_pages(
        self,
        database_id: str,
        page_size: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[NotionPageManager, None]:
        """
        Asynchronous generator that yields pages from the database.

        Args:
            database_id: The database ID to query
            page_size: Number of pages to fetch per request
            filter_conditions: Optional filter to apply to the database query
            sorts: Optional sort instructions for the database query

        Yields:
            NotionPageManager instances for each page
        """
        async for page_manager in self._schema.iter_database_pages(
            database_id=database_id,
            page_size=page_size,
            filter_conditions=filter_conditions,
            sorts=sorts,
        ):
            yield page_manager
