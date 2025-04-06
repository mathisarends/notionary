from typing import Dict, Any, List

from notionary.core.converters.registry.block_element_registry import BlockElementRegistry


class NotionToMarkdownConverter:
    """Converts Notion blocks to Markdown text."""

    @staticmethod
    def convert(blocks: List[Dict[str, Any]]) -> str:
        """
        Convert Notion blocks to Markdown text.

        Args:
            blocks: List of Notion blocks

        Returns:
            Markdown text
        """
        if not blocks:
            return ""

        markdown_parts = []

        for block in blocks:
            markdown = BlockElementRegistry.notion_to_markdown(block)
            if markdown:
                markdown_parts.append(markdown)

        return "\n\n".join(markdown_parts)
