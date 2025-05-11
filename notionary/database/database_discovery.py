from typing import (
    AsyncGenerator,
    Dict,
    List,
    Optional,
    Any,
    Tuple,
)
from notionary.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class DatabaseDiscovery(LoggingMixin):
    """
    A utility class that discovers Notion databases accessible to your integration.
    Focused on efficiently retrieving essential database information.
    """

    def __init__(self, client: Optional[NotionClient] = None) -> None:
        """
        Initialize the database discovery with a NotionClient.

        Args:
            client: NotionClient instance for API communication
        """
        self._client = client if client else NotionClient()
        self.logger.info("DatabaseDiscovery initialized")

    async def __call__(self, page_size: int = 100) -> List[Tuple[str, str]]:
        """
        Discover databases and print the results in a nicely formatted way.

        This is a convenience method that discovers databases and handles
        the formatting and printing of results.

        Args:
            page_size: The number of databases to fetch per request

        Returns:
            The same list of databases as discover() for further processing
        """
        databases = await self._discover(page_size)

        if not databases:
            print("\n⚠️ No databases found!")
            print("Please ensure your Notion integration has access to databases.")
            print(
                "You need to share the databases with your integration in Notion settings."
            )
            return databases

        print(f"✅ Found {len(databases)} databases:")

        for i, (title, db_id) in enumerate(databases, 1):
            print(f"{i}. {title} (ID: {db_id})")

        return databases

    async def _discover(self, page_size: int = 100) -> List[Tuple[str, str]]:
        """
        Discover all accessible databases and return their titles and IDs.

        Args:
            page_size: The number of databases to fetch per request

        Returns:
            List of tuples containing (database_title, database_id)
        """
        databases = []

        async for database in self._iter_databases(page_size):
            db_id = database.get("id")
            if not db_id:
                continue

            title = self._extract_database_title(database)
            databases.append((title, db_id))

        return databases

    async def _iter_databases(
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
                return

            for database in result["results"]:
                yield database

            if not result.get("has_more") or not result.get("next_cursor"):
                return

            start_cursor = result["next_cursor"]

    def _extract_database_title(self, database: Dict[str, Any]) -> str:
        """
        Extract the database title from a Notion API response.

        Args:
            database: The database object from the Notion API

        Returns:
            The extracted title or "Untitled" if no title is found
        """
        if "title" not in database:
            return "Untitled"

        title_parts = []
        for text_obj in database["title"]:
            if "plain_text" in text_obj:
                title_parts.append(text_obj["plain_text"])

        if not title_parts:
            return "Untitled"

        return "".join(title_parts)
