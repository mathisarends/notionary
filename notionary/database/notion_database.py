from __future__ import annotations
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from notionary.models.notion_database_response import NotionQueryDatabaseResponse
from notionary.notion_client import NotionClient
from notionary.page.notion_page import NotionPage
from notionary.util.warn_direct_constructor_usage import warn_direct_constructor_usage
from notionary.util import LoggingMixin
from notionary.util.page_id_utils import format_uuid


class NotionDatabase(LoggingMixin):
    """
    Minimal manager for Notion databases.
    Focused exclusively on creating basic pages and retrieving page managers
    for further page operations.
    """

    @warn_direct_constructor_usage
    def __init__(self, database_id: str, token: Optional[str] = None):
        """
        Initialize the minimal database manager.

        Args:
            database_id: ID of the Notion database
            token: Optional Notion API token
        """
        self.database_id = database_id
        self._client = NotionClient(token=token)

    @classmethod
    def from_database_id(
        cls, database_id: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabase from a database ID.
        Delegates to NotionDatabaseFactory.
        """
        from notionary.database.notion_database_factory import NotionDatabaseFactory

        return NotionDatabaseFactory.from_database_id(database_id, token)

    @classmethod
    async def from_database_name(
        cls, database_name: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabase by finding a database with a matching name.
        Delegates to NotionDatabaseFactory.
        """
        from notionary.database.notion_database_factory import NotionDatabaseFactory

        return await NotionDatabaseFactory.from_database_name(database_name, token)

    async def create_blank_page(self) -> Optional[NotionPage]:
        """
        Create a new blank page in the database with minimal properties.

        Returns:
            NotionPage for the created page, or None if creation failed
        """
        try:
            response = await self._client.post(
                "pages", {"parent": {"database_id": self.database_id}, "properties": {}}
            )

            if response and "id" in response:
                page_id = response["id"]
                self.logger.info(
                    "Created blank page %s in database %s", page_id, self.database_id
                )

                return NotionPage.from_page_id(
                    page_id=page_id, token=self._client.token
                )

            self.logger.warning("Page creation failed: invalid response")
            return None

        except Exception as e:
            self.logger.error("Error creating blank page: %s", str(e))
            return None

    async def get_pages(
        self,
        limit: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
    ) -> List[NotionPage]:
        """
        Get all pages from the database.

        Args:
            limit: Maximum number of pages to retrieve
            filter_conditions: Optional filter to apply to the database query
            sorts: Optional sort instructions for the database query

        Returns:
            List of NotionPage instances for each page
        """
        self.logger.debug(
            "Getting up to %d pages with filter: %s, sorts: %s",
            limit,
            filter_conditions,
            sorts,
        )

        pages: List[NotionPage] = []
        count = 0

        async for page in self.iter_pages(
            page_size=min(limit, 100),
            filter_conditions=filter_conditions,
            sorts=sorts,
        ):
            pages.append(page)
            count += 1

            if count >= limit:
                break

        self.logger.debug(
            "Retrieved %d pages from database %s", len(pages), self.database_id
        )
        return pages

    async def iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Asynchronous generator that yields pages from the database.
        Directly queries the Notion API without using the schema.

        Args:
            page_size: Number of pages to fetch per request
            filter_conditions: Optional filter to apply to the database query
            sorts: Optional sort instructions for the database query

        Yields:
            NotionPage instances for each page
        """
        self.logger.debug(
            "Iterating pages with page_size: %d, filter: %s, sorts: %s",
            page_size,
            filter_conditions,
            sorts,
        )

        start_cursor: Optional[str] = None
        has_more = True

        body: Dict[str, Any] = {"page_size": page_size}

        if filter_conditions:
            body["filter"] = filter_conditions

        if sorts:
            body["sorts"] = sorts

        while has_more:
            current_body = body.copy()
            if start_cursor:
                current_body["start_cursor"] = start_cursor

            result = await self._client.post(
                f"databases/{self.database_id}/query", data=current_body
            )

            if not result or "results" not in result:
                return

            for page in result["results"]:
                page_id: str = page.get("id", "")

                yield NotionPage.from_page_id(page_id=page_id, token=self._client.token)

            has_more = result.get("has_more", False)
            start_cursor = result.get("next_cursor") if has_more else None
            
    async def query_database_by_title(
        self, page_title: str) -> List[NotionPage]:
        """
        Query the database for pages with a specific title.
        """
        search_results: NotionQueryDatabaseResponse = await self._client.query_database_by_title(database_id=self.database_id, page_title=page_title)
        
        page_results: List[NotionPage] = []
        
        for page in search_results.results:
            page = NotionPage.from_page_id(page_id=page.id, token=self._client.token)
            page_results.append(page)
            
        return page_results
        

    async def archive_page(self, page_id: str) -> bool:
        """
        Delete (archive) a page.

        Args:
            page_id: The ID of the page to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            formatted_page_id = format_uuid(page_id)

            data = {"archived": True}

            result = await self._client.patch_page(formatted_page_id, data)

            if not result:
                self.logger.error("Error deleting page %s", formatted_page_id)
                return False

            self.logger.info(
                "Page %s successfully deleted (archived)", formatted_page_id
            )
            return True

        except Exception as e:
            self.logger.error("Error in archive_page: %s", str(e))
            return False

    async def get_last_edited_time(self) -> Optional[str]:
        """
        Retrieve the last edited time of the database.

        Returns:
            ISO 8601 timestamp string of the last database edit, or None if request fails.
        """
        try:
            db = await self._client.get_database(self.database_id)

            return db.last_edited_time

        except Exception as e:
            self.logger.error(
                "Error fetching last_edited_time for database %s: %s",
                self.database_id,
                str(e),
            )
            return None

    async def close(self) -> None:
        """Close the client connection."""
        await self._client.close()

if __name__ == "__main__":
    import asyncio

    async def main():
        db = await NotionDatabase.from_database_name("Wissen & Notizen")

        page_results = await db.query_database_by_title("Notion Agent")
        
        for page in page_results:
            text_content = await page.get_text_content()
        
    asyncio.run(main())