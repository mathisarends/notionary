from typing import (
    AsyncGenerator,
    Dict,
    Optional,
    Any,
)
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin

class NotionDatabaseAccessor(LoggingMixin):
    """
    A utility class that provides methods to access Notion databases.
    Focused on efficient, paginated access to databases without unnecessary complexity.
    """

    def __init__(self, client: Optional[NotionClient] = None) -> None:
        """
        Initialize the accessor with a NotionClient.

        Args:
            client: NotionClient instance for API communication
        """
        self._client = client if client else NotionClient()
        self.logger.info("NotionDatabaseAccessor initialized")

    async def iter_databases(
        self, page_size: int = 100
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Asynchronous generator that yields Notion databases one by one.

        Uses the Notion API to provide paginated access to all databases
        without loading all of them into memory at once.

        Args:
            page_size: The number of databases to fetch per request

        Yields:
            Individual database objects from the Notion API
        """
        start_cursor: Optional[str] = None

        while True:
            body: Dict[str, Any] = {
                "filter": {"value": "database", "property": "object"},
                "page_size": page_size,
            }

            if start_cursor:
                body["start_cursor"] = start_cursor

            result = await self._client.post("search", data=body)

            if not result or "results" not in result:
                self.logger.error("Error fetching databases")
                break

            for database in result["results"]:
                yield database

            if "has_more" in result and result["has_more"] and "next_cursor" in result:
                start_cursor = result["next_cursor"]
            else:
                break

    async def get_database(self, database_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the details for a specific database.

        Args:
            database_id: The ID of the database

        Returns:
            Database details or None if not found
        """
        db_details = await self._client.get(f"databases/{database_id}")
        if not db_details:
            self.logger.error("Failed to retrieve database %s", database_id)
            return None

        return db_details

    def extract_database_title(self, database: Dict[str, Any]) -> str:
        """
        Extract the database title from a Notion API response.

        Args:
            database: The database object from the Notion API

        Returns:
            The extracted title or "Untitled" if no title is found
        """
        title = "Untitled"

        if "title" in database:
            title_parts = []
            for text_obj in database["title"]:
                if "plain_text" in text_obj:
                    title_parts.append(text_obj["plain_text"])

            if title_parts:
                title = "".join(title_parts)

        return title