from typing import Any, Dict, List, Optional

from notionary.core.converters.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)
from notionary.core.converters.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.core.converters.registry.block_element_registry import BlockElementRegistry
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class PageContentManager(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient, block_registry: Optional[BlockElementRegistry] = None):
        self.page_id = page_id
        self._client = client
        self._markdown_to_notion_converter = MarkdownToNotionConverter(block_registry=block_registry)
        self._notion_to_markdown_converter = NotionToMarkdownConverter(block_registry=block_registry)

    async def append_markdown(self, markdown_text: str) -> str:
        blocks = self._markdown_to_notion_converter.convert(markdown_text)
        result = await self._client.patch(
            f"blocks/{self.page_id}/children", {"children": blocks}
        )
        return (
            "Successfully added text to the page." if result else "Failed to add text."
        )

    async def clear(self) -> str:
        blocks = await self._client.get(f"blocks/{self.page_id}/children")
        if not blocks:
            return "No content to delete."

        results = blocks.get("results", [])
        if not results:
            return "No content to delete."

        deleted = 0
        for b in results:
            if await self._client.delete(f"blocks/{b['id']}"):
                deleted += 1

        return f"Deleted {deleted}/{len(results)} blocks."

    # Methods from PageContentReader
    async def get_blocks(self) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{self.page_id}/children")
        if not result:
            self.logger.error("Error retrieving page content: %s", result.error)
            return []
        return result.data.get("results", [])

    async def get_block_children(self, block_id: str) -> List[Dict[str, Any]]:
        result = await self._client.get(f"blocks/{block_id}/children")
        if not result:
            self.logger.error("Error retrieving block children: %s", result.error)
            return []
        return result.data.get("results", [])

    async def get_page_blocks_with_children(self) -> List[Dict[str, Any]]:
        blocks = await self.get_blocks()
        for block in blocks:
            if block.get("has_children"):
                block_id = block.get("id")
                if block_id:
                    children = await self.get_block_children(block_id)
                    if children:
                        block["children"] = children
        return blocks

    async def get_text(self) -> str:
        blocks = await self.get_page_blocks_with_children()
        return self._notion_to_markdown_converter.convert(blocks)