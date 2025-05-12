from typing import Any, Dict
from textwrap import dedent

from notionary.elements.divider_element import DividerElement
from notionary.elements.registry.block_registry import BlockRegistry
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


class PageContentWriter(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        client: NotionClient,
        block_registry: BlockRegistry,
    ):
        self.page_id = page_id
        self._client = client
        self.block_registry = block_registry
        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )
        self._notion_to_markdown_converter = NotionToMarkdownConverter(
            block_registry=block_registry
        )
        self._chunker = NotionPageContentChunker()

    async def append_markdown(self, markdown_text: str, append_divider=False) -> bool:
        """
        Append markdown text to a Notion page, automatically handling content length limits.
        """
        # Check for leading whitespace in the first three lines and log a warning if found
        first_three_lines = markdown_text.split('\n')[:3]
        if any(line.startswith(' ') or line.startswith('\t') for line in first_three_lines):
            self.logger.warning(
                "Leading whitespace detected in input markdown. Consider using textwrap.dedent or similar logic: "
                "this code is indented the wrong way, which could lead to formatting issues."
            )
        
        markdown_text = "\n".join(line.lstrip() for line in markdown_text.split("\n"))

        if append_divider and not self.block_registry.contains(DividerElement):
            self.logger.warning(
                "DividerElement not registered. Appending divider skipped."
            )
            append_divider = False

        # Append divider in markdown format as it will be converted to a Notion divider block
        if append_divider:
            markdown_text = markdown_text + "\n\n---\n\n"

        try:
            blocks = self._markdown_to_notion_converter.convert(markdown_text)
            fixed_blocks = self._chunker.fix_blocks_content_length(blocks)

            result = await self._client.patch(
                f"blocks/{self.page_id}/children", {"children": fixed_blocks}
            )
            return bool(result)
        except Exception as e:
            self.logger.error("Error appending markdown: %s", str(e))
            return False

    async def clear_page_content(self) -> bool:
        """
        Clear all content of the page.
        """
        try:
            blocks_resp = await self._client.get(f"blocks/{self.page_id}/children")
            results = blocks_resp.get("results", []) if blocks_resp else []

            if not results:
                return True

            success = True
            for block in results:
                block_success = await self._delete_block_with_children(block)
                if not block_success:
                    success = False

            return success
        except Exception as e:
            self.logger.error("Error clearing page content: %s", str(e))
            return False

    async def _delete_block_with_children(self, block: Dict[str, Any]) -> bool:
        """
        Delete a block and all its children.
        """
        try:
            if block.get("has_children", False):
                children_resp = await self._client.get(f"blocks/{block['id']}/children")
                child_results = children_resp.get("results", [])

                for child in child_results:
                    child_success = await self._delete_block_with_children(child)
                    if not child_success:
                        return False

            return await self._client.delete(f"blocks/{block['id']}")
        except Exception as e:
            self.logger.error("Failed to delete block: %s", str(e))
            return False
