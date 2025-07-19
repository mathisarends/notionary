from typing import Dict, Any, List, Optional
from notionary.base_notion_client import BaseNotionClient
from notionary.models.notion_page_response import NotionPageResponse
from notionary.models.notion_database_response import NotionQueryDatabaseResponse
from notionary.util import singleton


@singleton
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
        parent_database_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> NotionPageResponse:
        """
        Creates a new page in a Notion database or as a child page.
        """
        page_data = {
            "parent": {"database_id": parent_database_id} if parent_database_id else {},
            "properties": properties or {},
        }

        response = await self.post("pages", page_data)
        return NotionPageResponse.model_validate(response)

    async def patch_page(
        self, page_id: str, data: Optional[Dict[str, Any]] = None
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
        self, page_id: str, properties: Dict[str, Any]
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

    async def get_page_blocks(self, page_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all blocks of a Notion page.
        """
        response = await self.get(f"blocks/{page_id}/children")
        return response.get("results", [])

    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all children blocks of a specific block.
        """
        response = await self.get(f"blocks/{block_id}/children")
        return response.get("results", [])
