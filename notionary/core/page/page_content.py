from typing import Any, Dict, List

from notionary.core.converters.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)
from notionary.core.converters.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.core.notion_client import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class PageContentEditor(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client

    async def append_markdown(self, markdown_text: str) -> str:
        blocks = MarkdownToNotionConverter().convert(markdown_text)
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

        deleted = 0
        for b in blocks.data.get("results", []):
            if await self._client.delete(f"blocks/{b['id']}"):
                deleted += 1

        return f"Deleted {deleted}/{len(blocks.data['results'])} blocks."

    async def replace_content(self, markdown_text: str) -> str:
        clear_result = await self.clear()
        append_result = await self.append_markdown(markdown_text)
        return f"{clear_result}\n{append_result}"


class PageContentReader(LoggingMixin):
    def __init__(self, page_id: str, client: NotionClient):
        self.page_id = page_id
        self._client = client

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
        return NotionToMarkdownConverter.convert(blocks)
