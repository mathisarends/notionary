from typing import Any, Dict, List, Optional

from notionary.elements.block_element_registry import BlockElementRegistry
from notionary.notion_client import NotionClient

from notionary.page.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)
from notionary.page.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.page.content.notion_page_content_chunker import (
    NotionPageContentChunker,
)
from notionary.util.logging_mixin import LoggingMixin


class PageContentManager(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        client: NotionClient,
        block_registry: Optional[BlockElementRegistry] = None,
    ):
        self.page_id = page_id
        self._client = client
        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )
        self._notion_to_markdown_converter = NotionToMarkdownConverter(
            block_registry=block_registry
        )
        self._chunker = NotionPageContentChunker()

    async def append_markdown(self, markdown_text: str) -> str:
        """
        Append markdown text to a Notion page, automatically handling content length limits.
        """
        try:
            blocks = self._markdown_to_notion_converter.convert(markdown_text)

            # Fix any blocks that exceed Notion's content length limits
            fixed_blocks = self._chunker.fix_blocks_content_length(blocks)

            result = await self._client.patch(
                f"blocks/{self.page_id}/children", {"children": fixed_blocks}
            )
            return (
                "Successfully added text to the page."
                if result
                else "Failed to add text."
            )
        except Exception as e:
            self.logger.error("Error appending markdown: %s", str(e))
            raise

    async def clear(self) -> str:
        blocks = await self._client.get(f"blocks/{self.page_id}/children")
        if not blocks:
            return "No content to delete."

        results = blocks.get("results", [])
        if not results:
            return "No content to delete."

        deleted = 0
        skipped = 0
        for block in results:
            if block.get("type") in ["child_database", "database", "linked_database"]:
                skipped += 1
                continue

            if await self._client.delete(f"blocks/{block['id']}"):
                deleted += 1

        return f"Deleted {deleted}/{len(results)} blocks. Skipped {skipped} database blocks."

    async def get_blocks(self) -> List[Dict[str, Any]]:
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
