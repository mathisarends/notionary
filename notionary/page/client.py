from typing import Any, Optional

from notionary.base_notion_client import BaseNotionClient
from notionary.database.models import NotionQueryDatabaseResponse
from notionary.page.models import NotionPageResponse


class NotionPageClient(BaseNotionClient):
    """
    Client for Notion page-specific operations.
    Inherits base HTTP functionality from BaseNotionClient.
    """

    async def get_page(self, page_id: str) -> NotionPageResponse:
        """
        Gets metadata for a Notion page by its ID.
        """
        response = await self.get(f"pages/{page_id}")
        return NotionPageResponse.model_validate(response)

    async def create_page(
        self,
        *,
        parent_database_id: Optional[str] = None,
        parent_page_id: Optional[str] = None,
        title: str,
    ) -> NotionPageResponse:
        """
        Creates a new page either in a database or as a child of another page.
        Exactly one of parent_database_id or parent_page_id must be provided.
        Only 'title' is supported here (no icon/cover/children).
        """
        # Exakt einen Parent zulassen
        if (parent_database_id is None) == (parent_page_id is None):
            raise ValueError("Specify exactly one parent: database OR page")

        # Parent bauen
        parent = (
            {"database_id": parent_database_id}
            if parent_database_id
            else {"page_id": parent_page_id}
        )

        properties: dict[str, Any] = {
            "title": {
                "title": [
                    {"type": "text", "text": {"content": title}}
                ]
            }
        }

        payload = {"parent": parent, "properties": properties}
        response = await self.post("pages", payload)
        return NotionPageResponse.model_validate(response)


    async def patch_page(
        self, page_id: str, data: Optional[dict[str, Any]] = None
    ) -> NotionPageResponse:
        """
        Updates a Notion page with the provided data.
        """
        response = await self.patch(f"pages/{page_id}", data=data)
        return NotionPageResponse.model_validate(response)

    async def delete_page(self, page_id: str) -> bool:
        """
        Deletes (archives) a Notion page.
        """
        # Notion doesn't have a direct delete endpoint, we archive by setting archived=True
        data = {"archived": True}
        response = await self.patch(f"pages/{page_id}", data=data)
        return response is not None

    async def search_pages(
        self, query: str, sort_ascending: bool = True, limit: int = 100
    ) -> NotionQueryDatabaseResponse:
        """
        Searches for pages in Notion using the search endpoint.
        """
        from notionary.page.search_filter_builder import SearchFilterBuilder

        search_filter = (
            SearchFilterBuilder()
            .with_query(query)
            .with_pages_only()
            .with_sort_direction("ascending" if sort_ascending else "descending")
            .with_page_size(limit)
        )

        result = await self.post("search", search_filter.build())
        return NotionQueryDatabaseResponse.model_validate(result)

    async def update_page_properties(
        self, page_id: str, properties: dict[str, Any]
    ) -> NotionPageResponse:
        """
        Updates only the properties of a Notion page.
        """
        data = {"properties": properties}
        return await self.patch_page(page_id, data)

    async def archive_page(self, page_id: str) -> NotionPageResponse:
        """
        Archives a Notion page (soft delete).
        """
        data = {"archived": True}
        return await self.patch_page(page_id, data)

    async def unarchive_page(self, page_id: str) -> NotionPageResponse:
        """
        Unarchives a previously archived Notion page.
        """
        data = {"archived": False}
        return await self.patch_page(page_id, data)

    async def get_page_blocks(self, page_id: str) -> list[dict[str, Any]]:
        """
        Retrieves all blocks of a Notion page.
        """
        response = await self.get(f"blocks/{page_id}/children")
        return response.get("results", [])

    async def get_block_children(self, block_id: str) -> list[dict[str, Any]]:
        """
        Retrieves all children blocks of a specific block.
        """
        response = await self.get(f"blocks/{block_id}/children")
        return response.get("results", [])
