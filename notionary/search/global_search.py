from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from notionary.notion_client import NotionClient
from notionary.page.notion_page import NotionPage
from notionary.database.notion_database import NotionDatabase
from notionary.util import LoggingMixin

class SearchObjectType(Enum):
    """Supported search object types."""
    PAGE = "page"
    DATABASE = "database"


class SearchResult:
    """Represents a single search result."""
    
    def __init__(
        self,
        object_type: SearchObjectType,
        id: str,
        title: str,
        url: str,
        parent_type: Optional[str] = None,
        parent_id: Optional[str] = None,
        last_edited_time: Optional[str] = None,
        created_time: Optional[str] = None
    ):
        self.object_type = object_type
        self.id = id
        self.title = title
        self.url = url
        self.parent_type = parent_type
        self.parent_id = parent_id
        self.last_edited_time = last_edited_time
        self.created_time = created_time
    
    def __repr__(self) -> str:
        return f"SearchResult(type={self.object_type.value}, title='{self.title}', id='{self.id}')"


class GlobalSearch(LoggingMixin):
    """
    Global search functionality for Notion workspace.
    Provides comprehensive search across pages and databases.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the global search.

        Args:
            token: Optional Notion API token
        """
        self._client = NotionClient(token=token)

    async def search_all(
        self,
        query: str,
        limit: int = 100,
        object_type: Optional[SearchObjectType] = None,
        sort_by_last_edited: bool = True
    ) -> List[SearchResult]:
        """
        Search across all accessible pages and databases.

        Args:
            query: Search query string
            limit: Maximum number of results (max 100 per API call)
            object_type: Filter by object type (page or database)
            sort_by_last_edited: Sort results by last edited time

        Returns:
            List of SearchResult objects
        """
        try:
            # Build search request
            search_body: Dict[str, Any] = {
                "query": query,
                "page_size": min(limit, 100)
            }

            # Add object type filter if specified
            if object_type:
                search_body["filter"] = {
                    "property": "object",
                    "value": object_type.value
                }

            # Add sorting
            if sort_by_last_edited:
                search_body["sort"] = {
                    "direction": "descending",
                    "timestamp": "last_edited_time"
                }

            # Execute search
            result = await self._client.post("search", search_body)

            if not result or "results" not in result:
                self.logger.warning("Search returned empty results for query: %s", query)
                return []

            # Parse results
            search_results = []
            for item in result["results"]:
                search_result = self._parse_search_result(item)
                if search_result:
                    search_results.append(search_result)

            self.logger.info(
                "Global search for '%s' found %d results", 
                query, len(search_results)
            )
            return search_results

        except Exception as e:
            self.logger.error("Error in global search: %s", str(e))
            return []

    async def search_pages(
        self,
        query: str,
        limit: int = 100,
        in_database_id: Optional[str] = None
    ) -> List[Tuple[NotionPage, str]]:
        """
        Search specifically for pages.

        Args:
            query: Search query string
            limit: Maximum number of results
            in_database_id: Optional database ID to limit search scope

        Returns:
            List of (NotionPage, title) tuples
        """
        search_results = await self.search_all(
            query=query,
            limit=limit,
            object_type=SearchObjectType.PAGE
        )

        pages = []
        for result in search_results:
            # Filter by database if specified
            if in_database_id and result.parent_id != in_database_id:
                continue

            page = NotionPage.from_page_id(result.id, token=self._client.token)
            pages.append((page, result.title))

        return pages

    async def find_database_by_title(
        self,
        title: str,
        exact_match: bool = False
    ) -> Optional[NotionDatabase]:
        """
        Find a database by its title.

        Args:
            title: Database title to search for
            exact_match: If True, requires exact title match

        Returns:
            NotionDatabase if found, None otherwise
        """
        search_results = await self.search_databases(query=title, limit=20)

        for database, db_title in search_results:
            if exact_match:
                if db_title.strip() == title.strip():
                    return database
            else:
                if title.lower() in db_title.lower():
                    return database

        return None

    async def search_recent(
        self,
        limit: int = 20,
        object_type: Optional[SearchObjectType] = None
    ) -> List[SearchResult]:
        """
        Get recently edited pages/databases.

        Args:
            limit: Maximum number of results
            object_type: Filter by object type

        Returns:
            List of SearchResult objects sorted by last edited time
        """
        return await self.search_all(
            query="",
            limit=limit,
            object_type=object_type,
            sort_by_last_edited=True
        )

    def _parse_search_result(self, item: Dict[str, Any]) -> Optional[SearchResult]:
        """Parse a single search result item from the API response."""
        try:
            object_type_str = item.get("object", "")
            if object_type_str == "page":
                object_type = SearchObjectType.PAGE
            elif object_type_str == "database":
                object_type = SearchObjectType.DATABASE
            else:
                return None

            # Extract basic info
            id = item.get("id", "")
            url = item.get("url", "")
            created_time = item.get("created_time")
            last_edited_time = item.get("last_edited_time")

            # Extract parent info
            parent = item.get("parent", {})
            parent_type = parent.get("type")
            parent_id = parent.get("database_id") or parent.get("page_id")

            # Extract title based on object type
            title = ""
            if object_type == SearchObjectType.PAGE:
                title = self._extract_page_title(item)
            elif object_type == SearchObjectType.DATABASE:
                title = self._extract_database_title(item)

            return SearchResult(
                object_type=object_type,
                id=id,
                title=title,
                url=url,
                parent_type=parent_type,
                parent_id=parent_id,
                created_time=created_time,
                last_edited_time=last_edited_time
            )

        except Exception as e:
            self.logger.error("Error parsing search result: %s", str(e))
            return None

    def _extract_page_title(self, page_data: Dict[str, Any]) -> str:
        """Extract title from page data."""
        try:
            properties = page_data.get("properties", {})
            for prop_value in properties.values():
                if prop_value.get("type") == "title":
                    title_array = prop_value.get("title", [])
                    if title_array:
                        return "".join(
                            text_obj.get("plain_text", "")
                            for text_obj in title_array
                        )
            return "Untitled"
        except Exception:
            return "Untitled"

    def _extract_database_title(self, database_data: Dict[str, Any]) -> str:
        """Extract title from database data."""
        try:
            title_array = database_data.get("title", [])
            if title_array:
                return "".join(
                    text_obj.get("plain_text", "")
                    for text_obj in title_array
                )
            return "Untitled Database"
        except Exception:
            return "Untitled Database"

    async def close(self) -> None:
        """Close the client connection."""
        await self._client.close()