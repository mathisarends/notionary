from typing import Dict, Any, List
from notionary.base_notion_client import BaseNotionClient
from notionary.util import singleton


# TODO: Tyoe the block api (fix registry as well)
@singleton
class NotionBlockClient(BaseNotionClient):
    """
    Client for Notion page-specific operations.
    Inherits base HTTP functionality from BaseNotionClient.
    """

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
