import json
from typing import Any, Dict, Optional

from notionary.blocks.registry.block_registry import BlockRegistry

from notionary.blocks import NotionBlockClient
from notionary.blocks.shared.models import Block
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

        # TODO: Fix this quick fix🧯 Quick-Fix: Konvertiere rekursive Block-Objekte in plain dicts
        blocks_as_dicts = [block.model_dump(mode="python", exclude_unset=True) for block in blocks]

        return self._notion_to_markdown_converter.convert(blocks_as_dicts)

    async def _get_page_blocks_with_children(
        self, parent_id: Optional[str] = None
    ) -> list[Block]:
        response = (
            await self.client.get_block_children(block_id=self.page_id)
            if parent_id is None
            else await self.client.get_block_children(parent_id)
        )

        if not response or not response.results:
            return []

        blocks = response.results

        for block in blocks:
            if not block.has_children:
                continue

            block_id = block.id
            if not block_id:
                continue

            children = await self._get_page_blocks_with_children(block_id)
            if children:
                block.children = children

        return blocks