from __future__ import annotations
from typing import Any, AsyncGenerator, Dict, List, Optional

from notionary.models.notion_database_response import (
    NotionPageResponse,
    NotionQueryDatabaseResponse,
)
from notionary.notion_client import NotionClient
from notionary.page.notion_page import NotionPage
from notionary.util import LoggingMixin
from notionary.util.page_id_utils import format_uuid
from notionary.exceptions.database_exceptions import (
    DatabaseConnectionError,
    DatabaseNotFoundException,
)

from notionary.common.filter_builder import FilterBuilder



class NotionDatabase(LoggingMixin):
    """
    Minimal manager for Notion databases.
    Focused exclusively on creating basic pages and retrieving page managers
    for further page operations.
    """

    def __init__(self, database_id: str, token: Optional[str] = None):
        """
        Initialize the minimal database manager.
        """
        self.database_id = database_id
        self._client = NotionClient(token=token)

    @classmethod
    def from_database_id(
        cls, database_id: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabase from a database ID.
        """
        formatted_id = format_uuid(database_id) or database_id

        instance = cls(formatted_id, token)

        cls.logger.info(
            "Successfully created database manager for ID: %s", formatted_id
        )
        return instance

    @classmethod
    async def from_database_name(
        cls, database_name: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabase by finding a database with a matching name.
        Uses Notion's search API and takes the first (best) result.
        """
        from notionary.search import GlobalSearchService

        cls.logger.debug("Searching for database with name: %s", database_name)
        search_service = GlobalSearchService()

        try:
            cls.logger.debug("Using search endpoint to find databases")

            databases = await search_service.search_databases(database_name, limit=1)

            if not databases:
                cls.logger.warning("No databases found for name: %s", database_name)
                raise DatabaseNotFoundException(database_name)

            # Take the first result - Notion's search already ranks by relevance
            matched_db = databases[0]
            database_id = matched_db.database_id
            matched_name = await matched_db.get_title()

            cls.logger.info(
                "Found matching database: '%s' (ID: %s)",
                matched_name,
                database_id,
            )

            manager = cls(database_id, token)

            cls.logger.info(
                "Successfully created database manager for '%s'", matched_name
            )
            return manager
        except Exception as e:
            error_msg = f"Error finding database by name: {str(e)}"
            cls.logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e

    async def create_blank_page(self) -> Optional[NotionPage]:
        """
        Create a new blank page in the database with minimal properties.
        """
        try:
            craeate_page_response: NotionPageResponse = await self._client.create_page(
                parent_database_id=self.database_id
            )

            return NotionPage.from_page_id(page_id=craeate_page_response.id)

        except Exception as e:
            self.logger.error("Error creating blank page: %s", str(e))
            return None

    async def archive_page(self, page_id: str) -> bool:
        """
        Delete (archive) a page.
        """
        try:
            formatted_page_id = format_uuid(page_id)

            result = await self._client.patch_page(
                formatted_page_id, {"archived": True}
            )

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

    async def query_database_by_title(self, page_title: str) -> List[NotionPage]:
        """
        Query the database for pages with a specific title.
        """
        search_results: NotionQueryDatabaseResponse = (
            await self._client.query_database_by_title(
                database_id=self.database_id, page_title=page_title
            )
        )

        page_results: List[NotionPage] = []

        for page in search_results.results:
            page = NotionPage.from_page_id(page_id=page.id, token=self._client.token)
            page_results.append(page)

        return page_results

    async def iter_pages_updated_within(
        self, hours: int = 24, page_size: int = 100
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Iterate through pages edited in the last N hours using FilterBuilder.
        """

        filter_builder = FilterBuilder()
        filter_builder.with_updated_last_n_hours(hours).with_page_size(page_size)
        filter_conditions = filter_builder.build()

        async for page in self._iter_pages(
            page_size=page_size, filter_conditions=filter_conditions
        ):
            yield page

    async def get_all_pages(self) -> List[NotionPage]:
        """
        Get all pages in the database (use with caution for large databases).
        """
        pages = []
        async for page in self._iter_pages():
            pages.append(page)
        return pages

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

    async def get_title(self) -> Optional[str]:
        """
        Retrieve the title of the database.
        """
        try:
            db = await self._client.get_database(self.database_id)
            return db.title[0].plain_text

        except Exception as e:
            self.logger.error(
                "Error fetching title for database %s: %s", self.database_id, str(e)
            )
            return None

    async def _iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Asynchronous generator that yields pages from the database.
        Directly queries the Notion API without using the schema.
        """
        self.logger.debug(
            "Iterating pages with page_size: %d, filter: %s, sorts: %s",
            page_size,
            filter_conditions,
        )

        start_cursor: Optional[str] = None
        has_more = True

        body: Dict[str, Any] = {"page_size": page_size}

        if filter_conditions:
            body["filter"] = filter_conditions

        while has_more:
            current_body = body.copy()
            if start_cursor:
                current_body["start_cursor"] = start_cursor

            result = await self._client.query_database(
                database_id=self.database_id, query_data=current_body
            )

            if not result or not result.results:
                return

            for page in result.results:
                yield NotionPage.from_page_id(page_id=page.id, token=self._client.token)

            has_more = result.has_more
            start_cursor = result.next_cursor if has_more else None
