from typing import Dict, Any, List, Optional

from notionary.core.converters.registry.block_element_registry import BlockElementRegistry
from notionary.core.converters.registry.block_element_registry_builder import BlockElementRegistryBuilder

class NotionToMarkdownConverter:
    """Converts Notion blocks to Markdown text."""

    def __init__(self, block_registry: Optional[BlockElementRegistry] = None):
        """
        Initialize the MarkdownToNotionConverter.

        Args:
            block_registry: Optional registry of Notion block elements
        """
        self._block_registry = block_registry or BlockElementRegistryBuilder().create_standard_registry()

    def convert(self, blocks: List[Dict[str, Any]]) -> str:
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
            markdown = self._block_registry.notion_to_markdown(block)
            if markdown:
                markdown_parts.append(markdown)

        return "\n\n".join(markdown_parts)
