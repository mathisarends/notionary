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
            # Convert the block itself using the registry
            block_markdown = self._block_registry.notion_to_markdown(block)

            if not block_markdown:
                continue

            # Apply indentation if needed
            if indent_level > 0:
                block_markdown = self._indent_text(
                    block_markdown, spaces=indent_level * 4
                )

            # If block has children, process them recursively with increased indentation
            if self._has_children(block):
                children_markdown = self._convert_blocks_to_markdown(
                    block.children, indent_level=indent_level + 1
                )

                if children_markdown:
                    # Combine parent block with indented children
                    block_markdown = f"{block_markdown}\n{children_markdown}"

            markdown_parts.append(block_markdown)

        # Join all blocks at this level with appropriate spacing
        separator = "\n\n" if indent_level == 0 else "\n"
        return separator.join(filter(None, markdown_parts))

    def _has_children(self, block: Block) -> bool:
        """
        Check if block has children that need processing.
        """
        return (
            block.has_children
            and block.children is not None
            and len(block.children) > 0
        )

    def _indent_text(self, text: str, spaces: int = 4) -> str:
        """
        Indent each line of text with specified number of spaces.
        """
        if not text:
            return text

        indent = " " * spaces
        lines = text.split("\n")
        return "\n".join(
            [f"{indent}{line}" if line.strip() else line for line in lines]
        )

    # Optional: If you still need toggle extraction for specific use cases
    def _extract_text_content(self, block: Block) -> str:
        """
        Extract plain text content from any block type.
        """
        content = block.get_block_content()
        if not content:
            return ""

        rich_text = content.rich_text if hasattr(content, "rich_text") else None
        if rich_text:
            return "".join([rt.plain_text for rt in rich_text])

        return ""
