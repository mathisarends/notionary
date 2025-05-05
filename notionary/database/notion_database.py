from typing import Any, AsyncGenerator, Dict, List, Optional

from notionary.notion_client import NotionClient
from notionary.page.notion_page import NotionPage
from notionary.util import warn_direct_constructor_usage
from notionary.util.logging_mixin import LoggingMixin
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
        self.database_id = format_uuid(database_id) or database_id
        self._client = NotionClient(token=token)

    @classmethod
    async def from_database_id(
        cls, database_id: str, token: Optional[str] = None
    ) -> "NotionDatabase":
        """
        Create a NotionDatabase from a database ID.
        Delegates to NotionDatabaseFactory.
        """
        from notionary.database.notion_database_factory import NotionDatabaseFactory

        return await NotionDatabaseFactory.from_database_id(database_id, token)

    @classmethod
    async def from_database_name(
        cls, database_name: str, token: Optional[str] = None
    ) -> "NotionDatabase":
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

                return NotionPage(page_id=page_id)

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

        # Prepare the query body
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
                title = self._extract_page_title(page)

                page_url = f"https://notion.so/{page_id.replace('-', '')}"

                notion_page_manager = NotionPage(
                    page_id=page_id, title=title, url=page_url
                )
                yield notion_page_manager

            # Update pagination parameters
            has_more = result.get("has_more", False)
            start_cursor = result.get("next_cursor") if has_more else None

    def _extract_page_title(self, page: Dict[str, Any]) -> str:
        """
        Extracts the title from a Notion page object.

        Args:
            page: The Notion page object

        Returns:
            The extracted title as a string, or an empty string if no title found
        """
        properties = page.get("properties", {})
        if not properties:
            return ""

        for prop_value in properties.values():
            if prop_value.get("type") != "title":
                continue

            title_array = prop_value.get("title", [])
            if not title_array:
                continue

            return title_array[0].get("plain_text", "")

        return ""

    async def delete_page(self, page_id: str) -> Dict[str, Any]:
        """
        Delete (archive) a page.

        Args:
            page_id: The ID of the page to delete

        Returns:
            Dict with success status, message, and page_id when successful
        """
        try:
            formatted_page_id = format_uuid(page_id) or page_id

            # Archive the page (Notion's way of deleting)
            data = {"archived": True}

            result = await self._client.patch(f"pages/{formatted_page_id}", data)
            if not result:
                self.logger.error("Error deleting page %s", formatted_page_id)
                return {
                    "success": False,
                    "message": f"Failed to delete page {formatted_page_id}",
                }

            self.logger.info(
                "Page %s successfully deleted (archived)", formatted_page_id
            )
            return {"success": True, "page_id": formatted_page_id}

        except Exception as e:
            self.logger.error("Error in delete_page: %s", str(e))
            return {"success": False, "message": f"Error: {str(e)}"}

    async def get_last_edited_time(self) -> Optional[str]:
        """
        Retrieve the last edited time of the database.

        Returns:
            ISO 8601 timestamp string of the last database edit, or None if request fails
        """
        try:
            response = await self._client.get(f"databases/{self.database_id}")

            if response and "last_edited_time" in response:
                return response["last_edited_time"]

            self.logger.warning(
                "Could not retrieve last_edited_time for database %s", self.database_id
            )
            return None

        except Exception as e:
            self.logger.error("Error fetching last_edited_time: %s", str(e))
            return None

    async def close(self) -> None:
        """Close the client connection."""
        await self._client.close()
