import json
from typing import Any, Dict, List, Optional

from notionary.elements.divider_element import DividerElement
from notionary.elements.registry.block_element_registry import BlockElementRegistry
from notionary.notion_client import NotionClient

from notionary.page.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.util.logging_mixin import LoggingMixin


class PageContentRetriever(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        client: NotionClient,
        block_registry: BlockElementRegistry,
    ):
        self.page_id = page_id
        self._client = client
        self._notion_to_markdown_converter = NotionToMarkdownConverter(
            block_registry=block_registry
        )
        
    async def get_page_content(self) -> str:
        blocks = await self._get_page_blocks_with_children()
        return self._notion_to_markdown_converter.convert(blocks)


    async def _get_blocks(self) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{self.page_id}/children")
        if not result:
            self.logger.error("Error retrieving page content: %s", result.error)
            return []
        return result.get("results", [])


    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{block_id}/children")
        if not result:
            self.logger.error("Error retrieving block children: %s", result.error)
            return []
        return result.get("results", [])


    async def _get_page_blocks_with_children(
        self, parent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        blocks = (
            await self._get_blocks()
            if parent_id is None
            else await self.get_block_children(parent_id)
        )

        if not blocks:
            return []

        for block in blocks:
            if not block.get("has_children"):
                continue

            block_id = block.get("id")
            if not block_id:
                continue

            children = await self._get_page_blocks_with_children(block_id)
            if children:
                block["children"] = children

        return blocks
