from typing import Any, Dict, Optional

from notionary.base_notion_client import BaseNotionClient
from notionary.database.models import (
    NotionDatabaseResponse,
    NotionDatabaseSearchResponse,
    NotionPageResponse,
    NotionQueryDatabaseResponse,
)


class NotionDatabaseClient(BaseNotionClient):
    """
    Specialized Notion client for database operations.
    Inherits connection management and HTTP methods from BaseNotionClient.
    """

    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        super().__init__(token, timeout)

    async def get_database(self, database_id: str) -> NotionDatabaseResponse:
        """
        Gets metadata for a Notion database by its ID.
        """
        response = await self.get(f"databases/{database_id}")
        return NotionDatabaseResponse.model_validate(response)

    async def patch_database(
        self, database_id: str, data: Dict[str, Any]
    ) -> NotionDatabaseResponse:
        """
        Updates a Notion database with the provided data.
        """
        response = await self.patch(f"databases/{database_id}", data=data)
        return NotionDatabaseResponse.model_validate(response)

    async def query_database(
        self, database_id: str, query_data: Dict[str, Any] = None
    ) -> NotionQueryDatabaseResponse:
        """
        Queries a Notion database with the provided filter and sorts.
        """
        response = await self.post(f"databases/{database_id}/query", data=query_data)
        return NotionQueryDatabaseResponse.model_validate(response)

    async def query_database_by_title(
        self, database_id: str, page_title: str
    ) -> NotionQueryDatabaseResponse:
        """
        Queries a Notion database by title.
        """
        query_data = {
            "filter": {"property": "title", "title": {"contains": page_title}}
        }

        return await self.query_database(database_id=database_id, query_data=query_data)

    async def search_databases(
        self, query: str = "", sort_ascending: bool = True, limit: int = 100
    ) -> NotionDatabaseSearchResponse:
        """
        Searches for databases in Notion using the search endpoint.

        Args:
            query: Search query string
            sort_ascending: Whether to sort in ascending order
            limit: Maximum number of results to return
        """
        search_data = {
            "query": query,
            "filter": {"value": "database", "property": "object"},
            "sort": {
                "direction": "ascending" if sort_ascending else "descending",
                "timestamp": "last_edited_time",
            },
            "page_size": limit,
        }

        response = await self.post("search", search_data)
        return NotionDatabaseSearchResponse.model_validate(response)

    async def create_page(self, parent_database_id: str) -> NotionPageResponse:
        """
        Creates a new blank page in the given database with minimal properties.
        """
        page_data = {
            "parent": {"database_id": parent_database_id},
            "properties": {},
        }
        response = await self.post("pages", page_data)
        return NotionPageResponse.model_validate(response)

    async def update_database_title(
        self, database_id: str, title: str
    ) -> NotionDatabaseResponse:
        """
        Updates the title of a database.
        """
        data = {"title": [{"text": {"content": title}}]}
        return await self.patch_database(database_id, data)

    async def update_database_emoji(
        self, database_id: str, emoji: str
    ) -> NotionDatabaseResponse:
        """
        Updates the emoji/icon of a database.
        """
        data = {"icon": {"type": "emoji", "emoji": emoji}}
        return await self.patch_database(database_id, data)

    async def update_database_cover_image(
        self, database_id: str, image_url: str
    ) -> NotionDatabaseResponse:
        """
        Updates the cover image of a database.
        """
        data = {"cover": {"type": "external", "external": {"url": image_url}}}
        return await self.patch_database(database_id, data)

    async def update_database_external_icon(
        self, database_id: str, icon_url: str
    ) -> NotionDatabaseResponse:
        """
        Updates the database icon with an external image URL.
        """
        data = {"icon": {"type": "external", "external": {"url": icon_url}}}
        return await self.patch_database(database_id, data)
