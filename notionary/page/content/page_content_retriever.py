from typing import Any, Dict, List, Optional

from notionary.database.client import NotionDatabaseClient
from notionary.elements.registry.block_registry import BlockRegistry

from notionary.page.notion_block_client import NotionBlockClient
from notionary.page.notion_page_client import NotionPageClient
from notionary.page.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.util import LoggingMixin


class PageContentRetriever(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        block_registry: BlockRegistry,
    ):
        self.page_id = page_id
        self._notion_to_markdown_converter = NotionToMarkdownConverter(
            block_registry=block_registry
        )
        self.client = NotionBlockClient()

    async def get_page_content(self) -> str:
        blocks = await self._get_page_blocks_with_children()
        return self._notion_to_markdown_converter.convert(blocks)

    async def _get_page_blocks_with_children(
        self, parent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        blocks = (
            await self.client.get_page_blocks()
            if parent_id is None
            else await self.client.get_block_children(parent_id)
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
