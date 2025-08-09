from notionary.blocks.block_client import NotionBlockClient
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.block_models import Block
from notionary.util import LoggingMixin


class PageContentRetriever(LoggingMixin):
    """Retrieves Notion page content and converts it to Markdown using hierarchical structure."""

    def __init__(
        self,
        page_id: str,
        block_registry: BlockRegistry,
    ):
        self.page_id = page_id
        self._block_registry = block_registry
        self.client = NotionBlockClient()

    async def get_page_content(self) -> str:
        """
        Retrieve page content and convert it to Markdown.
        Uses the hierarchical structure of blocks for automatic formatting.
        """
        blocks = await self.client.get_blocks_by_page_id_recursively(
            page_id=self.page_id
        )

        return self._convert_blocks_to_markdown(blocks, indent_level=0)

    def _convert_blocks_to_markdown(
        self, blocks: list[Block], indent_level: int = 0
    ) -> str:
        """
        Convert blocks to Markdown using their natural hierarchical structure.

        Args:
            blocks: List of blocks to convert
            indent_level: Current indentation level (0 = no indent)
        """
        if not blocks:
            return ""

        markdown_parts = []

        for block in blocks:
            block_markdown = self._process_single_block(block, indent_level)
            if block_markdown:
                markdown_parts.append(block_markdown)

        separator = "\n\n" if indent_level == 0 else "\n"
        return separator.join(markdown_parts)

    def _process_single_block(self, block: Block, indent_level: int) -> str:
        """Process a single block and return its markdown representation."""
        block_markdown = self._block_registry.notion_to_markdown(block)
        if not block_markdown:
            return ""

        # Apply indentation if needed
        if indent_level > 0:
            block_markdown = self._indent_text(block_markdown, spaces=indent_level * 4)

        # Early return if no children
        if not self._has_children(block):
            return block_markdown

        # Process children recursively
        children_markdown = self._convert_blocks_to_markdown(
            block.children, indent_level=indent_level + 1
        )

        # Early return if no children content
        if not children_markdown:
            return block_markdown

        return f"{block_markdown}\n{children_markdown}"

    def _has_children(self, block: Block) -> bool:
        """Check if block has children that need processing."""
        return (
            block.has_children
            and block.children is not None
            and len(block.children) > 0
        )

    def _indent_text(self, text: str, spaces: int = 4) -> str:
        """Indent each line of text with specified number of spaces."""
        if not text:
            return text

        indent = " " * spaces
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
