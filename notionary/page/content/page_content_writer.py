from typing import Any, Dict

from notionary.blocks import DividerElement, BlockRegistry

from notionary.page.client import NotionPageClient
from notionary.page.formatting.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)
from notionary.page.notion_to_markdown_converter import (
    NotionToMarkdownConverter,
)
from notionary.page.content.notion_page_content_chunker import (
    NotionPageContentChunker,
)
from notionary.util import LoggingMixin


class PageContentWriter(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        client: NotionPageClient,
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
        if append_divider and not self.block_registry.contains(DividerElement):
            self.logger.warning(
                "DividerElement not registered. Appending divider skipped."
            )
            append_divider = False

        # Append divider in markdown format as it will be converted to a Notion divider block
        if append_divider:
            markdown_text = markdown_text + "---\n"

        markdown_text = self._process_markdown_whitespace(markdown_text)

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

    def _process_markdown_whitespace(self, markdown_text: str) -> str:
        """
        Process markdown text to preserve code structure while removing unnecessary indentation.
        Strips all leading whitespace from regular lines, but preserves relative indentation
        within code blocks.

        Args:
            markdown_text: Original markdown text with potential leading whitespace

        Returns:
            Processed markdown text with corrected whitespace
        """
        lines = markdown_text.split("\n")
        if not lines:
            return ""

        processed_lines = []
        in_code_block = False
        current_code_block = []

        for line in lines:
            # Handle code block markers
            if self._is_code_block_marker(line):
                if not in_code_block:
                    # Starting a new code block
                    in_code_block = True
                    processed_lines.append(self._process_code_block_start(line))
                    current_code_block = []
                    continue

                # Ending a code block
                processed_lines.extend(
                    self._process_code_block_content(current_code_block)
                )
                processed_lines.append("```")
                in_code_block = False
                continue

            # Handle code block content
            if in_code_block:
                current_code_block.append(line)
                continue

            # Handle regular text
            processed_lines.append(line.lstrip())

        # Handle unclosed code block
        if in_code_block and current_code_block:
            processed_lines.extend(self._process_code_block_content(current_code_block))
            processed_lines.append("```")

        return "\n".join(processed_lines)

    def _is_code_block_marker(self, line: str) -> bool:
        """Check if a line is a code block marker."""
        return line.lstrip().startswith("```")

    def _process_code_block_start(self, line: str) -> str:
        """Extract and normalize the code block opening marker."""
        language = line.lstrip().replace("```", "", 1).strip()
        return "```" + language

    def _process_code_block_content(self, code_lines: list) -> list:
        """
        Normalize code block indentation by removing the minimum common indentation.

        Args:
            code_lines: List of code block content lines

        Returns:
            List of processed code lines with normalized indentation
        """
        if not code_lines:
            return []

        # Find non-empty lines to determine minimum indentation
        non_empty_code_lines = [line for line in code_lines if line.strip()]
        if not non_empty_code_lines:
            return [""] * len(code_lines)  # All empty lines stay empty

        # Calculate minimum indentation
        min_indent = min(
            len(line) - len(line.lstrip()) for line in non_empty_code_lines
        )
        if min_indent == 0:
            return code_lines  # No common indentation to remove

        # Process each line
        processed_code_lines = []
        for line in code_lines:
            if not line.strip():
                processed_code_lines.append("")  # Keep empty lines empty
                continue

            # Remove exactly the minimum indentation
            processed_code_lines.append(line[min_indent:])

        return processed_code_lines
